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
from apps.customers.api.repositories import CustomerRepository
from apps.customers.api.serializers import CustomerSerializer
from apps.customers.docs.customers_doc import (
    customer_list_doc,
    customer_create_doc,
    customer_detail_doc,
    customer_update_doc,
    customer_delete_doc,
)
from apps.customers.utils.cache_invalidation import invalidate_customer_cache
from apps.customers.utils.cache_keys import customer_list_cache_key

logger = logging.getLogger(__name__)
LIST_TTL = 60 * 5


def _cache_filters(request):
    params = request.query_params.copy()
    filters = {k: params.get(k) for k in params}
    filters.setdefault("page", params.get("page", 1))
    filters.setdefault("page_size", params.get("page_size", Pagination.page_size))
    filters.setdefault("zone", request.query_params.get("zone"))
    return filters


@extend_schema(methods=["GET"], **customer_list_doc)
@extend_schema(methods=["POST"], **customer_create_doc)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def customer_list_create_view(request):
    if request.method == "GET":
        filters = _cache_filters(request)
        cache_key = customer_list_cache_key(**filters)
        use_cache = not settings.DEBUG
        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)

        qs = CustomerRepository.list_customers(
            search=request.query_params.get("search"),
            zone=request.query_params.get("zone"),
        )
        paginator = Pagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = CustomerSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        if use_cache:
            cache.set(cache_key, response.data, LIST_TTL)
        return response

    serializer = CustomerSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=request.user)
    invalidate_customer_cache()
    broadcast_crud_event("create", "customers", "Customer", serializer.data)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(methods=["GET"], **customer_detail_doc)
@extend_schema(methods=["PUT"], **customer_update_doc)
@extend_schema(methods=["DELETE"], **customer_delete_doc)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def customer_detail_view(request, customer_id: int):
    customer = get_object_or_404(CustomerRepository.list_customers(), pk=customer_id)

    if request.method == "GET":
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        invalidate_customer_cache()
        broadcast_crud_event("update", "customers", "Customer", serializer.data)
        return Response(serializer.data)

    CustomerRepository.soft_delete(customer, user=request.user)
    invalidate_customer_cache()
    broadcast_crud_event("delete", "customers", "Customer", {"id": customer_id})
    return Response(status=status.HTTP_204_NO_CONTENT)
