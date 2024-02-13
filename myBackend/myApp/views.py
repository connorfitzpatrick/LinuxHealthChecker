# myApp/views.py

'''
This file is in charge of defining the logic of HTTP request handlers of the app.
'''
import json
import time
# from .shared_data import server_data, server_data_lock
from uuid import uuid4
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .utils.server_utils import parse_server_health_results, process_server_health
from confluent_kafka import Producer
from .utils.server_utils import start_kafka_consumer, get_server_data
from threading import Thread, Lock, current_thread
from django.core.cache import cache
import logging
from kafka.admin import KafkaAdminClient, NewTopic


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(threadName)s] %(message)s')
logger = logging.getLogger(__name__)

# Kafka configuration for message queue configuration
kafka_config = {'bootstrap.servers': 'localhost:9092'}
topic_name = 'message_queue'

# Initialize Kafka producer to send messages to the topic
producer = Producer(kafka_config)
# Initialize a background thread to consume messages from Kafka
consumer_thread = Thread(target=start_kafka_consumer, daemon=True)

# GLOBAL dictionary for maintaining the state of each connection with a unique ID 
connection_states = {}

# Create a Kafka topic if it doesn't exist
def create_topic_if_not_exists():
    admin_client = KafkaAdminClient(bootstrap_servers='localhost:9092')
    topic_metadata = admin_client.list_topics()
    
    # Check if topic_metadata is a list
    if isinstance(topic_metadata, list):
        # Convert list to set for easy membership check
        topic_names = set(topic_metadata)
    else:
        topic_names = topic_metadata.topics
    
    if topic_name not in topic_names:
        print(f"Topic '{topic_name}' does not exist. Creating it...")
        new_topic = NewTopic(name=topic_name, num_partitions=1, replication_factor=1)
        admin_client.create_topics([new_topic])
        print(f"Topic '{topic_name}' created successfully.")

# Call function to create topic if not exists
create_topic_if_not_exists()

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
            message = json.dumps({'connection_id': connection_id, 'server': server})
            producer.produce(topic_name, message)
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
    start_time = time.time()
    timeout = 120  # Timeout after 120 seconds of no updates

    while True:
        all_servers_updated = True
        for server in connection_states[connection_id]['servers']:
            # Retrieve the last update time for this server from the connection state
            last_update = connection_states[connection_id]['last_updates'].get(server, 0)
            # Retrieve the server update from Redis
            cache_key = connection_id + "-" + server
            server_update = cache.get(cache_key)

            if server_update and last_update < server_update['last_updated']:
                event_data = {'server': server, 'status': server_update['status']}
                yield f"data: {json.dumps(event_data)}\n\n"
                connection_states[connection_id]['last_updates'][server] = server_update['last_updated']
            else:
                all_servers_updated = False

        if all_servers_updated:
            print("All Servers are checked. Closing session")
            # yield "data: {\"message\": \"All servers updated\"}\n\n"
            break

        if time.time() - start_time > timeout:
            yield "data: {\"message\": \"Timeout reached\"}\n\n"
            break

        time.sleep(1.5)  # Sleep to prevent a tight loop, adjust as necessary
    
    
    # Clean up by removing connection state to free resources
    if connection_id in connection_states:
        del connection_states[connection_id]
