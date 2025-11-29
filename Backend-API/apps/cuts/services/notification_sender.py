# apps/cuts/services/notification_sender.py
import logging
from typing import Optional, Dict

from apps.cuts.tasks import (
    notify_cut_assignment,
    notify_cut_status_change,
)
from apps.notifications.tasks_global import push_cutting_order_status_global

logger = logging.getLogger(__name__)

# Política de reintentos ante errores de conexión con el broker
DEFAULT_RETRY_POLICY: Dict[str, int] = {
    "max_retries": 5,      # cantidad máxima de reintentos
    "interval_start": 5,   # primer espera (segundos)
    "interval_step": 10,   # incremento por intento
    "interval_max": 60,    # tope de espera
}

def send_cut_assignment_notification(
    user_id: int,
    order_id: int,
    *,
    countdown: int = 0,
    retry: bool = True,
    retry_policy: Optional[Dict[str, int]] = None,
    queue: Optional[str] = None,
) -> None:
    """
    Encola la notificación de asignación al operario.
    Usa apply_async con reintentos (broker down, timeouts, etc.).

    :param user_id: ID del usuario asignado
    :param order_id: ID de la orden de corte
    :param countdown: segundos a demorar antes de ejecutar la task (opcional)
    :param retry: habilitar reintentos automáticos de publicación en el broker
    :param retry_policy: política de reintentos (max_retries, interval_start, interval_step, interval_max)
    :param queue: nombre de la cola (si querés rutear a una cola específica)
    """
    try:
        notify_cut_assignment.apply_async(
            kwargs={"user_id": user_id, "order_id": order_id},
            countdown=countdown,
            retry=retry,
            retry_policy=retry_policy or DEFAULT_RETRY_POLICY,
            queue=queue,  # opcional
        )
    except Exception:
        logger.exception(
            "No se pudo encolar notify_cut_assignment (user_id=%s, order_id=%s)",
            user_id, order_id
        )

def send_cut_status_change_notification(
    actor_user_id: int,
    order_id: int,
    new_status: str,
    *,
    countdown: int = 0,
    retry: bool = True,
    retry_policy: Optional[Dict[str, int]] = None,
    queue: Optional[str] = None,
) -> None:
    """
    Encola la notificación de cambio de estado.
    - completed  -> se notifican admins (is_staff=True)
    - cancelled  -> se notifica al asignado
    - otros      -> no se notifica

    :param actor_user_id: ID del usuario que produjo el cambio (puede ser el asignado o staff)
    :param order_id: ID de la orden
    :param new_status: estado objetivo ('completed' | 'cancelled' | etc.)
    :param countdown: demora en segundos antes de ejecutar
    :param retry: habilitar reintentos de publicación en el broker
    :param retry_policy: ver DEFAULT_RETRY_POLICY
    :param queue: cola específica (opcional)
    """
    try:
        notify_cut_status_change.apply_async(
            kwargs={"actor_user_id": actor_user_id, "order_id": order_id, "new_status": new_status},
            countdown=countdown,
            retry=retry,
            retry_policy=retry_policy or DEFAULT_RETRY_POLICY,
            queue=queue,  # opcional
        )
    except Exception:
        logger.exception(
            "No se pudo encolar notify_cut_status_change (actor_user_id=%s, order_id=%s, new_status=%s)",
            actor_user_id, order_id, new_status
        )

def send_cutting_order_status_global(order_id: int, workflow_status: str, extra: Optional[Dict] = None, *, countdown: int = 0, retry: bool = True, retry_policy: Optional[Dict[str, int]] = None, queue: Optional[str] = None) -> None:
    """
    Envia un evento global para refresco de dashboards (WebSocket group 'cutting_orders').
    Llama a la Celery task push_cutting_order_status_global.
    """
    try:
        push_cutting_order_status_global.apply_async(
            kwargs={"order_id": order_id, "workflow_status": workflow_status, "extra": extra or {}},
            countdown=countdown,
            retry=retry,
            retry_policy=retry_policy or DEFAULT_RETRY_POLICY,
            queue=queue,
        )
    except Exception:
        logger.exception(
            "No se pudo encolar push_cutting_order_status_global (order_id=%s, workflow_status=%s)",
            order_id, workflow_status
        )
