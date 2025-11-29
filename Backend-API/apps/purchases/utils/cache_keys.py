from apps.products.utils.cache_keys import generate_cache_key

PURCHASE_ORDER_LIST_CACHE_PREFIX = "purchase_order_list"
PURCHASE_RECEIPT_LIST_CACHE_PREFIX = "purchase_receipt_list"
PURCHASE_PAYMENT_LIST_CACHE_PREFIX = "purchase_payment_list"


def purchase_order_list_cache_key(**filters):
    return generate_cache_key(PURCHASE_ORDER_LIST_CACHE_PREFIX, **filters)


def purchase_receipt_list_cache_key(**filters):
    return generate_cache_key(PURCHASE_RECEIPT_LIST_CACHE_PREFIX, **filters)


def purchase_payment_list_cache_key(**filters):
    return generate_cache_key(PURCHASE_PAYMENT_LIST_CACHE_PREFIX, **filters)
