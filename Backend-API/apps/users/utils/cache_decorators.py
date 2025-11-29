from django.conf import settings
from django.views.decorators.cache import cache_page
from apps.users.utils.cache_keys import USER_LIST_CACHE_PREFIX, USER_DETAIL_CACHE_PREFIX

LIST_TTL = 60 * 10   # 10 minutos
DETAIL_TTL = 60 * 5  # 5 minutos

list_cache = (
    cache_page(LIST_TTL, key_prefix=USER_LIST_CACHE_PREFIX)
    if not settings.DEBUG else (lambda fn: fn)
)
detail_cache = (
    cache_page(DETAIL_TTL, key_prefix=USER_DETAIL_CACHE_PREFIX)
    if not settings.DEBUG else (lambda fn: fn)
)
