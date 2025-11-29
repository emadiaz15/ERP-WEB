from apps.products.utils.redis_access import delete_keys_by_pattern
from .cache_keys import (
    SUPPLIER_DESCRIPTION_LIST_CACHE_PREFIX,
    SUPPLIER_DISCOUNT_LIST_CACHE_PREFIX,
    SUPPLIER_COST_HISTORY_CACHE_PREFIX,
)


def invalidate_supplier_description_cache():
    delete_keys_by_pattern(SUPPLIER_DESCRIPTION_LIST_CACHE_PREFIX)


def invalidate_supplier_discount_cache():
    delete_keys_by_pattern(SUPPLIER_DISCOUNT_LIST_CACHE_PREFIX)


def invalidate_supplier_cost_history_cache():
    delete_keys_by_pattern(SUPPLIER_COST_HISTORY_CACHE_PREFIX)
