# apps.py
"""
This file contains configurations for the app.
"""

from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myApp'
