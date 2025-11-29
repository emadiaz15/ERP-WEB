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
from apps.purchases.api.repositories import PurchasePaymentRepository
from apps.purchases.api.serializers import PurchasePaymentSerializer
from apps.purchases.docs.purchase_doc import (
    purchase_payment_list_doc,
    purchase_payment_create_doc,
    purchase_payment_detail_doc,
    purchase_payment_delete_doc,
)
from apps.purchases.utils.cache_invalidation import invalidate_purchase_payment_cache
from apps.purchases.utils.cache_keys import purchase_payment_list_cache_key

logger = logging.getLogger(__name__)
PAYMENT_LIST_TTL = 60 * 5


def _cache_filters(request):
    params = request.query_params.copy()
    filters = {k: params.get(k) for k in params}
    filters.setdefault("page", params.get("page", 1))
    filters.setdefault("page_size", params.get("page_size", Pagination.page_size))
    return filters


@extend_schema(methods=["GET"], **purchase_payment_list_doc)
@extend_schema(methods=["POST"], **purchase_payment_create_doc)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def purchase_payment_list_create_view(request):
    if request.method == "GET":
        filters = _cache_filters(request)
        cache_key = purchase_payment_list_cache_key(**filters)
        use_cache = not settings.DEBUG
        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)

        qs = PurchasePaymentRepository.list_payments(
            supplier_id=request.query_params.get("supplier"),
        )
        paginator = Pagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = PurchasePaymentSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        if use_cache:
            cache.set(cache_key, response.data, PAYMENT_LIST_TTL)
        return response

    serializer = PurchasePaymentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=request.user)
    invalidate_purchase_payment_cache()
    broadcast_crud_event("create", "purchases", "PurchasePayment", serializer.data)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(methods=["GET"], **purchase_payment_detail_doc)
@extend_schema(methods=["DELETE"], **purchase_payment_delete_doc)
@api_view(["GET", "DELETE"])
@permission_classes([IsAuthenticated])
def purchase_payment_detail_view(request, payment_id: int):
    payment = get_object_or_404(PurchasePaymentRepository.list_payments(), pk=payment_id)

    if request.method == "GET":
        serializer = PurchasePaymentSerializer(payment)
        return Response(serializer.data)

    PurchasePaymentRepository.soft_delete(payment, user=request.user)
    invalidate_purchase_payment_cache()
    broadcast_crud_event("delete", "purchases", "PurchasePayment", {"id": payment_id})
    return Response(status=status.HTTP_204_NO_CONTENT)
