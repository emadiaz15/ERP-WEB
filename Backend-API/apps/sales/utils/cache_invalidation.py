from apps.products.utils.redis_access import delete_keys_by_pattern
from .cache_keys import (
    SALES_ORDER_LIST_CACHE_PREFIX,
    SALES_SHIPMENT_LIST_CACHE_PREFIX,
    SALES_INVOICE_LIST_CACHE_PREFIX,
)


def invalidate_sales_order_cache():
    delete_keys_by_pattern(SALES_ORDER_LIST_CACHE_PREFIX)


def invalidate_sales_shipment_cache():
    delete_keys_by_pattern(SALES_SHIPMENT_LIST_CACHE_PREFIX)


def invalidate_sales_invoice_cache():
    delete_keys_by_pattern(SALES_INVOICE_LIST_CACHE_PREFIX)
