from apps.products.utils.redis_access import delete_keys_by_pattern
from .cache_keys import (
    PURCHASE_ORDER_LIST_CACHE_PREFIX,
    PURCHASE_RECEIPT_LIST_CACHE_PREFIX,
    PURCHASE_PAYMENT_LIST_CACHE_PREFIX,
)


def invalidate_purchase_order_cache():
    delete_keys_by_pattern(PURCHASE_ORDER_LIST_CACHE_PREFIX)


def invalidate_purchase_receipt_cache():
    delete_keys_by_pattern(PURCHASE_RECEIPT_LIST_CACHE_PREFIX)


def invalidate_purchase_payment_cache():
    delete_keys_by_pattern(PURCHASE_PAYMENT_LIST_CACHE_PREFIX)
