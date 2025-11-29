
import json
import hashlib
from django.core.cache import cache

TTL_EVENTS = 120  # seg. Ajusta a lo que usas en productos
INDEX_TTL = 24 * 3600

_ALLOWED_PARAMS = ("start", "end", "event_type", "direction", "page")

def _norm_params(params: dict) -> dict:
    base = {k: (params.get(k) or "").strip() for k in _ALLOWED_PARAMS}
    d = base.get("direction", "").lower()
    base["direction"] = d if d in ("ingreso", "egreso", "all", "") else ""
    base["page"] = base.get("page") or "1"
    return base

def _hash_params(params: dict) -> str:
    data = json.dumps(_norm_params(params), sort_keys=True, ensure_ascii=True)
    return hashlib.md5(data.encode("utf-8")).hexdigest()

def key_sub_events(subproduct_id: int, params: dict) -> str:
    return f"stocks:events:sub:{subproduct_id}:{_hash_params(params)}"

def key_prod_events(product_id: int, params: dict) -> str:
    return f"stocks:events:prod:{product_id}:{_hash_params(params)}"

def _index_key_sub(subproduct_id: int) -> str:
    return f"stocks:events:sub:{subproduct_id}:index"

def _index_key_prod(product_id: int) -> str:
    return f"stocks:events:prod:{product_id}:index"

def _add_to_index(index_key: str, k: str):
    keys = cache.get(index_key) or set()
    keys.add(k)
    cache.set(index_key, keys, INDEX_TTL)

def cache_get(key: str):
    return cache.get(key)

def cache_set(key: str, data, ttl: int = TTL_EVENTS, *, index_key: str | None = None):
    cache.set(key, data, ttl)
    if index_key:
        _add_to_index(index_key, key)

def invalidate_subproduct_events(subproduct_id: int):
    idx = _index_key_sub(subproduct_id)
    keys = cache.get(idx) or set()
    if keys:
        cache.delete_many(list(keys))
    cache.delete(idx)

def invalidate_product_events(product_id: int):
    idx = _index_key_prod(product_id)
    keys = cache.get(idx) or set()
    if keys:
        cache.delete_many(list(keys))
    cache.delete(idx)
