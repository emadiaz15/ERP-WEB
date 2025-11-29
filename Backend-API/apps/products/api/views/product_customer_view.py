# apps/products/api/views/product_customer_view.py

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from apps.products.models import Product
from apps.products.api.serializers.customer_product_serializer import CustomerProductSerializer
from apps.products.api.repositories.customer_product_repository import CustomerProductRepository


@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
def product_customer_list_create_view(request, prod_pk: int):
    """List or create customer-specific configurations for a product.

    - GET: devuelve todas las filas activas de ``CustomerProduct`` para el producto.
    - POST: crea una nueva fila para un cliente legacy dado.
    """

    try:
        product = Product.objects.get(pk=prod_pk, status=True)
    except Product.DoesNotExist:
        return Response({"detail": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        qs = CustomerProductRepository.get_all_by_product(product)
        serializer = CustomerProductSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST
    data = request.data.copy()
    data["product"] = product.pk
    serializer = CustomerProductSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save(user=request.user)
    return Response(CustomerProductSerializer(instance).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAdminUser])
def product_customer_detail_view(request, prod_pk: int, cp_pk: int):
    """Retrieve, update or soft-delete a customer-product configuration row."""

    try:
        product = Product.objects.get(pk=prod_pk, status=True)
    except Product.DoesNotExist:
        return Response({"detail": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    from apps.products.models.customer_product_model import CustomerProduct

    try:
        instance = CustomerProduct.objects.get(pk=cp_pk, product=product, status=True)
    except CustomerProduct.DoesNotExist:
        return Response({"detail": "Configuración cliente-producto no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = CustomerProductSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "PUT":
        serializer = CustomerProductSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save(user=request.user)
        return Response(CustomerProductSerializer(updated).data, status=status.HTTP_200_OK)

    # DELETE (soft delete)
    CustomerProductRepository.soft_delete(instance, user=request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)
