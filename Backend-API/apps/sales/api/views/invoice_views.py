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
from apps.sales.api.repositories import SalesInvoiceRepository
from apps.sales.api.serializers import SalesInvoiceSerializer
from apps.sales.docs.sales_doc import (
    sales_invoice_list_doc,
    sales_invoice_create_doc,
    sales_invoice_detail_doc,
    sales_invoice_update_doc,
    sales_invoice_delete_doc,
)
from apps.sales.utils.cache_invalidation import invalidate_sales_invoice_cache
from apps.sales.utils.cache_keys import sales_invoice_list_cache_key

logger = logging.getLogger(__name__)
INVOICE_LIST_TTL = 60 * 5


def _cache_filters(request):
    params = request.query_params.copy()
    filters = {k: params.get(k) for k in params}
    filters.setdefault("page", params.get("page", 1))
    filters.setdefault("page_size", params.get("page_size", Pagination.page_size))
    return filters


@extend_schema(methods=["GET"], **sales_invoice_list_doc)
@extend_schema(methods=["POST"], **sales_invoice_create_doc)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def sales_invoice_list_create_view(request):
    if request.method == "GET":
        filters = _cache_filters(request)
        cache_key = sales_invoice_list_cache_key(**filters)
        use_cache = not settings.DEBUG
        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)

        qs = SalesInvoiceRepository.list_invoices(
            search=request.query_params.get("search"),
            status=request.query_params.get("status"),
        )
        paginator = Pagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = SalesInvoiceSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        if use_cache:
            cache.set(cache_key, response.data, INVOICE_LIST_TTL)
        return response

    serializer = SalesInvoiceSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=request.user)
    invalidate_sales_invoice_cache()
    broadcast_crud_event("create", "sales", "SalesInvoice", serializer.data)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(methods=["GET"], **sales_invoice_detail_doc)
@extend_schema(methods=["PUT"], **sales_invoice_update_doc)
@extend_schema(methods=["DELETE"], **sales_invoice_delete_doc)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def sales_invoice_detail_view(request, invoice_id: int):
    invoice = get_object_or_404(SalesInvoiceRepository.list_invoices(), pk=invoice_id)

    if request.method == "GET":
        serializer = SalesInvoiceSerializer(invoice)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = SalesInvoiceSerializer(invoice, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        invalidate_sales_invoice_cache()
        broadcast_crud_event("update", "sales", "SalesInvoice", serializer.data)
        return Response(serializer.data)

    SalesInvoiceRepository.soft_delete(invoice, user=request.user)
    invalidate_sales_invoice_cache()
    broadcast_crud_event("delete", "sales", "SalesInvoice", {"id": invoice_id})
    return Response(status=status.HTTP_204_NO_CONTENT)
