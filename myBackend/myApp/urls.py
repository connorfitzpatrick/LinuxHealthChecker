# myApp/urls.py
from django.urls import path
from .views import process_servers  # Import your views

urlpatterns = [
    path('process_servers/', process_servers, name='process_servers'),
    # Add more URL patterns as needed
]
