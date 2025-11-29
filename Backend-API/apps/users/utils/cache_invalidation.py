from django.core.cache import caches
from .cache_keys import USER_LIST_CACHE_PREFIX, USER_DETAIL_CACHE_PREFIX


def invalidate_user_cache(user_id=None):
    deleted = 0
    if user_id is not None:
        pattern = f"{USER_DETAIL_CACHE_PREFIX}:{user_id}*"
        deleted += caches["default"].delete_pattern(pattern)
    pattern = f"{USER_LIST_CACHE_PREFIX}*"
    deleted += caches["default"].delete_pattern(pattern)
    return deleted
