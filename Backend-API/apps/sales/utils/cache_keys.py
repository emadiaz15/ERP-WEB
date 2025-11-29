from apps.products.utils.cache_keys import generate_cache_key

SALES_ORDER_LIST_CACHE_PREFIX = "sales_order_list"
SALES_SHIPMENT_LIST_CACHE_PREFIX = "sales_shipment_list"
SALES_INVOICE_LIST_CACHE_PREFIX = "sales_invoice_list"


def sales_order_list_cache_key(**filters):
    return generate_cache_key(SALES_ORDER_LIST_CACHE_PREFIX, **filters)


def sales_shipment_list_cache_key(**filters):
    return generate_cache_key(SALES_SHIPMENT_LIST_CACHE_PREFIX, **filters)


def sales_invoice_list_cache_key(**filters):
    return generate_cache_key(SALES_INVOICE_LIST_CACHE_PREFIX, **filters)
