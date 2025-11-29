from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.products.api.repositories.catalog_repository import CatalogRepository
from apps.products.api.serializers.stock_history_serializer import ProductStockHistorySerializer
from apps.products.docs.catalog_doc import catalog_history_doc
from apps.products.models import Product


@extend_schema(**catalog_history_doc)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def product_stock_history_view(request, prod_pk: int):
    try:
        Product.objects.get(pk=prod_pk)
    except Product.DoesNotExist:
        return Response({"detail": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    limit_param = request.query_params.get("limit")
    try:
        limit = int(limit_param) if limit_param is not None else 50
    except (TypeError, ValueError):
        limit = 50
    limit = max(1, min(limit, 500))

    history = CatalogRepository.get_stock_history(prod_pk, limit)
    serializer = ProductStockHistorySerializer(history, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
