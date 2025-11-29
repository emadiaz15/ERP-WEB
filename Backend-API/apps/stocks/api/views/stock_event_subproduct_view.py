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

# 👇 cache
from apps.stocks.utils.cache_utils import cache_get, cache_set, key_sub_events, invalidate_subproduct_events


@extend_schema(
    summary="Historial de stock por SUBPRODUCTO (con product_pk)",
    description="Devuelve eventos del subproducto indicado perteneciente al producto dado.",
    tags=["Stock Events"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subproduct_stock_event_history(request, product_pk, subproduct_pk):
    # ⚠️ Permitir ver historial aunque el Subproduct esté inactivo
    subproduct = get_object_or_404(Subproduct, pk=subproduct_pk, parent_id=product_pk)

    params = {
        "start": request.query_params.get('start'),
        "end": request.query_params.get('end'),
        "event_type": request.query_params.get('event_type'),
        "direction": (request.query_params.get('direction') or '').strip().lower(),
        "page": request.query_params.get('page') or "1",
    }
    cache_key = key_sub_events(subproduct.id, params)
    cached = cache_get(cache_key)
    if cached is not None:
        return Response(cached)

    qs = (
        StockEvent.objects
        .filter(subproduct_stock__subproduct=subproduct, status=True)
        .select_related('subproduct_stock', 'created_by')
        .order_by('-created_at')
    )

    start = params["start"]; end = params["end"]; event_type = params["event_type"]; direction = params["direction"]
    if start:
        dt = parse_datetime(start);  qs = qs.filter(created_at__gte=dt) if dt else qs
    if end:
        dt = parse_datetime(end);    qs = qs.filter(created_at__lte=dt) if dt else qs
    if event_type:
        qs = qs.filter(event_type=event_type)
    if direction == 'ingreso':
        qs = qs.filter(quantity_change__gt=0)
    elif direction == 'egreso':
        qs = qs.filter(quantity_change__lt=0)

    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    ser = StockEventSerializer(page, many=True, context={'request': request})
    resp = paginator.get_paginated_response(ser.data)

    cache_set(cache_key, resp.data, index_key=None)
    return resp


@extend_schema(
    summary="Historial de stock por SUBPRODUCTO (solo por ID)",
    description="Devuelve eventos del subproducto por su ID, sin requerir product_pk.",
    tags=["Stock Events"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subproduct_stock_event_history_by_id(request, subproduct_pk):
    # ⚠️ Permitir ver historial aunque el Subproduct esté inactivo
    subproduct = get_object_or_404(Subproduct, pk=subproduct_pk)

    params = {
        "start": request.query_params.get('start'),
        "end": request.query_params.get('end'),
        "event_type": request.query_params.get('event_type'),
        "direction": (request.query_params.get('direction') or '').strip().lower(),
        "page": request.query_params.get('page') or "1",
    }
    cache_key = key_sub_events(subproduct.id, params)
    cached = cache_get(cache_key)
    if cached is not None:
        return Response(cached)

    qs = (
        StockEvent.objects
        .filter(subproduct_stock__subproduct=subproduct, status=True)
        .select_related('subproduct_stock', 'created_by')
        .order_by('-created_at')
    )

    start = params["start"]; end = params["end"]; event_type = params["event_type"]; direction = params["direction"]
    if start:
        dt = parse_datetime(start);  qs = qs.filter(created_at__gte=dt) if dt else qs
    if end:
        dt = parse_datetime(end);    qs = qs.filter(created_at__lte=dt) if dt else qs
    if event_type:
        qs = qs.filter(event_type=event_type)
    if direction == 'ingreso':
        qs = qs.filter(quantity_change__gt=0)
    elif direction == 'egreso':
        qs = qs.filter(quantity_change__lt=0)

    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    ser = StockEventSerializer(page, many=True, context={'request': request})
    resp = paginator.get_paginated_response(ser.data)

    cache_set(cache_key, resp.data, index_key=None)
    return resp
