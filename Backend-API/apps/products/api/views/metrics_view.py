from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.core.pagination import Pagination
from apps.products.api.repositories.catalog_repository import CatalogRepository
from apps.products.api.serializers.metrics_serializer import ProductMetricsSerializer
from apps.products.docs.metrics_doc import metrics_list_doc, metrics_detail_doc
from apps.products.models import Product


def _parse_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    return str(value).lower() in {"1", "true", "yes"}


def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@extend_schema(**metrics_list_doc)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def product_metrics_list_view(request):
    filters = {
        "include_inactive": _parse_bool(request.query_params.get("include_inactive")) or False,
        "category_id": _parse_int(request.query_params.get("category_id")),
        "rotation_min": _parse_int(request.query_params.get("rotation_min")),
        "rotation_max": _parse_int(request.query_params.get("rotation_max")),
        "days_since_last_sale": _parse_int(request.query_params.get("days_since_last_sale")),
    }

    queryset = CatalogRepository.metrics_queryset(filters=filters)
    paginator = Pagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = ProductMetricsSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@extend_schema(**metrics_detail_doc)
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def product_metrics_detail_view(request, prod_pk: int):
    queryset = CatalogRepository.metrics_queryset({"include_inactive": True})
    metrics = queryset.filter(product_id=prod_pk).first()

    if request.method == "GET":
        if not metrics:
            return Response({"detail": "Métricas no encontradas."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ProductMetricsSerializer(metrics).data)

    if not request.user.is_staff:
        return Response({"detail": "Permiso denegado."}, status=status.HTTP_403_FORBIDDEN)

    product = get_object_or_404(Product, pk=prod_pk)
    serializer = ProductMetricsSerializer(metrics, data=request.data, partial=True, context={"product": product})
    serializer.is_valid(raise_exception=True)
    instance = serializer.save(user=request.user)
    http_status = status.HTTP_200_OK if metrics else status.HTTP_201_CREATED
    return Response(ProductMetricsSerializer(instance).data, status=http_status)
