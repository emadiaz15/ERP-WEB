from .cache_keys import NOTIFICATION_LIST_CACHE_PREFIX, NOTIFICATION_DETAIL_CACHE_PREFIX
from .cache_invalidation import invalidate_notification_cache
from rest_framework.response import Response

# ── CACHE CONFIG ─────────────────────────────────────────────
LIST_TTL = 60 * 5   # 5 minutos
DETAIL_TTL = 60 * 2  # 2 minutos

# ── MÉTRICAS EN MEMORIA (thread-safe básico) ─────────────────
from threading import Lock
_metrics_lock = Lock()
_cache_metrics = {
    'notifications_list_hits': 0,
    'notifications_list_miss': 0,
    'notifications_list_sets': 0,
    'notifications_detail_hits': 0,
    'notifications_detail_miss': 0,
    'notifications_detail_sets': 0,
}

def _inc(key):
    with _metrics_lock:
        _cache_metrics[key] += 1

def get_notification_cache_metrics():
    """Devuelve copia de métricas (para endpoint de observabilidad)."""
    with _metrics_lock:
        return dict(_cache_metrics)

def user_cache_key_list(request):
    return f"{NOTIFICATION_LIST_CACHE_PREFIX}:{request.user.id}"

def user_cache_key_detail(request, notif_pk):
    return f"{NOTIFICATION_DETAIL_CACHE_PREFIX}:{request.user.id}:{notif_pk}"

def cache_decorator_list(view_func):
    def wrapper(request, *args, **kwargs):
        key = user_cache_key_list(request)
        from django.core.cache import cache
        cached = cache.get(key)
        if cached is not None:
            _inc('notifications_list_hits')
            return Response(cached)
        _inc('notifications_list_miss')
        resp = view_func(request, *args, **kwargs)
        if resp.status_code == 200:
            cache.set(key, resp.data, LIST_TTL)
            _inc('notifications_list_sets')
        return resp
    return wrapper

def cache_decorator_detail(view_func):
    def wrapper(request, notif_pk, *args, **kwargs):
        key = user_cache_key_detail(request, notif_pk)
        from django.core.cache import cache
        cached = cache.get(key)
        if cached is not None:
            _inc('notifications_detail_hits')
            return Response(cached)
        _inc('notifications_detail_miss')
        resp = view_func(request, notif_pk, *args, **kwargs)
        if resp.status_code == 200:
            cache.set(key, resp.data, DETAIL_TTL)
            _inc('notifications_detail_sets')
        return resp
    return wrapper
