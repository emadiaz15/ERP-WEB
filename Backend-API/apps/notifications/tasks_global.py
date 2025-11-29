
import logging
from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def push_cutting_order_status_global(self, order_id: int, workflow_status: str, extra: dict = None):
    """
    Envía un evento global a todos los dashboards conectados para refresco en tiempo real.
    """
    logger.info(f"[GLOBAL WS] Ejecutando push_cutting_order_status_global: order_id={order_id}, workflow_status={workflow_status}, extra={extra}")
    channel_layer = get_channel_layer()
    if not channel_layer:
        logger.error("[GLOBAL WS] channel_layer no disponible. No se puede enviar evento global.")
        return
    payload = {
        "type": "notify.message",  # handler en el consumer
        "data": {
            "type": "cutting_order_status",
            "order_id": order_id,
            "workflow_status": workflow_status,
        }
    }
    if extra:
        payload["data"].update(extra)
    try:
        async_to_sync(channel_layer.group_send)("cutting_orders", payload)
        logger.info(f"[GLOBAL WS] Evento enviado a grupo 'cutting_orders': {payload}")
    except Exception as e:
        logger.exception(f"[GLOBAL WS] Error enviando evento global cutting_order_status: {e}")