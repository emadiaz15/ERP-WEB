
import decimal
import json
import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

def _decimal_to_float(obj):
    if isinstance(obj, dict):
        return {k: _decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_decimal_to_float(v) for v in obj]
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    return obj

def broadcast_crud_event(event_type, app, model, data):
    """
    Envía un evento CRUD a todos los clientes conectados por WebSocket.
    event_type: 'create' | 'update' | 'delete'
    app: nombre de la app (str)
    model: nombre del modelo (str)
    data: dict serializable con la info relevante
    """
    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            logger.debug("broadcast_crud_event: no channel_layer available")
            return
        # Convertir decimal.Decimal a float en el payload
        safe_data = _decimal_to_float(data)
        async_to_sync(channel_layer.group_send)(
            "crud_events",
            {
                "type": "crud_event",
                "data": {
                    "event": event_type,
                    "app": app,
                    "model": model,
                    "payload": safe_data,
                },
            },
        )
        try:
            obj_id = None
            if isinstance(safe_data, dict):
                obj_id = safe_data.get("id")
            logger.info("[WS][crud][send] %s.%s %s id=%s", app, model, event_type, obj_id)
        except Exception:
            logger.debug("broadcast_crud_event: sent %s %s.%s", event_type, app, model)
    except Exception as e:
        # Loggear la excepción para diagnosticar problemas con Channels sin romper la petición
        logger.exception("broadcast_crud_event: error sending event %s.%s: %s", app, model, e)
        return
