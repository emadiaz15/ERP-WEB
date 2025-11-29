# apps/notifications/services/notification_service.py
from typing import Optional, Dict, Any
from django.contrib.auth.models import AbstractBaseUser
from apps.notifications.models.notification_model import Notification
from apps.notifications.tasks import push_notification_task

def create_notification(
    user: AbstractBaseUser,
    notif_type: str,
    title: str,
    message: str = "",
    payload: Optional[Dict[str, Any]] = None,
    actor: Optional[AbstractBaseUser] = None,
) -> Notification:
    """
    Crea, persiste y encola el push de la notificación por WebSocket (Celery).
    """
    n = Notification(
        user=user,
        notif_type=notif_type or "generic",
        title=(title or "")[:255],
        message=message or "",
        payload=payload or {},
        created_by=actor,
    )
    try:
        n.save(user=actor)
    except TypeError:
        n.save()

    # Encola envío asíncrono al WS del usuario
    push_notification_task.delay(n.id)
    return n
