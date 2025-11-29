# apps/stocks/api/serializers/stock_product_serializer.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime

from apps.core.pagination import Pagination
from apps.stocks.api.serializers.stock_event_serializer import StockEventSerializer
from apps.stocks.models.stock_event_model import StockEvent
from apps.products.models.subproduct_model import Subproduct
from apps.stocks.docs.stock_event_doc import stock_event_history_doc


@extend_schema(
    summary=stock_event_history_doc["summary"],
    description=stock_event_history_doc["description"],
    tags=stock_event_history_doc["tags"],
    operation_id=stock_event_history_doc["operation_id"],
    parameters=stock_event_history_doc["parameters"],
    responses=stock_event_history_doc["responses"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subproduct_stock_event_history(request, product_pk, subproduct_pk):
    """
    Historial de eventos de stock para un subproducto específico (vía product_pk + subproduct_pk).
    Filtros: ?start=ISO&end=ISO&event_type=...
    """
    subproduct = get_object_or_404(
        Subproduct, pk=subproduct_pk, parent_id=product_pk, status=True
    )

    qs = (
        StockEvent.objects
        .filter(subproduct_stock__subproduct=subproduct, status=True)
        .select_related('subproduct_stock', 'created_by')
        .order_by('-created_at')
    )

    start = request.query_params.get('start')
    end = request.query_params.get('end')
    event_type = request.query_params.get('event_type')

    if start:
        dt = parse_datetime(start)
        if dt:
            qs = qs.filter(created_at__gte=dt)
    if end:
        dt = parse_datetime(end)
        if dt:
            qs = qs.filter(created_at__lte=dt)
    if event_type:
        qs = qs.filter(event_type=event_type)

    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    ser = StockEventSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(ser.data)


@extend_schema(
    summary="Historial de stock por subproducto (solo por ID)",
    description="Devuelve el historial de eventos de stock de un subproducto por su ID, sin requerir product_pk.",
    tags=["Stock Events"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subproduct_stock_event_history_by_id(request, subproduct_pk):
    """
    Variante que coincide con tu UI: /stocks/subproducts/<subproduct_pk>/stock/events/
    """
    subproduct = get_object_or_404(Subproduct, pk=subproduct_pk, status=True)

    qs = (
        StockEvent.objects
        .filter(subproduct_stock__subproduct=subproduct, status=True)
        .select_related('subproduct_stock', 'created_by')
        .order_by('-created_at')
    )

    start = request.query_params.get('start')
    end = request.query_params.get('end')
    event_type = request.query_params.get('event_type')

    if start:
        dt = parse_datetime(start)
        if dt:
            qs = qs.filter(created_at__gte=dt)
    if end:
        dt = parse_datetime(end)
        if dt:
            qs = qs.filter(created_at__lte=dt)
    if event_type:
        qs = qs.filter(event_type=event_type)

    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    ser = StockEventSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(ser.data)
