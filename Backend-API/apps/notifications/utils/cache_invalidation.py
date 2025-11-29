# apps/notifications/utils/cache_invalidation.py
from django.core.cache import caches
from .cache_keys import NOTIFICATION_LIST_CACHE_PREFIX, NOTIFICATION_DETAIL_CACHE_PREFIX


def invalidate_notification_cache(user_id=None):
    """Elimina todas las entradas de cache de notificaciones. Si se pasa user_id, solo para ese usuario.

    Usa la API del backend de cache (django `caches`) y su método `delete_pattern`.
    Esto evita depender del cliente redis-py que no expone `delete_pattern`.
    """
    cache = caches["default"]
    deleted = 0
    # Algunos backends (p.ej. locmem) no implementan delete_pattern.
    # Intentamos usarlo; si no existe, hacemos un fallback seguro.
    try:
        if user_id is not None:
            deleted += cache.delete_pattern(f"{NOTIFICATION_LIST_CACHE_PREFIX}:{user_id}*")
            deleted += cache.delete_pattern(f"{NOTIFICATION_DETAIL_CACHE_PREFIX}:{user_id}*")
        else:
            deleted += cache.delete_pattern(f"{NOTIFICATION_LIST_CACHE_PREFIX}*")
            deleted += cache.delete_pattern(f"{NOTIFICATION_DETAIL_CACHE_PREFIX}*")
        return deleted
    except AttributeError:
        # Fallback para backends sin delete_pattern: borrar la key de lista y
        # borrar detalle por ID cuando se provee user_id.
        try:
            if user_id is not None:
                # Borrar la llave de lista conocida
                cache.delete(f"{NOTIFICATION_LIST_CACHE_PREFIX}:{user_id}")
                # Borrar detalles individuales si existen (consultamos la BD)
                from apps.notifications.models.notification_model import Notification
                ids = Notification.objects.filter(user_id=user_id).values_list("id", flat=True)
                for nid in ids:
                    cache.delete(f"{NOTIFICATION_DETAIL_CACHE_PREFIX}:{user_id}:{nid}")
            else:
                # No podemos enumerar todas las keys sin soporte; fallamos silenciosamente
                return 0
        except Exception:
            # No queremos que la invalidación provoque errores en la petición
            return 0
    return deleted
