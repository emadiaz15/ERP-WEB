from apps.products.utils.cache_keys import generate_cache_key

EXPENSE_TYPE_LIST_CACHE_PREFIX = "expense_type_list"
EXPENSE_LIST_CACHE_PREFIX = "expense_list"
EXPENSE_PAYMENT_LIST_CACHE_PREFIX = "expense_payment_list"


def expense_type_list_cache_key(**filters):
    return generate_cache_key(EXPENSE_TYPE_LIST_CACHE_PREFIX, **filters)


def expense_list_cache_key(**filters):
    return generate_cache_key(EXPENSE_LIST_CACHE_PREFIX, **filters)


def expense_payment_list_cache_key(**filters):
    return generate_cache_key(EXPENSE_PAYMENT_LIST_CACHE_PREFIX, **filters)
