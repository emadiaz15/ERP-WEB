from apps.products.utils.cache_keys import generate_cache_key

SUPPLIER_DESCRIPTION_LIST_CACHE_PREFIX = "supplier_description_list"
SUPPLIER_DISCOUNT_LIST_CACHE_PREFIX = "supplier_discount_list"
SUPPLIER_COST_HISTORY_CACHE_PREFIX = "supplier_cost_history"


def supplier_description_list_cache_key(supplier_product_id, **filters):
    return generate_cache_key(
        SUPPLIER_DESCRIPTION_LIST_CACHE_PREFIX,
        supplier_product_id=supplier_product_id,
        **filters,
    )


def supplier_discount_list_cache_key(supplier_product_id, **filters):
    return generate_cache_key(
        SUPPLIER_DISCOUNT_LIST_CACHE_PREFIX,
        supplier_product_id=supplier_product_id,
        **filters,
    )


def supplier_cost_history_cache_key(supplier_product_id, **filters):
    return generate_cache_key(
        SUPPLIER_COST_HISTORY_CACHE_PREFIX,
        supplier_product_id=supplier_product_id,
        **filters,
    )
