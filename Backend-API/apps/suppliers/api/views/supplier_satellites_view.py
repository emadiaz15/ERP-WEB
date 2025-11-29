import logging
from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.pagination import Pagination
from apps.core.utils import broadcast_crud_event
from apps.products.models.supplier_product_model import SupplierProduct
from apps.suppliers.api.repositories.supplier_repositories import (
    SupplierProductDescriptionRepository,
    SupplierProductDiscountRepository,
    SupplierCostHistoryRepository,
)
from apps.suppliers.api.serializers import (
    SupplierProductDescriptionSerializer,
    SupplierProductDiscountSerializer,
    SupplierCostHistorySerializer,
)
from apps.suppliers.docs.supplier_doc import (
    supplier_description_list_doc,
    supplier_description_create_doc,
    supplier_description_detail_doc,
    supplier_description_update_doc,
    supplier_description_delete_doc,
    supplier_discount_list_doc,
    supplier_discount_create_doc,
    supplier_discount_detail_doc,
    supplier_discount_update_doc,
    supplier_discount_delete_doc,
    supplier_cost_history_list_doc,
)
from apps.suppliers.utils.cache_invalidation import (
    invalidate_supplier_description_cache,
    invalidate_supplier_discount_cache,
)
from apps.suppliers.utils.cache_keys import (
    supplier_description_list_cache_key,
    supplier_discount_list_cache_key,
    supplier_cost_history_cache_key,
)

logger = logging.getLogger(__name__)

DESC_LIST_TTL = 60 * 5
DISCOUNT_LIST_TTL = 60 * 5
COST_HISTORY_TTL = 60 * 10


def _get_supplier_product(prod_pk: int, sp_pk: int) -> SupplierProduct:
    return get_object_or_404(
        SupplierProduct.objects.select_related("product"),
        pk=sp_pk,
        product_id=prod_pk,
        status=True,
    )


def _cache_filters(request):
    params = request.query_params.copy()
    filters = {k: params.get(k) for k in params}
    filters.setdefault("page", params.get("page", 1))
    filters.setdefault("page_size", params.get("page_size", Pagination.page_size))
    return filters


def _parse_bool(value):
    if value is None:
        return None
    value = value.strip().lower()
    if value in {"1", "true", "t", "yes", "y"}:
        return True
    if value in {"0", "false", "f", "no", "n"}:
        return False
    return None


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD.") from exc


@extend_schema(methods=["GET"], **supplier_description_list_doc)
@extend_schema(methods=["POST"], **supplier_description_create_doc)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def supplier_description_list_create_view(request, prod_pk: int, sp_pk: int):
    supplier_product = _get_supplier_product(prod_pk, sp_pk)

    if request.method == "GET":
        filters = _cache_filters(request)
        cache_key = supplier_description_list_cache_key(
            supplier_product_id=supplier_product.id,
            **filters,
        )
        use_cache = not settings.DEBUG
        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)

        qs = SupplierProductDescriptionRepository.list_active(
            supplier_product,
            search=request.query_params.get("search"),
        )
        paginator = Pagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = SupplierProductDescriptionSerializer(
            page,
            many=True,
            context={"request": request},
        )
        response = paginator.get_paginated_response(serializer.data)

        if use_cache:
            cache.set(cache_key, response.data, DESC_LIST_TTL)
        return response

    if not request.user.is_staff:
        return Response({"detail": "Solo administradores."}, status=status.HTTP_403_FORBIDDEN)

    serializer = SupplierProductDescriptionSerializer(
        data=request.data,
        context={"request": request, "supplier_product": supplier_product},
    )
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    instance = serializer.save(user=request.user)
    invalidate_supplier_description_cache()
    payload = SupplierProductDescriptionSerializer(instance).data
    broadcast_crud_event("create", "suppliers", "SupplierProductDescription", payload)
    return Response(payload, status=status.HTTP_201_CREATED)


