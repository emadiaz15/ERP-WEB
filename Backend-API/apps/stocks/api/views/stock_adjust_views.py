from apps.stocks.utils.cache_utils import invalidate_subproduct_events, invalidate_product_events
from apps.core.utils import broadcast_crud_event
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.stocks.models import SubproductStock, ProductStock, StockEvent
from apps.stocks.api.serializers.stock_event_serializer import StockEventSerializer
from apps.stocks.api.serializers.stock_adjust_serializer import StockAdjustInputSerializer
from apps.stocks.services import adjust_subproduct_stock, adjust_product_stock
from apps.products.api.serializers.product_serializer import ProductSerializer
from apps.products.api.serializers.subproduct_serializer import SubProductSerializer
from apps.products.utils.cache_invalidation import (
    invalidate_product_cache,
    invalidate_subproduct_cache,
)


def _ensure_event_from_service_result(result, *, product_stock=None, subproduct_stock=None, user=None):
    """
    Soporta ambos comportamientos:
    - Si el service retorna StockEvent -> lo usa directo.
    - Si retorna ProductStock/SubproductStock -> busca el último evento creado por el usuario.
    """
    if isinstance(result, StockEvent):
        return result

    qs = StockEvent.objects.all()
    if product_stock is not None:
        qs = qs.filter(product_stock=product_stock)
    if subproduct_stock is not None:
        qs = qs.filter(subproduct_stock=subproduct_stock)
    if user is not None:
        qs = qs.filter(created_by=user)

    return qs.order_by("-created_at", "-id").first()


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])  # solo staff
def subproduct_stock_adjust(request, subproduct_id: int):
    """
    Ajuste manual de stock para un SubproductStock activo.
    Espera: { event_type: ingreso_ajuste|egreso_ajuste, quantity_change, notes? }
    """
    stock = get_object_or_404(SubproductStock, subproduct_id=subproduct_id, status=True)

    ser_in = StockAdjustInputSerializer(data=request.data)
    ser_in.is_valid(raise_exception=True)

    event_type = ser_in.validated_data["event_type"]
    quantity_change = ser_in.validated_data["quantity_change"]
    notes = ser_in.validated_data.get("notes") or ""

    # Llama al servicio. Si tu servicio acepta force_event_type, pásalo; si no, igual funcionará por el signo normalizado.
    result = adjust_subproduct_stock(
        subproduct_stock=stock,
        quantity_change=quantity_change,
        reason=notes,
        user=request.user,
        # force_event_type=event_type,  # Descomenta si agregas ese parámetro en tu service
    )

    event = _ensure_event_from_service_result(
        result, subproduct_stock=stock, user=request.user
    )
    if event is None:
        return Response(
            {"detail": "El ajuste se aplicó, pero no se pudo recuperar el evento."},
            status=status.HTTP_200_OK,
        )

    # Invalidar cache de eventos de este subproducto
    invalidate_subproduct_events(subproduct_id)
    out = StockEventSerializer(event, context={"request": request})

    # Emitir evento WebSocket para notificar a todos los usuarios logueados
    broadcast_crud_event(
        event_type="create",  # o "update" si corresponde, aquí es ajuste manual
        app="stocks",
        model="StockEvent",
        data=out.data,
    )
    # Además, invalidar caches y emitir update del subproducto y su producto padre para refrescar stock en UI
    try:
        subp = stock.subproduct  # relacionado por FK
        invalidate_subproduct_cache()
        if subp and getattr(subp, "parent_id", None):
            invalidate_product_cache()
        # Broadcast del Subproduct actualizado
        subp_ser = SubProductSerializer(subp, context={"request": request, "parent_product": getattr(subp, "parent", None)}).data
        broadcast_crud_event(
            event_type="update",
            app="products",
            model="Subproduct",
            data=subp_ser,
        )
        # Broadcast del Product padre actualizado
        if getattr(subp, "parent", None):
            prod_ser = ProductSerializer(subp.parent, context={"request": request}).data
            broadcast_crud_event(
                event_type="update",
                app="products",
                model="Product",
                data=prod_ser,
            )
    except Exception:
        # No romper respuesta si falla broadcast adicional
        pass
    return Response(out.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])  # opcional: staff-only
def product_stock_adjust(request, product_id: int):
    """
    Ajuste manual de stock para un ProductStock activo (productos sin subproductos).
    Espera: { event_type: ingreso_ajuste|egreso_ajuste, quantity_change, notes? }
    """
    stock = get_object_or_404(ProductStock, product_id=product_id, status=True)

    ser_in = StockAdjustInputSerializer(data=request.data)
    ser_in.is_valid(raise_exception=True)

    event_type = ser_in.validated_data["event_type"]
    quantity_change = ser_in.validated_data["quantity_change"]
    notes = ser_in.validated_data.get("notes") or ""

    result = adjust_product_stock(
        product_stock=stock,
        quantity_change=quantity_change,
        reason=notes,
        user=request.user,
        # force_event_type=event_type,  # Descomenta si agregas ese parámetro en tu service
    )

    event = _ensure_event_from_service_result(
        result, product_stock=stock, user=request.user
    )
    if event is None:
        return Response(
            {"detail": "El ajuste se aplicó, pero no se pudo recuperar el evento."},
            status=status.HTTP_200_OK,
        )

    # Invalidar cache de eventos de este producto
    invalidate_product_events(product_id)
    out = StockEventSerializer(event, context={"request": request})

    # Emitir evento WebSocket para notificar a todos los usuarios logueados
    broadcast_crud_event(
        event_type="create",  # o "update" si corresponde, aquí es ajuste manual
        app="stocks",
        model="StockEvent",
        data=out.data,
    )
    # Además, invalidar caches y emitir update del producto para refrescar stock en UI
    try:
        prod = stock.product
        invalidate_product_cache()
        prod_ser = ProductSerializer(prod, context={"request": request}).data
        broadcast_crud_event(
            event_type="update",
            app="products",
            model="Product",
            data=prod_ser,
        )
    except Exception:
        pass
    return Response(out.data, status=status.HTTP_201_CREATED)
