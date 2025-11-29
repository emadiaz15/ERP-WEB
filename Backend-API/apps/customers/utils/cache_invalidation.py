from apps.products.utils.redis_access import delete_keys_by_pattern
from .cache_keys import (
    CUSTOMER_LIST_CACHE_PREFIX,
    CUSTOMER_PRODUCT_LIST_CACHE_PREFIX,
)


def invalidate_customer_cache():
    delete_keys_by_pattern(CUSTOMER_LIST_CACHE_PREFIX)


def invalidate_customer_product_cache():
    delete_keys_by_pattern(CUSTOMER_PRODUCT_LIST_CACHE_PREFIX)
