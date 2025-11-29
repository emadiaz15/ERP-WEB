from apps.products.utils.redis_access import delete_keys_by_pattern
from .cache_keys import (
    ADJUSTMENT_LIST_CACHE_PREFIX,
    INVENTORY_COUNT_LIST_CACHE_PREFIX,
    STOCK_HISTORY_LIST_CACHE_PREFIX,
)


def invalidate_adjustment_cache():
    delete_keys_by_pattern(ADJUSTMENT_LIST_CACHE_PREFIX)


def invalidate_inventory_count_cache():
    delete_keys_by_pattern(INVENTORY_COUNT_LIST_CACHE_PREFIX)


def invalidate_stock_history_cache():
    delete_keys_by_pattern(STOCK_HISTORY_LIST_CACHE_PREFIX)
