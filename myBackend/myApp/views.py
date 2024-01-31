# myApp/views.py

'''
This file is in charge of defining the logic of HTTP request handlers of the app.
'''
import json
import time
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

@csrf_exempt
def process_servers(request):
    # if not consumer_thread.is_alive():
    #     consumer_thread.start()

    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        servers = data.get('serverNames', [])
        print(servers)

        # Update the server data
        for server in servers:
            producer.produce(topic_name, server)
            producer.flush()

        return JsonResponse({'message': 'Server processing started'}, status=200)

    elif request.method == 'GET':
        # Handle GET requests for SSE connections
        return StreamingHttpResponse(streaming_content=server_events(), content_type='text/event-stream')

    else:
        return JsonResponse({'message': 'Error: Request could not be processed'}, status=405)


def server_events():
    global server_data
    while True:
        # Check for updates in server_data
        # If there are updates, yield them
        for server, status in server_data.items():
            if status != 'pending':  # Assuming status is updated by some background process
                event_data = {'server': server, 'status': status}
                yield f"data: {json.dumps(event_data)}\n\n"
        
        # Avoid busy-waiting;
        time.sleep(1)