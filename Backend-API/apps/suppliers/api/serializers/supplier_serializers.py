from rest_framework import serializers

from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.suppliers.models import Supplier
from apps.products.models.supplier_product_model import SupplierProduct
from apps.products.models.supplier_discount_model import (
    SupplierProductDescription,
    SupplierProductDiscount,
)
from apps.stocks.models import SupplierCostHistory


class SupplierSerializer(BaseSerializer):
    """Serializer maestro de proveedores."""

    class Meta:
        model = Supplier
        fields = [
            "id",
            "name",
            "address",
            "location_legacy_id",
            "sign_number",
            "phone1",
            "phone2",
            "mobile",
            "tax_id",
            "email",
            "tax_condition_code",
            "perception",
            "discount_for_payment",
            "balance",
            "credit_balance",
            "last_invoice_letter",
            "last_invoice_pos",
            "notes",
            "status",
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]
        read_only_fields = [
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]

    def validate_name(self, value: str) -> str:
        if not value:
            raise serializers.ValidationError("El nombre es obligatorio.")
        return self._get_normalized_name(value)

    def validate_tax_id(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("El CUIT debe ser positivo.")
        return value


class SupplierProductSerializer(BaseSerializer):
    """Serializer reutilizado para configuraciones proveedor-producto."""

    class Meta:
        model = SupplierProduct
        fields = [
            "id",
            "product",
            "supplier_legacy_id",
            "cost",
            "sale_cost",
            "description",
            "currency",
            "price_list_number",
            "other_flag",
            "exchange_rate_ref",
            "status",
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]
        read_only_fields = [
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]

    def validate(self, attrs):
        supplier_legacy_id = attrs.get("supplier_legacy_id") or getattr(self.instance, "supplier_legacy_id", None)
        product = attrs.get("product") or getattr(self.instance, "product", None)
        price_list_number = attrs.get("price_list_number") or getattr(self.instance, "price_list_number", None)
        if supplier_legacy_id is None:
            raise serializers.ValidationError({"supplier_legacy_id": "Debe indicar el ID legacy del proveedor."})
        if product is None:
            raise serializers.ValidationError({"product": "Debe indicar el producto."})
        if price_list_number is None:
            raise serializers.ValidationError({"price_list_number": "Debe indicar el número de lista."})

        qs = SupplierProduct.objects.filter(
            supplier_legacy_id=supplier_legacy_id,
            product=product,
            price_list_number=price_list_number,
            status=True,
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Ya existe una configuración activa para este proveedor, producto y número de lista.",
            )
        return attrs


class SupplierProductDescriptionSerializer(BaseSerializer):
    """Serializer para descripciones alternativas por proveedor."""

    supplier_product = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SupplierProductDescription
        fields = [
            "id",
            "supplier_product",
            "description",
            "status",
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]
        read_only_fields = [
            "supplier_product",
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]

    def validate_description(self, value):
        description = (value or "").strip()
        if not description:
            raise serializers.ValidationError("La descripción no puede estar vacía.")
        supplier_product = self.context.get("supplier_product")
        qs = SupplierProductDescription.objects.filter(
            supplier_product=supplier_product,
            description__iexact=description,
            status=True,
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if supplier_product and qs.exists():
            raise serializers.ValidationError(
                "Ya existe una descripción igual para este proveedor-producto.",
            )
        return description

    def create(self, validated_data, user=None):
        supplier_product = self.context.get("supplier_product")
        if not supplier_product:
            raise serializers.ValidationError("Falta supplier_product en el contexto.")
        validated_data["supplier_product"] = supplier_product
        return super().create(validated_data, user=user)

    def update(self, instance, validated_data, user=None):
        validated_data.pop("supplier_product", None)
        return super().update(instance, validated_data, user=user)


class SupplierProductDiscountSerializer(BaseSerializer):
    """Serializer para descuentos configurados en listas de proveedores."""

    supplier_product = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SupplierProductDiscount
        fields = [
            "id",
            "supplier_product",
            "discount_legacy_id",
            "is_negative",
            "status",
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]
        read_only_fields = [
            "supplier_product",
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]

    def validate_discount_legacy_id(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("El identificador legacy debe ser positivo.")
        supplier_product = self.context.get("supplier_product")
        qs = SupplierProductDiscount.objects.filter(
            supplier_product=supplier_product,
            discount_legacy_id=value,
            status=True,
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if supplier_product and qs.exists():
            raise serializers.ValidationError(
                "Ya existe un descuento con ese identificador para este proveedor-producto.",
            )
        return value

    def create(self, validated_data, user=None):
        supplier_product = self.context.get("supplier_product")
        if not supplier_product:
            raise serializers.ValidationError("Falta supplier_product en el contexto.")
        validated_data["supplier_product"] = supplier_product
        return super().create(validated_data, user=user)

    def update(self, instance, validated_data, user=None):
        validated_data.pop("supplier_product", None)
        return super().update(instance, validated_data, user=user)


class SupplierCostHistorySerializer(BaseSerializer):
    """Serializer de sólo lectura para el histórico de costos."""

    supplier_product = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SupplierCostHistory
        fields = [
            "id",
            "supplier_product",
            "date",
            "previous_cost",
            "new_cost",
            "previous_sale_cost",
            "new_sale_cost",
            "currency",
            "status",
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]
        read_only_fields = fields

    def create(self, validated_data, user=None):  # pragma: no cover - read only
        raise serializers.ValidationError("El histórico es de solo lectura.")

    def update(self, instance, validated_data, user=None):  # pragma: no cover
        raise serializers.ValidationError("El histórico es de solo lectura.")
