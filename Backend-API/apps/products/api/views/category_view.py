# apps/products/api/views/category_view.py

import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.views.decorators.cache import cache_page

from apps.products.models.category_model import Category
from apps.products.api.serializers.category_serializer import CategorySerializer
from apps.products.api.repositories.category_repository import CategoryRepository
from apps.products.filters.category_filter import CategoryFilter
from apps.core.pagination import Pagination


from apps.products.utils.cache_keys import CATEGORY_LIST_CACHE_PREFIX
from apps.products.utils.cache_invalidation import invalidate_category_cache
from apps.core.utils import broadcast_crud_event

logger = logging.getLogger(__name__)

# ── CACHE DE LISTADO (TTL 60s) ────────────────────────────────
# Antes era "None" (infinito hasta invalidación). Reducimos a 60s para evitar servir datos obsoletos mucho tiempo
# y aun así disminuir hits a DB en escenarios de polling frecuente.
CATEGORY_LIST_TTL = 60  # 1 minuto
cache_decorator = cache_page(CATEGORY_LIST_TTL, key_prefix=CATEGORY_LIST_CACHE_PREFIX)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_decorator
def category_list(request):
    """
    Lista categorías activas (TTL 60s + invalidación proactiva en CREATE/UPDATE/DELETE).
    """
    qs = Category.objects.filter(status=True).select_related('created_by')
    qs = CategoryFilter(request.GET, queryset=qs).qs
    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    data = CategorySerializer(page, many=True, context={'request': request}).data
    return paginator.get_paginated_response(data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_category(request):
    """
    Crea una nueva categoría (solo admins) e invalida caché de lista.
    """
    serializer = CategorySerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    category = serializer.save(user=request.user)
    # Invalidar caché de lista y emitir evento WebSocket
    invalidate_category_cache()
    logger.debug("Cache de category_list invalidada tras CREATE")
    response_data = CategorySerializer(category, context={'request': request}).data
    broadcast_crud_event(
        event_type="create",
        app="products",
        model="Category",
        data=response_data
    )
    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def category_detail(request, category_pk):
    """
    GET: obtiene detalle de categoría.
    PUT: actualiza categoría (solo admins) e invalida caché de lista.
    DELETE: soft-delete de categoría (solo admins) e invalida caché de lista.
    """
    category = CategoryRepository.get_by_id(category_pk)
    if not category:
        return Response({"detail": "Categoría no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    # GET (sin cache_page)
    if request.method == 'GET':
        return Response(CategorySerializer(category, context={'request': request}).data)

    # PUT
    if request.method == 'PUT':
        if not request.user.is_staff:
            return Response({"detail": "Sin permiso."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CategorySerializer(
            category,
            data=request.data,
            context={'request': request},
            partial=True
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        updated = CategoryRepository.update(
            category_instance=category,
            user=request.user,
            **serializer.validated_data
        )
        # Invalidar caché y emitir evento WebSocket
        invalidate_category_cache()
        logger.debug("Cache de category_list invalidada tras UPDATE")
        response_data = CategorySerializer(updated, context={'request': request}).data
        broadcast_crud_event(
            event_type="update",
            app="products",
            model="Category",
            data=response_data
        )
        return Response(response_data)

    # DELETE
    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response({"detail": "Sin permiso."}, status=status.HTTP_403_FORBIDDEN)

        CategoryRepository.soft_delete(category, user=request.user)
        # Invalidar caché y emitir evento WebSocket
        invalidate_category_cache()
        logger.debug("Cache de category_list invalidada tras DELETE")
        broadcast_crud_event(
            event_type="delete",
            app="products",
            model="Category",
            data={"id": category.id}
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
