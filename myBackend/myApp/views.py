# myApp/views.py

'''
This file is in charge of defining the logic of HTTP request handlers of the app.
'''
import json
import time
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
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
    global consumer_thread

    if not consumer_thread.is_alive():
        consumer_thread.start()

    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        servers = data.get('serverNames', [])
        print(servers)
        # Update the server data
        for server in servers:
            producer.produce(topic_name, server)
            producer.flush()

        # Trigger some background process to update server_data as checks are completed
        # ...

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
        
        time.sleep(1)  # Avoid busy-waiting; adjust sleep time as needed

consumer_thread = Thread(target=start_kafka_consumer)



# # Create your views here.
# @csrf_exempt
# def process_servers(request):
#     if request.method == 'POST':
#         # Get the raw JSON data from the request body
#         data = json.loads(request.body.decode('utf-8'))

#         # Access the 'servers' list from the JSON data
#         servers = data.get('serverNames', [])

#         '''
#         We are using SSE (Server-Sent Events) instead of Websockets. Both allow real time communication between host and client.

#         Websockets provide bidirectional communication and are great for low latency apps that need isntant data updates. It
#         is also separate from HTTP (Usually implemented over TCP)

#         SSE or Server-Sent Events is a simpler and uni-directional (server to client) technology for pushing data over a
#         single long lived connection. Only the server can initiate communication. It automatically handles reconnection and is
#         great for real time updates (applied to news and sport sites, notifications)
#         '''
#         # Send SSE headers
#         # response = HttpResponse(content_type='text/event-stream')
#         response = StreamingHttpResponse(streaming_content=(self.server_events(servers)), content_type='text/event-stream')
#         response['Cache-Control'] = 'no-cache'
#         return response


#         # Process the servers (print them in the console for this example)
#         # print("Received servers:", servers)

#         # for server in servers:
#         #     result = process_server_health(server)
#             # response.write(f"data: {result}\n\n")
#             # response.flush()

#             # result = process_server_health(server)
#             # Format envent data
#             # print(result)
#             # event_data = {'server': server, 'result': result}
#             # response.write(f"data: {json.dumps(event_data)}\n\n")
#             # print("RESPONSE")
#             # print(response.content)
#             # print(response)

#             # Ensure the data is sent immediately to the client
#             # response.flush()
#         # return JsonResponse({'message': 'Servers processed successfully.'})

#     elif request.method == 'GET':
#         # Handle GET requests for SSE connections
#         # response = HttpResponse(content_type='text/event-stream')
#         # response['Cache-Control'] = 'no-cache'
#         # return response
#         response = StreamingHttpResponse(streaming_content=(self.server_events([])), content_type='text/event-stream')
#         response['Cache-Control'] = 'no-cache'
#         return response


#     else:
#         response_data = {
#             'message': 'Error: Request could not be processed',
#         }

#         return JsonResponse(response_data, status=405)

# def server_events(servers):
#     for server in servers:
#         result = process_server_health(server)
        # event_data = {'server': server, 'result': result}
        # yield f"data: {json.dumps(event_data)}\n\n"


# from django.http import StreamingHttpResponse