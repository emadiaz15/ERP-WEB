from apps.products.utils.cache_keys import generate_cache_key

CUSTOMER_LIST_CACHE_PREFIX = "customer_list"
CUSTOMER_PRODUCT_LIST_CACHE_PREFIX = "customer_product_list"


def customer_list_cache_key(**filters):
    return generate_cache_key(CUSTOMER_LIST_CACHE_PREFIX, **filters)


def customer_product_list_cache_key(**filters):
    return generate_cache_key(CUSTOMER_PRODUCT_LIST_CACHE_PREFIX, **filters)
