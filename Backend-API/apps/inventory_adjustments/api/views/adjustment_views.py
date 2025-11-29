import logging

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.pagination import Pagination
from apps.core.utils import broadcast_crud_event
from apps.inventory_adjustments.api.repositories import StockAdjustmentRepository
from apps.inventory_adjustments.api.serializers import StockAdjustmentSerializer
from apps.inventory_adjustments.docs.adjustments_doc import (
    stock_adjustment_list_doc,
    stock_adjustment_create_doc,
    stock_adjustment_detail_doc,
    stock_adjustment_update_doc,
    stock_adjustment_delete_doc,
)
from apps.inventory_adjustments.utils.cache_invalidation import invalidate_adjustment_cache
from apps.inventory_adjustments.utils.cache_keys import adjustment_list_cache_key

logger = logging.getLogger(__name__)
LIST_TTL = 60 * 5


def _cache_filters(request):
    params = request.query_params.copy()
    filters = {k: params.get(k) for k in params}
    filters.setdefault("page", params.get("page", 1))
    filters.setdefault("page_size", params.get("page_size", Pagination.page_size))
    return filters


@extend_schema(methods=["GET"], **stock_adjustment_list_doc)
@extend_schema(methods=["POST"], **stock_adjustment_create_doc)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def stock_adjustment_list_create_view(request):
    if request.method == "GET":
        filters = _cache_filters(request)
        cache_key = adjustment_list_cache_key(**filters)
        use_cache = not settings.DEBUG
        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)

        qs = StockAdjustmentRepository.list_adjustments(
            search=request.query_params.get("search"),
            status=request.query_params.get("status"),
        )
        paginator = Pagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = StockAdjustmentSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        if use_cache:
            cache.set(cache_key, response.data, LIST_TTL)
        return response

    serializer = StockAdjustmentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=request.user)
    invalidate_adjustment_cache()
    broadcast_crud_event("create", "inventory", "StockAdjustment", serializer.data)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(methods=["GET"], **stock_adjustment_detail_doc)
@extend_schema(methods=["PUT"], **stock_adjustment_update_doc)
@extend_schema(methods=["DELETE"], **stock_adjustment_delete_doc)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def stock_adjustment_detail_view(request, adjustment_id: int):
    adjustment = get_object_or_404(StockAdjustmentRepository.list_adjustments(), pk=adjustment_id)

    if request.method == "GET":
        serializer = StockAdjustmentSerializer(adjustment)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = StockAdjustmentSerializer(adjustment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        invalidate_adjustment_cache()
        broadcast_crud_event("update", "inventory", "StockAdjustment", serializer.data)
        return Response(serializer.data)

    StockAdjustmentRepository.soft_delete(adjustment, user=request.user)
    invalidate_adjustment_cache()
    broadcast_crud_event("delete", "inventory", "StockAdjustment", {"id": adjustment_id})
    return Response(status=status.HTTP_204_NO_CONTENT)
