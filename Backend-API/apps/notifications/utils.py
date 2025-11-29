# apps/notifications/utils.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def notify_user(user_id: int, payload: dict):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {"type": "notify.message", "data": payload}
    )
