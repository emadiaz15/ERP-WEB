"""Views for supplier product price history management."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.users.permissions import CanManageProducts, CanViewProducts
from apps.products.models import SupplierProduct, SupplierProductPriceHistory
from apps.products.api.serializers import (
    SupplierProductPriceHistorySerializer,
    SupplierProductPriceHistoryCreateSerializer,
)
from apps.products.services.supplier_price_history_service import SupplierPriceHistoryService
from apps.products.docs.supplier_price_history_doc import (
    list_supplier_price_history_doc,
    create_supplier_price_history_doc,
    get_supplier_price_history_detail_doc,
    get_current_supplier_price_doc,
)


@extend_schema(**list_supplier_price_history_doc)
@api_view(["GET"])
@permission_classes([IsAuthenticated, CanViewProducts])
def supplier_price_history_list_view(request, supplier_product_id: int):
    """List all price history records for a supplier product.

    Returns all historical price records ordered by valid_from descending.
    The first record in the list will be the current active price (valid_to=NULL).
    """
    try:
        supplier_product = SupplierProduct.objects.get(pk=supplier_product_id, status=True)
    except SupplierProduct.DoesNotExist:
        return Response(
            {"detail": "Supplier product not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    history = SupplierPriceHistoryService.get_price_history(supplier_product)
    serializer = SupplierProductPriceHistorySerializer(history, many=True)

    return Response({
        "supplier_product_id": supplier_product.id,
        "product_name": supplier_product.product.name if supplier_product.product else None,
        "supplier_id": supplier_product.supplier_legacy_id,
        "total_records": len(history),
        "history": serializer.data
    }, status=status.HTTP_200_OK)


@extend_schema(**create_supplier_price_history_doc)
@api_view(["POST"])
@permission_classes([IsAuthenticated, CanManageProducts])
def supplier_price_history_create_view(request, supplier_product_id: int):
    """Create a new price history record for a supplier product.

    This endpoint allows manual creation of price history records,
    useful for importing historical data or recording special price changes.

    Note: Price changes made via the SupplierProduct update endpoint
    are automatically recorded by the system signal.
    """
    try:
        supplier_product = SupplierProduct.objects.get(pk=supplier_product_id, status=True)
    except SupplierProduct.DoesNotExist:
        return Response(
            {"detail": "Supplier product not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    data = request.data.copy()
    data["supplier_product"] = supplier_product.id
    data["changed_by"] = request.user.id

    serializer = SupplierProductPriceHistoryCreateSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    # Usar el servicio para crear el registro (maneja el cierre del registro anterior)
    history_record = SupplierPriceHistoryService.create_price_history_record(
        supplier_product=supplier_product,
        cost=serializer.validated_data.get("cost"),
        sale_cost=serializer.validated_data.get("sale_cost"),
        currency=serializer.validated_data.get("currency"),
        exchange_rate_ref=serializer.validated_data.get("exchange_rate_ref"),
        changed_by=request.user,
        notes=serializer.validated_data.get("notes"),
        valid_from=serializer.validated_data.get("valid_from"),
    )

    response_serializer = SupplierProductPriceHistorySerializer(history_record)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(**get_supplier_price_history_detail_doc)
@api_view(["GET"])
@permission_classes([IsAuthenticated, CanViewProducts])
def supplier_price_history_detail_view(request, supplier_product_id: int, history_id: int):
    """Get details of a specific price history record."""
    try:
        history_record = SupplierProductPriceHistory.objects.get(
            pk=history_id,
            supplier_product_id=supplier_product_id
        )
    except SupplierProductPriceHistory.DoesNotExist:
        return Response(
            {"detail": "Price history record not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = SupplierProductPriceHistorySerializer(history_record)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(**get_current_supplier_price_doc)
@api_view(["GET"])
@permission_classes([IsAuthenticated, CanViewProducts])
def supplier_current_price_view(request, supplier_product_id: int):
    """Get the current active price for a supplier product.

    Returns the price history record with valid_to=NULL (current price).
    """
    try:
        supplier_product = SupplierProduct.objects.get(pk=supplier_product_id, status=True)
    except SupplierProduct.DoesNotExist:
        return Response(
            {"detail": "Supplier product not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    current_price = SupplierPriceHistoryService.get_current_price(supplier_product)

    if not current_price:
        return Response(
            {"detail": "No current price found for this supplier product."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = SupplierProductPriceHistorySerializer(current_price)
    return Response(serializer.data, status=status.HTTP_200_OK)
