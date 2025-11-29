from django.conf import settings
from django.views.decorators.cache import cache_page
from apps.cuts.utils.cache_keys import CUTTING_ORDER_LIST_CACHE_PREFIX, CUTTING_ORDER_DETAIL_CACHE_PREFIX

LIST_TTL = 60 * 10   # 10 minutos
DETAIL_TTL = 60 * 5  # 5 minutos

list_cache = (
    cache_page(LIST_TTL, key_prefix=CUTTING_ORDER_LIST_CACHE_PREFIX)
    if not settings.DEBUG else (lambda fn: fn)
)
detail_cache = (
    cache_page(DETAIL_TTL, key_prefix=CUTTING_ORDER_DETAIL_CACHE_PREFIX)
    if not settings.DEBUG else (lambda fn: fn)
)
