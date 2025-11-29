# apps/products/api/views/product_supplier_view.py

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from apps.products.models import Product
from apps.suppliers.api.serializers import SupplierProductSerializer
from apps.suppliers.api.repositories.supplier_repositories import SupplierProductRepository


@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
def product_supplier_list_create_view(request, prod_pk: int):
    """List or create supplier-specific configurations for a product.

    - GET: devuelve todas las filas activas de ``SupplierProduct`` para el producto.
    - POST: crea una nueva fila de lista de precios por proveedor.
    """

    try:
        product = Product.objects.get(pk=prod_pk, status=True)
    except Product.DoesNotExist:
        return Response({"detail": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        qs = SupplierProductRepository.get_all_by_product(product)
        serializer = SupplierProductSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST
    data = request.data.copy()
    data["product"] = product.pk
    serializer = SupplierProductSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save(user=request.user)
    return Response(SupplierProductSerializer(instance).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAdminUser])
def product_supplier_detail_view(request, prod_pk: int, sp_pk: int):
    """Retrieve, update or soft-delete a supplier-product configuration row."""

    try:
        product = Product.objects.get(pk=prod_pk, status=True)
    except Product.DoesNotExist:
        return Response({"detail": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    from apps.products.models.supplier_product_model import SupplierProduct

    try:
        instance = SupplierProduct.objects.get(pk=sp_pk, product=product, status=True)
    except SupplierProduct.DoesNotExist:
        return Response({"detail": "Configuración proveedor-producto no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = SupplierProductSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "PUT":
        serializer = SupplierProductSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save(user=request.user)
        return Response(SupplierProductSerializer(updated).data, status=status.HTTP_200_OK)

    # DELETE (soft delete)
    SupplierProductRepository.soft_delete(instance, user=request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)
