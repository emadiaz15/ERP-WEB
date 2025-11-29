from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime

from apps.core.pagination import Pagination
from apps.stocks.api.serializers.stock_event_serializer import StockEventSerializer
from apps.stocks.api.repositories.stock_product_repository import StockProductRepository
from apps.products.models.product_model import Product
from apps.stocks.models.stock_event_model import StockEvent

# 👇 cache
from apps.stocks.utils.cache_utils import cache_get, cache_set, key_prod_events, invalidate_product_events


from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime

from apps.core.pagination import Pagination
from apps.stocks.api.serializers.stock_event_serializer import StockEventSerializer
from apps.stocks.api.repositories.stock_product_repository import StockProductRepository
from apps.products.models.product_model import Product
from apps.stocks.models.stock_event_model import StockEvent

# 👇 cache
from apps.stocks.utils.cache_utils import cache_get, cache_set, key_prod_events, _index_key_prod


@extend_schema(
    summary="Historial de stock por PRODUCTO (sin subproductos)",
    description="Devuelve eventos de stock asociados al ProductStock del producto dado. "
                "Si el producto tiene subproductos, devolverá 400.",
    tags=["Stock Events"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_stock_event_history(request, pk):
    # ⚠️ Permitir ver historial aunque el producto esté inactivo
    product = get_object_or_404(Product, pk=pk)

    if getattr(product, "has_subproducts", False):
        return Response(
            {"detail": "Este producto tiene subproductos. Consulta el historial por subproducto."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    stock_record = StockProductRepository.get_stock_for_product(product)
    if not stock_record:
        return Response(
            {"detail": "No se encontró un registro de stock directo para este producto."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # === Cache: key por URL params + página ===
    params = {
        "start": request.query_params.get('start'),
        "end": request.query_params.get('end'),
        "event_type": request.query_params.get('event_type'),
        "direction": (request.query_params.get('direction') or '').strip().lower(),
        "page": request.query_params.get('page') or "1",
    }
    cache_key = key_prod_events(product.id, params)
    cached = cache_get(cache_key)
    if cached is not None:
        return Response(cached)

    qs = (
        StockEvent.objects
        .filter(product_stock=stock_record, status=True)
        .select_related('product_stock', 'subproduct_stock', 'created_by')
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

    cache_set(cache_key, resp.data, index_key=None)  # indexado interno en cache_utils
    return resp



@extend_schema(
    summary="Historial AGREGADO por PRODUCTO (con subproductos)",
    description="Devuelve eventos de stock de TODOS los subproductos del producto dado.",
    tags=["Stock Events"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_subproducts_stock_event_history(request, product_pk):
    # ⚠️ Permitir ver historial aunque el producto esté inactivo
    product = get_object_or_404(Product, pk=product_pk)

    params = {
        "start": request.query_params.get('start'),
        "end": request.query_params.get('end'),
        "event_type": request.query_params.get('event_type'),
        "direction": (request.query_params.get('direction') or '').strip().lower(),
        "page": request.query_params.get('page') or "1",
        "_agg": "sub",  # marca para distinguir cache
    }

    # Reutiliza key_prod_events pero distingue con sufijo para no colisionar
    base_key = key_prod_events(product.id, params)
    cache_key = f"{base_key}::sub-agg"
    cached = cache_get(cache_key)
    if cached is not None:
        return Response(cached)

    qs = (
        StockEvent.objects
        .filter(subproduct_stock__subproduct__parent_id=product.id, status=True)
        .select_related('product_stock', 'subproduct_stock', 'created_by')
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
