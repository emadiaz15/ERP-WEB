from apps.products.utils.redis_access import delete_keys_by_pattern
from .cache_keys import (
    EXPENSE_LIST_CACHE_PREFIX,
    EXPENSE_PAYMENT_LIST_CACHE_PREFIX,
    EXPENSE_TYPE_LIST_CACHE_PREFIX,
)


def invalidate_expense_type_cache():
    delete_keys_by_pattern(EXPENSE_TYPE_LIST_CACHE_PREFIX)


def invalidate_expense_cache():
    delete_keys_by_pattern(EXPENSE_LIST_CACHE_PREFIX)


def invalidate_expense_payment_cache():
    delete_keys_by_pattern(EXPENSE_PAYMENT_LIST_CACHE_PREFIX)
