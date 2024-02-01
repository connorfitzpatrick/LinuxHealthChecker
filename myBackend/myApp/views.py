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
from .utils.server_utils import parse_server_health_results, process_server_health
from confluent_kafka import Producer
from .utils.server_utils import start_kafka_consumer
from threading import Thread
from .shared_data import server_data

# Kafka configuration 
kafka_config = {'bootstrap.servers': 'localhost:9092'}
topic_name = 'message_queue'

# Kafka producer instance
producer = Producer(kafka_config)
consumer_thread = Thread(target=start_kafka_consumer, daemon=True)

# Dictionary to store the state of each connection
connection_states = {}

@csrf_exempt
def process_servers(request):
    connection_id = request.GET.get('id', str(uuid4()))

    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        servers = data.get('serverNames', [])
        print(servers)

        # Initialize the state for this connection
        connection_states[connection_id] = {
            'servers': servers,
            'last_updates': {server: 0 for server in servers},
            'all_results_sent': False
        }

        # Update the server data
        for server in servers:
            producer.produce(topic_name, server)
            producer.flush()

        return JsonResponse({'message': 'Server processing started'}, status=200)

    elif request.method == 'GET':
        # Return the SSE response
        return StreamingHttpResponse(streaming_content=server_events(connection_id), content_type='text/event-stream')

    else:
        return JsonResponse({'message': 'Error: Request could not be processed'}, status=405)

def server_events(connection_id):
    global server_data
    print("Starting server events for connection:", connection_id)
    
    while True:
        connection_state = connection_states.get(connection_id)
        if not connection_state:
            print(f"Connection state not found for {connection_id}, exiting server_events")
            break

        all_results_sent = True
        for server in connection_state['servers']:
            last_update = connection_state['last_updates'].get(server)
            server_update = server_data.get(server)

            if server_update and last_update < server_update['last_updated']:
                event_data = {'server': server, 'status': server_update['status']}
                yield f"data: {json.dumps(event_data)}\n\n"
                connection_state['last_updates'][server] = server_update['last_updated']
                all_results_sent = False

        if all_results_sent:
            connection_state['all_results_sent'] = True

        if connection_state['all_results_sent']:
            print(f"All results sent for {connection_id}, exiting server_events")
            break

        time.sleep(1)

    if connection_id in connection_states:
        del connection_states[connection_id]