@extend_schema(methods=["GET"], **supplier_description_detail_doc)
@extend_schema(methods=["PUT"], **supplier_description_update_doc)
@extend_schema(methods=["DELETE"], **supplier_description_delete_doc)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def supplier_description_detail_view(request, prod_pk: int, sp_pk: int, desc_pk: int):
    supplier_product = _get_supplier_product(prod_pk, sp_pk)
    instance = get_object_or_404(
        SupplierProductDescriptionRepository.list_active(supplier_product),
        pk=desc_pk,
    )

    if request.method == "GET":
        data = SupplierProductDescriptionSerializer(instance).data
        return Response(data)

    if not request.user.is_staff:
        return Response({"detail": "Solo administradores."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "PUT":
        serializer = SupplierProductDescriptionSerializer(
            instance,
            data=request.data,
            partial=True,
            context={"request": request, "supplier_product": supplier_product},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        updated = serializer.save(user=request.user)
        invalidate_supplier_description_cache()
        payload = SupplierProductDescriptionSerializer(updated).data
        broadcast_crud_event("update", "suppliers", "SupplierProductDescription", payload)
        return Response(payload)

    SupplierProductDescriptionRepository.soft_delete(instance, user=request.user)
    invalidate_supplier_description_cache()
    broadcast_crud_event("delete", "suppliers", "SupplierProductDescription", {"id": instance.id})
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(methods=["GET"], **supplier_discount_list_doc)
@extend_schema(methods=["POST"], **supplier_discount_create_doc)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def supplier_discount_list_create_view(request, prod_pk: int, sp_pk: int):
    supplier_product = _get_supplier_product(prod_pk, sp_pk)

    if request.method == "GET":
        filters = _cache_filters(request)
        cache_key = supplier_discount_list_cache_key(
            supplier_product_id=supplier_product.id,
            **filters,
        )
        use_cache = not settings.DEBUG
        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)

        negative_only = _parse_bool(request.query_params.get("negative_only"))
        qs = SupplierProductDiscountRepository.list_active(
            supplier_product,
            search=request.query_params.get("search"),
            negative_only=negative_only,
        )
        paginator = Pagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = SupplierProductDiscountSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)

        if use_cache:
            cache.set(cache_key, response.data, DISCOUNT_LIST_TTL)
        return response

    if not request.user.is_staff:
        return Response({"detail": "Solo administradores."}, status=status.HTTP_403_FORBIDDEN)

    serializer = SupplierProductDiscountSerializer(
        data=request.data,
        context={"request": request, "supplier_product": supplier_product},
    )
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    instance = serializer.save(user=request.user)
    invalidate_supplier_discount_cache()
    payload = SupplierProductDiscountSerializer(instance).data
    broadcast_crud_event("create", "suppliers", "SupplierProductDiscount", payload)
    return Response(payload, status=status.HTTP_201_CREATED)


@extend_schema(methods=["GET"], **supplier_discount_detail_doc)
@extend_schema(methods=["PUT"], **supplier_discount_update_doc)
@extend_schema(methods=["DELETE"], **supplier_discount_delete_doc)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def supplier_discount_detail_view(request, prod_pk: int, sp_pk: int, disc_pk: int):
    supplier_product = _get_supplier_product(prod_pk, sp_pk)
    instance = get_object_or_404(
        SupplierProductDiscountRepository.list_active(supplier_product),
        pk=disc_pk,
    )

    if request.method == "GET":
        data = SupplierProductDiscountSerializer(instance).data
        return Response(data)

    if not request.user.is_staff:
        return Response({"detail": "Solo administradores."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "PUT":
        serializer = SupplierProductDiscountSerializer(
            instance,
            data=request.data,
            partial=True,
            context={"request": request, "supplier_product": supplier_product},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        updated = serializer.save(user=request.user)
        invalidate_supplier_discount_cache()
        payload = SupplierProductDiscountSerializer(updated).data
        broadcast_crud_event("update", "suppliers", "SupplierProductDiscount", payload)
        return Response(payload)

    SupplierProductDiscountRepository.soft_delete(instance, user=request.user)
    invalidate_supplier_discount_cache()
    broadcast_crud_event("delete", "suppliers", "SupplierProductDiscount", {"id": instance.id})
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(methods=["GET"], **supplier_cost_history_list_doc)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def supplier_cost_history_list_view(request, prod_pk: int, sp_pk: int):
    supplier_product = _get_supplier_product(prod_pk, sp_pk)
    filters = _cache_filters(request)
    cache_key = supplier_cost_history_cache_key(
        supplier_product_id=supplier_product.id,
        **filters,
    )
    use_cache = not settings.DEBUG
    if use_cache:
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

    try:
        date_from = _parse_date(request.query_params.get("date_from"))
        date_to = _parse_date(request.query_params.get("date_to"))
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    qs = SupplierCostHistoryRepository.list_by_supplier_product(
        supplier_product,
        date_from=date_from,
        date_to=date_to,
        currency=request.query_params.get("currency"),
    )
    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = SupplierCostHistorySerializer(page, many=True)
    response = paginator.get_paginated_response(serializer.data)

    if use_cache:
        cache.set(cache_key, response.data, COST_HISTORY_TTL)
    return response
