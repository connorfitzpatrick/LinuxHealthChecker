# myApp/views.py

'''
This file is in charge of defining the logic of HTTP request handlers of the app.
'''
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .utils.server_utils import parse_server_health_results, process_servers_health

# Create your views here.
@csrf_exempt
@require_POST
def process_servers(request):
    if request.method == 'POST':
        # Get the raw JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))

        # Access the 'servers' list from the JSON data
        servers = data.get('serverNames', [])

        # Process the servers (print them in the console for this example)
        print("Received servers:", servers)

        results = process_servers_health(servers)

        return HttpResponse("Servers processed successfully.")
    else:
        return HttpResponse("Invalid HTTP method. Use POST.")
