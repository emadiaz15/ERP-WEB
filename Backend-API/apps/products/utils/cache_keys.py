from urllib.parse import urlencode
from typing import Any, List, Tuple

# Namespace y versionado lógico de tus claves
CACHE_NS = "inventory"
CACHE_LOGICAL_VERSION = "v2"

def _normalize_value(v: Any) -> str:
    if isinstance(v, bool):
        return "1" if v else "0"
    if v is None:
        return ""
    return str(v)

def namespaced_prefix(prefix: str) -> str:
    return f"{CACHE_NS}:{CACHE_LOGICAL_VERSION}:{prefix}"

def generate_cache_key(prefix: str, **params: Any) -> str:
    nsprefix = namespaced_prefix(prefix)
    items: List[Tuple[str, str]] = sorted((k, _normalize_value(v)) for k, v in params.items())
    query_string = urlencode(items)
    return f"{nsprefix}:{query_string}" if query_string else nsprefix

def generate_detail_key(prefix: str, *ids: Any) -> str:
    nsprefix = namespaced_prefix(prefix)
    id_parts = ":".join(_normalize_value(i) for i in ids)
    return f"{nsprefix}:{id_parts}" if id_parts else nsprefix

PRODUCT_LIST_CACHE_PREFIX = "product_list"
PRODUCT_DETAIL_CACHE_PREFIX = "product_detail"
SUBPRODUCT_LIST_CACHE_PREFIX = "subproduct_list"
SUBPRODUCT_DETAIL_CACHE_PREFIX = "subproduct_detail"
CATEGORY_LIST_CACHE_PREFIX = "category_list"

def product_list_cache_key(page=1, page_size=10, **filters):
    return generate_cache_key(PRODUCT_LIST_CACHE_PREFIX, page=page, page_size=page_size, **filters)

def product_detail_cache_key(prod_pk):
    return generate_detail_key(PRODUCT_DETAIL_CACHE_PREFIX, prod_pk)

def subproduct_list_cache_key(page=1, page_size=10, **filters):
    return generate_cache_key(SUBPRODUCT_LIST_CACHE_PREFIX, page=page, page_size=page_size, **filters)

def subproduct_detail_cache_key(sub_pk):
    return generate_detail_key(SUBPRODUCT_DETAIL_CACHE_PREFIX, sub_pk)

def category_list_cache_key():
    return generate_cache_key(CATEGORY_LIST_CACHE_PREFIX)

