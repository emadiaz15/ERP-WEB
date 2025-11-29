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
from apps.purchases.api.repositories import PurchaseReceiptRepository
from apps.purchases.api.serializers import PurchaseReceiptSerializer
from apps.purchases.docs.purchase_doc import (
    purchase_receipt_list_doc,
    purchase_receipt_create_doc,
    purchase_receipt_detail_doc,
    purchase_receipt_update_doc,
    purchase_receipt_delete_doc,
)
from apps.purchases.utils.cache_invalidation import invalidate_purchase_receipt_cache
from apps.purchases.utils.cache_keys import purchase_receipt_list_cache_key

logger = logging.getLogger(__name__)
RECEIPT_LIST_TTL = 60 * 5


def _cache_filters(request):
    params = request.query_params.copy()
    filters = {k: params.get(k) for k in params}
    filters.setdefault("page", params.get("page", 1))
    filters.setdefault("page_size", params.get("page_size", Pagination.page_size))
    return filters


@extend_schema(methods=["GET"], **purchase_receipt_list_doc)
@extend_schema(methods=["POST"], **purchase_receipt_create_doc)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def purchase_receipt_list_create_view(request):
    if request.method == "GET":
        filters = _cache_filters(request)
        cache_key = purchase_receipt_list_cache_key(**filters)
        use_cache = not settings.DEBUG
        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)

        qs = PurchaseReceiptRepository.list_receipts(search=request.query_params.get("search"))
        paginator = Pagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = PurchaseReceiptSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        if use_cache:
            cache.set(cache_key, response.data, RECEIPT_LIST_TTL)
        return response

    serializer = PurchaseReceiptSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=request.user)
    invalidate_purchase_receipt_cache()
    broadcast_crud_event("create", "purchases", "PurchaseReceipt", serializer.data)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(methods=["GET"], **purchase_receipt_detail_doc)
@extend_schema(methods=["PUT"], **purchase_receipt_update_doc)
@extend_schema(methods=["DELETE"], **purchase_receipt_delete_doc)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def purchase_receipt_detail_view(request, receipt_id: int):
    receipt = get_object_or_404(PurchaseReceiptRepository.list_receipts(), pk=receipt_id)

    if request.method == "GET":
        serializer = PurchaseReceiptSerializer(receipt)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = PurchaseReceiptSerializer(receipt, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        invalidate_purchase_receipt_cache()
        broadcast_crud_event("update", "purchases", "PurchaseReceipt", serializer.data)
        return Response(serializer.data)

    PurchaseReceiptRepository.soft_delete(receipt, user=request.user)
    invalidate_purchase_receipt_cache()
    broadcast_crud_event("delete", "purchases", "PurchaseReceipt", {"id": receipt_id})
    return Response(status=status.HTTP_204_NO_CONTENT)
