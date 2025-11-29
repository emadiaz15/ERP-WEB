import logging

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.core.pagination import Pagination
from apps.core.utils import broadcast_crud_event
from apps.expenses.api.repositories import ExpenseTypeRepository
from apps.expenses.api.serializers import ExpenseTypeSerializer
from apps.expenses.docs.expense_doc import (
    expense_type_list_doc,
    expense_type_create_doc,
    expense_type_detail_doc,
    expense_type_update_doc,
    expense_type_delete_doc,
)
from apps.expenses.utils.cache_invalidation import invalidate_expense_type_cache
from apps.expenses.utils.cache_keys import expense_type_list_cache_key

logger = logging.getLogger(__name__)
LIST_TTL = 60 * 5


def _cache_filters(request):
    params = request.query_params.copy()
    filters = {k: params.get(k) for k in params}
    filters.setdefault("page", params.get("page", 1))
    filters.setdefault("page_size", params.get("page_size", Pagination.page_size))
    return filters


@extend_schema(methods=["GET"], **expense_type_list_doc)
@extend_schema(methods=["POST"], **expense_type_create_doc)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def expense_type_list_create_view(request):
    if request.method == "GET":
        filters = _cache_filters(request)
        cache_key = expense_type_list_cache_key(**filters)
        use_cache = not settings.DEBUG
        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)

        qs = ExpenseTypeRepository.list_types(search=request.query_params.get("search"))
        paginator = Pagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = ExpenseTypeSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        if use_cache:
            cache.set(cache_key, response.data, LIST_TTL)
        return response

    serializer = ExpenseTypeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=request.user)
    invalidate_expense_type_cache()
    broadcast_crud_event("create", "expenses", "ExpenseType", serializer.data)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(methods=["GET"], **expense_type_detail_doc)
@extend_schema(methods=["PUT"], **expense_type_update_doc)
@extend_schema(methods=["DELETE"], **expense_type_delete_doc)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def expense_type_detail_view(request, type_id: int):
    expense_type = get_object_or_404(ExpenseTypeRepository.list_types(), pk=type_id)

    if request.method == "GET":
        serializer = ExpenseTypeSerializer(expense_type)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = ExpenseTypeSerializer(expense_type, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        invalidate_expense_type_cache()
        broadcast_crud_event("update", "expenses", "ExpenseType", serializer.data)
        return Response(serializer.data)

    ExpenseTypeRepository.soft_delete(expense_type, user=request.user)
    invalidate_expense_type_cache()
    broadcast_crud_event("delete", "expenses", "ExpenseType", {"id": type_id})
    return Response(status=status.HTTP_204_NO_CONTENT)
