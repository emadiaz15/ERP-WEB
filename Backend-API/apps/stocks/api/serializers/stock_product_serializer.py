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
from apps.stocks.api.repositories.stock_product_repository import StockProductRepository
from apps.products.models.product_model import Product
from apps.stocks.models.stock_event_model import StockEvent
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
def product_stock_event_history(request, pk):
    """
    Historial de eventos de stock para un *producto* que NO tiene subproductos.
    Filtros: ?start=ISO&end=ISO&event_type=...
    """
    product = get_object_or_404(Product, pk=pk, status=True)

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

    qs = (
        StockEvent.objects
        .filter(product_stock=stock_record, status=True)
        .select_related('product_stock', 'subproduct_stock', 'created_by')
        .order_by('-created_at')
    )

    # Filtros opcionales
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
