# apps/notifications/tasks.py
from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from apps.notifications.models.notification_model import Notification


@shared_task(bind=True, max_retries=3)
def push_notification_task(self, notif_id: int):
    """
    Busca la notificación y la envía al grupo WebSocket del usuario: user_{user_id}
    """
    try:
        notif = Notification.objects.select_related("user").get(pk=notif_id)
    except Notification.DoesNotExist:
        return

    channel_layer = get_channel_layer()
    if not channel_layer:
        # Si CHANNEL_LAYERS no está ok, evitamos reventar la task
        return

    group = f"user_{notif.user_id}"
    payload = {
        "type": "notify.message",  # handler en el consumer: notify_message
        "data": {
            "id": notif.id,
            "notif_type": notif.notif_type,  # ← unificado con REST
            "title": notif.title,
            "message": notif.message,
            "payload": notif.payload,
            "created_at": notif.created_at.isoformat(),
            "is_read": notif.is_read,
        },
    }
    async_to_sync(channel_layer.group_send)(group, payload)
