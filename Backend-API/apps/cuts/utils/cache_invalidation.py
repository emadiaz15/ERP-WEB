# apps/cuts/utils/cache_invalidation.py
from django_redis import get_redis_connection
from .cache_keys import CUTTING_ORDER_LIST_CACHE_PREFIX, CUTTING_ORDER_DETAIL_CACHE_PREFIX


def invalidate_cutting_order_cache():
    """Elimina todas las entradas de cache de listado y detalle de órdenes de corte."""
    conn = get_redis_connection("default")
    deleted = 0
    for prefix in [CUTTING_ORDER_LIST_CACHE_PREFIX, CUTTING_ORDER_DETAIL_CACHE_PREFIX]:
        # Usar scan_iter para encontrar las keys que matchean el patrón y borrarlas
        for key in conn.scan_iter(f"{prefix}*"):
            deleted += conn.delete(key)
    return deleted
