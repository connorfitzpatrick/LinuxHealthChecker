# myApp/views.py

'''
This file is in charge of defining the logic of HTTP request handlers of the app.
'''
import json
import time
from uuid import uuid4
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .utils.server_utils import parse_server_health_results, process_server_health
from confluent_kafka import Producer
from .utils.server_utils import start_kafka_consumer
from threading import Thread
from .shared_data import server_data

# Kafka configuration for message queue configuration
kafka_config = {'bootstrap.servers': 'localhost:9092'}
topic_name = 'message_queue'

# Initialize Kafka producer to send messages to the topic
producer = Producer(kafka_config)
# Initialize a background thread to consume messages from Kafka
consumer_thread = Thread(target=start_kafka_consumer, daemon=True)

# GLOBAL dictionary for maintaining the state of each connection with a unique ID 
connection_states = {}

@csrf_exempt
def process_servers(request):
    '''
    Handles requests to initiate health checks or stream healthcheck results
    '''
    ### POST ###
    if request.method == 'POST':
        # Extract UUID from header
        connection_id = request.META.get('HTTP_X_CONNECTION_ID')

        # Grab server list from request body
        data = json.loads(request.body.decode('utf-8'))
        servers = data.get('serverNames', [])

        # Initialize the state for this connection
        connection_states[connection_id] = {
            # list of servers
            'servers': servers,
            # timestamp of when health check results were obtained for each server
            'last_updates': {server: 0 for server in servers},
            # indicates if all health check results were returned to client
            'all_results_sent': False       
        }

        # Send each server name to the Kafka topic for processing
        for server in servers:
            producer.produce(topic_name, server)
            producer.flush()

        return JsonResponse({'message': 'Server processing started'}, status=200)
    
    ### GET ###
    elif request.method == 'GET':
        # Extract UUID from header
        connection_id = request.GET.get('id')
        # Ensure connection_id was already initialized in the POST request
        if connection_id not in connection_states:
            return JsonResponse({'error': 'Connection not initialized'}, status=400)
        # Stream results to client
        return StreamingHttpResponse(server_events(connection_id, connection_states), content_type='text/event-stream')

    else:
        return JsonResponse({'message': 'Error: Request could not be processed'}, status=405)

def server_events(connection_id, connection_states):
    '''
    Generator function for streaming health check results to client
    '''
    # Access the global server_data updated by Kafka consumer
    global server_data

    # parameters to dictate timeout
    start_time = time.time()
    timeout = 120

    # Assume all servers are updated unless proven otherwise
    while True:
        all_servers_updated = True
        for server in connection_states[connection_id]['servers']:
            # time server's HC results were either initialized or updated
            last_update = connection_states[connection_id]['last_updates'].get(server, 0)
            # time the health check was finished
            server_update = server_data.get(server)
            
            if not server_update:
                # If server_update is None, it means we haven't received an update yet
                all_servers_updated = False
                continue

            # If the health check has been completed and not yet sent to client...
            # Send the results of it to the client
            if last_update < server_update['last_updated']:
                event_data = {'server': server, 'status': server_update['status']}
                yield f"data: {json.dumps(event_data)}\n\n"
                connection_states[connection_id]['last_updates'][server] = server_update['last_updated']
                all_servers_updated = False

        # If all server updated, end stream
        if all_servers_updated:
            print("All servers updated. Ending stream.")
            yield "data: {\"message\": \"All servers updated\"}\n\n"
            break

        # If timeout limit exceeded, end stream
        if time.time() - start_time > timeout:
            print("Timeout reached. Ending stream.")
            yield "data: {\"message\": \"Timeout reached\"}\n\n"
            break

        time.sleep(1)
    
    # Clean up by removing connection state to free resources
    if connection_id in connection_states:
        del connection_states[connection_id]
