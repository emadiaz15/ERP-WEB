from .redis_access import delete_keys_by_pattern
from .cache_keys import (
    PRODUCT_LIST_CACHE_PREFIX,
    PRODUCT_DETAIL_CACHE_PREFIX,
    SUBPRODUCT_LIST_CACHE_PREFIX,
    SUBPRODUCT_DETAIL_CACHE_PREFIX,
    CATEGORY_LIST_CACHE_PREFIX,
)

def invalidate_product_cache():
    delete_keys_by_pattern(PRODUCT_LIST_CACHE_PREFIX)
    delete_keys_by_pattern(PRODUCT_DETAIL_CACHE_PREFIX)

def invalidate_subproduct_cache():
    delete_keys_by_pattern(SUBPRODUCT_LIST_CACHE_PREFIX)
    delete_keys_by_pattern(SUBPRODUCT_DETAIL_CACHE_PREFIX)

def invalidate_category_cache():
    delete_keys_by_pattern(CATEGORY_LIST_CACHE_PREFIX)