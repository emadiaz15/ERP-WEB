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
from apps.expenses.api.repositories import ExpensePaymentRepository
from apps.expenses.api.serializers import (
    ExpensePaymentSerializer,
    ExpensePaymentAllocationInputSerializer,
)
from apps.expenses.docs.expense_doc import (
    expense_payment_list_doc,
    expense_payment_create_doc,
    expense_payment_detail_doc,
    expense_payment_delete_doc,
    expense_payment_allocation_doc,
)
from apps.expenses.utils.cache_invalidation import (
    invalidate_expense_cache,
    invalidate_expense_payment_cache,
)
from apps.expenses.utils.cache_keys import expense_payment_list_cache_key
from apps.expenses.services.workflows import register_payment_allocation

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
        logger.warning("[expenses] Fecha inválida recibida en pagos: %s", value)
        return None


def _parse_int(value: str | None):
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        logger.warning("[expenses] Valor entero inválido en pagos: %s", value)
        return None


@extend_schema(methods=["GET"], **expense_payment_list_doc)
@extend_schema(methods=["POST"], **expense_payment_create_doc)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def expense_payment_list_create_view(request):
    if request.method == "GET":
        filters = _cache_filters(request)
        cache_key = expense_payment_list_cache_key(**filters)
        use_cache = not settings.DEBUG
        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)

        qs = ExpensePaymentRepository.list_payments(
            person_legacy_id=_parse_int(request.query_params.get("person")),
            status=request.query_params.get("status"),
            date_from=_parse_date(request.query_params.get("date_from")),
            date_to=_parse_date(request.query_params.get("date_to")),
        )
        paginator = Pagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = ExpensePaymentSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        if use_cache:
            cache.set(cache_key, response.data, LIST_TTL)
        return response

    serializer = ExpensePaymentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=request.user)
    invalidate_expense_payment_cache()
    broadcast_crud_event("create", "expenses", "ExpensePayment", serializer.data)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(methods=["GET"], **expense_payment_detail_doc)
@extend_schema(methods=["DELETE"], **expense_payment_delete_doc)
@api_view(["GET", "DELETE"])
@permission_classes([IsAuthenticated])
def expense_payment_detail_view(request, payment_id: int):
    payment = get_object_or_404(ExpensePaymentRepository.list_payments(), pk=payment_id)

    if request.method == "GET":
        serializer = ExpensePaymentSerializer(payment)
        return Response(serializer.data)

    ExpensePaymentRepository.soft_delete(payment, user=request.user)
    invalidate_expense_payment_cache()
    broadcast_crud_event("delete", "expenses", "ExpensePayment", {"id": payment_id})
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(methods=["POST"], **expense_payment_allocation_doc)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def expense_payment_allocation_view(request, payment_id: int):
    payment = get_object_or_404(ExpensePaymentRepository.list_payments(), pk=payment_id)

    payload_serializer = ExpensePaymentAllocationInputSerializer(data=request.data)
    payload_serializer.is_valid(raise_exception=True)

    data = payload_serializer.validated_data
    try:
        register_payment_allocation(
            payment=payment,
            expense=data["expense"],
            amount=data["amount"],
            is_partial=data.get("is_partial", False),
            user=request.user,
        )
    except ValidationError as exc:
        return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)

    invalidate_expense_payment_cache()
    invalidate_expense_cache()
    broadcast_crud_event("update", "expenses", "ExpensePayment", {"id": payment.id})
    serializer = ExpensePaymentSerializer(payment)
    return Response(serializer.data)
