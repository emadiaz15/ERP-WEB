import logging
from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.core.pagination import Pagination
from apps.core.utils import broadcast_crud_event
from apps.expenses.api.repositories import ExpenseRepository
from apps.expenses.api.serializers import ExpenseSerializer
from apps.expenses.docs.expense_doc import (
    expense_list_doc,
    expense_create_doc,
    expense_detail_doc,
    expense_update_doc,
    expense_delete_doc,
    expense_approve_doc,
)
from apps.expenses.utils.cache_invalidation import invalidate_expense_cache
from apps.expenses.utils.cache_keys import expense_list_cache_key
from apps.expenses.services.workflows import approve_expense

logger = logging.getLogger(__name__)
LIST_TTL = 60 * 5


def _cache_filters(request):
    params = request.query_params.copy()
    filters = {k: params.get(k) for k in params}
    filters.setdefault("page", params.get("page", 1))
    filters.setdefault("page_size", params.get("page_size", Pagination.page_size))
    return filters


def _parse_date(value: str | None):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        logger.warning("[expenses] Fecha inválida recibida: %s", value)
        return None


def _parse_int(value: str | None):
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        logger.warning("[expenses] Valor entero inválido recibido: %s", value)
        return None


@extend_schema(methods=["GET"], **expense_list_doc)
@extend_schema(methods=["POST"], **expense_create_doc)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def expense_list_create_view(request):
    if request.method == "GET":
        filters = _cache_filters(request)
        cache_key = expense_list_cache_key(**filters)
        use_cache = not settings.DEBUG
        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)

        qs = ExpenseRepository.list_expenses(
            search=request.query_params.get("search"),
            status=request.query_params.get("status"),
            expense_type=_parse_int(request.query_params.get("type")),
            person_legacy_id=_parse_int(request.query_params.get("person")),
            date_from=_parse_date(request.query_params.get("date_from")),
            date_to=_parse_date(request.query_params.get("date_to")),
        )
        paginator = Pagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = ExpenseSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        if use_cache:
            cache.set(cache_key, response.data, LIST_TTL)
        return response

    serializer = ExpenseSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=request.user)
    invalidate_expense_cache()
    broadcast_crud_event("create", "expenses", "Expense", serializer.data)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(methods=["GET"], **expense_detail_doc)
@extend_schema(methods=["PUT"], **expense_update_doc)
@extend_schema(methods=["DELETE"], **expense_delete_doc)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def expense_detail_view(request, expense_id: int):
    expense = get_object_or_404(ExpenseRepository.list_expenses(), pk=expense_id)

    if request.method == "GET":
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = ExpenseSerializer(expense, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        invalidate_expense_cache()
        broadcast_crud_event("update", "expenses", "Expense", serializer.data)
        return Response(serializer.data)

    ExpenseRepository.soft_delete(expense, user=request.user)
    invalidate_expense_cache()
    broadcast_crud_event("delete", "expenses", "Expense", {"id": expense_id})
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(methods=["POST"], **expense_approve_doc)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def expense_approve_view(request, expense_id: int):
    expense = get_object_or_404(ExpenseRepository.list_expenses(), pk=expense_id)
    try:
        expense = approve_expense(expense, user=request.user, notes=request.data.get("notes"))
    except ValidationError as exc:
        return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)

    invalidate_expense_cache()
    serializer = ExpenseSerializer(expense)
    return Response(serializer.data)
