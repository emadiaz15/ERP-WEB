# apps/notifications/routing.py
from django.urls import re_path
from .consumers import NotificationsConsumer, PingConsumer

websocket_urlpatterns = [
    re_path(r"^ws/notifications$", NotificationsConsumer.as_asgi()),
    re_path(r"^ws/ping$", PingConsumer.as_asgi()),
]
