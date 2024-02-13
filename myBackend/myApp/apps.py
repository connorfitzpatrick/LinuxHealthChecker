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
        from .views import consumer_thread
        consumer_thread.start()

    """ 
    Graceful shutdown for kafka consumers. I was having delays in my execution
    after restarting the app back and sending a request. This seems to have been
    because the old consumer had not yet failed. Kafka needed more time to detect
    that they no longer had a heartbeat. Once it did, it would rebalance the 
    group which used up even more time.

    This function should gracefully shut down consumers if I hit 'ctrl c'
    """