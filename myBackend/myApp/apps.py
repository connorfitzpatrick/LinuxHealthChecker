# apps.py
"""
This file contains configurations for the app.
"""

from django.apps import AppConfig
from threading import Thread
from .utils.server_utils import start_kafka_consumer

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myApp'

    def ready(self):
        consumer_thread = Thread(target=start_kafka_consumer, daemon=True) 
        consumer_thread.start()
