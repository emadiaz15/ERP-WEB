from apps.products.utils.cache_keys import generate_cache_key

ADJUSTMENT_LIST_CACHE_PREFIX = "stock_adjustment_list"
INVENTORY_COUNT_LIST_CACHE_PREFIX = "inventory_count_list"
STOCK_HISTORY_LIST_CACHE_PREFIX = "stock_history_list"


def adjustment_list_cache_key(**filters):
    return generate_cache_key(ADJUSTMENT_LIST_CACHE_PREFIX, **filters)


def inventory_count_list_cache_key(**filters):
    return generate_cache_key(INVENTORY_COUNT_LIST_CACHE_PREFIX, **filters)


def stock_history_list_cache_key(**filters):
    return generate_cache_key(STOCK_HISTORY_LIST_CACHE_PREFIX, **filters)
