from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def _delete_pattern(pattern: str) -> int:
    deleted = 0
    try:
        if hasattr(cache, "delete_pattern"):
            deleted = cache.delete_pattern(pattern) or 0
        else:
            # No recomendado en producción; fallback best-effort
            try:
                keys = cache.keys(pattern)
                for k in keys or []:
                    cache.delete(k)
                    deleted += 1
            except Exception:
                deleted = 0
    except Exception as e:
        logger.debug("[Cache] delete_pattern error: %s", e)
        deleted = 0
    return int(deleted)


def delete_keys_by_pattern(prefix: str) -> int:
    """
    Borra claves que contengan el prefijo lógico (p.ej. 'product_list').
    Cubre tanto claves propias como las generadas por cache_page con key_prefix.
    IMPORTANTE: No incluir KEY_PREFIX ni version en el patrón; django-redis
    lo añade automáticamente cuando usa delete_pattern/scan_iter.
    """
    patterns = [
        f"*{prefix}*",
        # Claves típicas de cache_page incluyen el key_prefix lógico dentro del nombre
        # generado (cache_header y cache_page). Borramos ambas por si acaso.
        f"*views.decorators.cache.cache_page*{prefix}*",
        f"*views.decorators.cache.cache_header*{prefix}*",
    ]
    total = 0
    for pat in patterns:
        cnt = _delete_pattern(pat)
        total += cnt
        logger.debug("[Cache] borradas %s claves con patrón '%s'", cnt, pat)
    return total