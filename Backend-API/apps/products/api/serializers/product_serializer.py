# apps/products/api/serializers/product_serializer.py
from rest_framework import serializers
from decimal import Decimal
from django.db.models import Sum

from apps.products.models.product_model import Product
from apps.products.models.category_model import Category
from apps.products.api.serializers.subproduct_serializer import SubProductSerializer
from apps.products.api.serializers.product_image_serializer import ProductImageSerializer
from apps.suppliers.api.serializers import SupplierProductSerializer
from apps.products.api.serializers.customer_product_serializer import CustomerProductSerializer

from apps.stocks.models import ProductStock, SubproductStock  # 👈 para el fallback
from .base_serializer import BaseSerializer


class ProductSerializer(BaseSerializer):
    """
    Serializer final para Producto.
    - Usa BaseSerializer para auditoría.
    - Muestra stock actual calculado ('current_stock').
    - Incluye imágenes relacionadas ('product_images').
    - Acepta ajuste de stock opcional en PUT ('quantity_change', 'reason').
    """

    # --- Relaciones ---
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(status=True),
        required=True
    )

    # --- Derivados de FK ---
    category_name = serializers.CharField(source='category.name', read_only=True)
    # --- Subproductos e imágenes ---
    subproducts = SubProductSerializer(many=True, read_only=True)
    product_images = ProductImageSerializer(many=True, read_only=True)

    # --- Configuración por proveedor/cliente ---
    suppliers = SupplierProductSerializer(many=True, read_only=True, source="supplier_products")
    customers = CustomerProductSerializer(many=True, read_only=True, source="customer_products")

    # --- Stock actual dinámico (con fallback si no viene anotado en la QuerySet) ---
    current_stock = serializers.SerializerMethodField(read_only=True)

    # --- Ajuste opcional de stock (escritura solamente) ---
    quantity_change = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        write_only=True,
        required=False,
        allow_null=True
    )
    reason = serializers.CharField(
        max_length=255,
        write_only=True,
        required=False,
        allow_null=True,
        allow_blank=True
    )

    class Meta:
        model = Product
        fields = [
            # Identidad y catálogo básico
            'id', 'code', 'name',

            # Precios y costos
            'price', 'last_purchase_cost', 'vat_condition_code',

            # Unidades y stock paramétrico (no cantidades reales)
            'unit', 'min_stock',

            # Descripciones
            'detail_internal', 'detail_public',

            # Información adicional de catálogo
            'brand', 'location', 'position',

            # Rubro / categoría
            'category', 'category_name',

            # Subproductos y stock derivado
            'has_subproducts',
            'current_stock',
            'subproducts',
            'product_images',

            # Configuración específica
            'suppliers',
            'customers',
            'status',
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by',
            'quantity_change', 'reason',
        ]
        read_only_fields = [
            'status', 'subproducts', 'current_stock', 'product_images',
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by',
            'category_name',
        ]

    # --- Cálculo de current_stock ---
    def get_current_stock(self, obj):
        """
        1) Si la QuerySet ya trae 'current_stock' anotado (lista), úsalo.
        2) Si no, calcula:
           - Si tiene subproductos: suma de SubproductStock activos.
           - Si no: ProductStock (si existe y está activo).
        """
        anotado = getattr(obj, "current_stock", None)
        if anotado is not None:
            return float(anotado)

        # Fallback para detail (u otras vistas sin annotate)
        if getattr(obj, "has_subproducts", False):
            total = (
                SubproductStock.objects
                .filter(
                    subproduct__parent_id=obj.pk,
                    status=True,
                    subproduct__status=True
                )
                .aggregate(total=Sum("quantity"))
                .get("total")
            )
            return float(total) if total is not None else 0.0

        # Sin subproductos: usar ProductStock si está activo
        qty = (
            ProductStock.objects
            .filter(product=obj, status=True)
            .values_list("quantity", flat=True)
            .first()
        )
        return float(qty) if qty is not None else 0.0

    # --- Validaciones personalizadas ---
    def validate_name(self, value):
        return self._get_normalized_name(value) if value else value

    def validate_code(self, value):
        qs = Product.objects.filter(code=value, status=True)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un producto con este código.")
        return value

    def validate_quantity_change(self, value):
        if value is not None and value == 0:
            raise serializers.ValidationError("La cantidad del ajuste no puede ser cero.")
        return value

    def validate(self, data):
        quantity_change = data.get("quantity_change")
        reason = data.get("reason")
        if quantity_change and not reason:
            raise serializers.ValidationError({"reason": "Se requiere una razón para el ajuste de stock."})
        return data

    # --- Representación personalizada para el frontend ---
    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Forzar IDs de FK (opcional; DRF ya los devuelve con PrimaryKeyRelatedField)
        rep["category"] = instance.category.id if instance.category else None

        return rep
