from django.urls import re_path
from apps.core.consumers.crud_event_consumer import CrudEventConsumer

websocket_urlpatterns = [
    re_path(r"^ws/crud-events$", CrudEventConsumer.as_asgi()),
]
