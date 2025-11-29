from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.core.pagination import Pagination
from apps.products.api.repositories.catalog_repository import CatalogRepository
from apps.products.api.serializers.catalog_serializer import (
    CatalogProductSerializer,
    CatalogSearchParamsSerializer,
    ProductInsightSerializer,
)
from apps.products.docs.catalog_doc import catalog_search_doc, catalog_insight_doc
from apps.products.models import Product


@extend_schema(**catalog_search_doc)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def catalog_search_view(request):
    """Búsqueda inteligente en el catálogo maestro."""

    params = CatalogSearchParamsSerializer(data=request.query_params)
    params.is_valid(raise_exception=True)
    filters = params.validated_data.copy()
    keyword = filters.pop("query", "")

    queryset = CatalogRepository.search_products(keyword=keyword, filters=filters)
    paginator = Pagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = CatalogProductSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@extend_schema(**catalog_insight_doc)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def catalog_product_insight_view(request, prod_pk: int):
    """Devuelve todos los satélites del artículo (métricas, alias, history)."""

    try:
        product = CatalogRepository.get_product_with_relations(prod_pk)
    except Product.DoesNotExist:
        return Response({"detail": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    try:
        history_limit = int(request.query_params.get("history_limit", 25))
    except (TypeError, ValueError):
        history_limit = 25
    history_limit = max(1, min(history_limit, 200))

    history = CatalogRepository.get_stock_history(prod_pk, history_limit)
    serializer = ProductInsightSerializer(product, context={"history": history})
    return Response(serializer.data, status=status.HTTP_200_OK)
