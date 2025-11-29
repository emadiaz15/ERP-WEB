import logging

from django.conf import settings
from django.core.cache import cache

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.pagination import Pagination
from apps.inventory_adjustments.api.repositories import StockHistoryRepository
from apps.inventory_adjustments.api.serializers import StockHistorySerializer
from apps.inventory_adjustments.docs.adjustments_doc import stock_history_list_doc
from apps.inventory_adjustments.utils.cache_keys import stock_history_list_cache_key

logger = logging.getLogger(__name__)
LIST_TTL = 60 * 5


def _cache_filters(request):
    params = request.query_params.copy()
    filters = {k: params.get(k) for k in params}
    filters.setdefault("page", params.get("page", 1))
    filters.setdefault("page_size", params.get("page_size", Pagination.page_size))
    filters.setdefault("product", request.query_params.get("product"))
    return filters


@extend_schema(methods=["GET"], **stock_history_list_doc)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def stock_history_list_view(request):
    filters = _cache_filters(request)
    cache_key = stock_history_list_cache_key(**filters)
    use_cache = not settings.DEBUG
    if use_cache:
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

    qs = StockHistoryRepository.list_history(product_id=request.query_params.get("product"))
    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = StockHistorySerializer(page, many=True)
    response = paginator.get_paginated_response(serializer.data)
    if use_cache:
        cache.set(cache_key, response.data, LIST_TTL)
    return response
