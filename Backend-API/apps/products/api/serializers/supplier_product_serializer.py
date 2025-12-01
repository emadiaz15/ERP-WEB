"""Serializers for SupplierProduct and related models."""

from rest_framework import serializers
from apps.products.models import SupplierProduct, SupplierProductPriceHistory


class SupplierProductPriceHistorySerializer(serializers.ModelSerializer):
    """Serializer for reading supplier product price history records.

    Returns historical price data including validity periods and change information.
    """

    changed_by_name = serializers.SerializerMethodField()
    is_current = serializers.SerializerMethodField()
    duration_days = serializers.SerializerMethodField()

    class Meta:
        model = SupplierProductPriceHistory
        fields = [
            "id",
            "supplier_product",
            "cost",
            "sale_cost",
            "currency",
            "exchange_rate_ref",
            "valid_from",
            "valid_to",
            "changed_by",
            "changed_by_name",
            "notes",
            "is_current",
            "duration_days",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_changed_by_name(self, obj):
        """Get full name of user who made the change."""
        if obj.changed_by:
            return f"{obj.changed_by.name} {obj.changed_by.last_name}".strip()
        return None

    def get_is_current(self, obj):
        """Check if this is the current active price."""
        return obj.is_current()

    def get_duration_days(self, obj):
        """Calculate duration in days this price was valid."""
        if obj.valid_from and obj.valid_to:
            delta = obj.valid_to - obj.valid_from
            return delta.days
        return None


class SupplierProductPriceHistoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating price history records manually.

    Used when importing historical data or manually recording price changes.
    """

    class Meta:
        model = SupplierProductPriceHistory
        fields = [
            "supplier_product",
            "cost",
            "sale_cost",
            "currency",
            "exchange_rate_ref",
            "valid_from",
            "changed_by",
            "notes",
        ]

    def validate(self, attrs):
        """Validate price history data."""
        if attrs.get("cost") is None and attrs.get("sale_cost") is None:
            raise serializers.ValidationError(
                "At least one of 'cost' or 'sale_cost' must be provided."
            )
        return attrs


class SupplierProductSerializer(serializers.ModelSerializer):
    """Serializer for SupplierProduct model.

    Includes basic supplier product information and related product data.
    """

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_code = serializers.CharField(source="product.code", read_only=True)
    current_price = serializers.SerializerMethodField()

    class Meta:
        model = SupplierProduct
        fields = [
            "id",
            "product",
            "product_name",
            "product_code",
            "supplier_legacy_id",
            "cost",
            "sale_cost",
            "description",
            "currency",
            "price_list_number",
            "other_flag",
            "exchange_rate_ref",
            "current_price",
            "created_at",
            "updated_at",
            "status",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_current_price(self, obj):
        """Get current price history record if available."""
        from apps.products.services.supplier_price_history_service import SupplierPriceHistoryService

        current = SupplierPriceHistoryService.get_current_price(obj)
        if current:
            return {
                "cost": str(current.cost) if current.cost else None,
                "sale_cost": str(current.sale_cost) if current.sale_cost else None,
                "valid_from": current.valid_from,
                "currency": current.currency,
            }
        return None


class SupplierProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for SupplierProduct including price history.

    Used for detail views where complete information is needed.
    """

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_code = serializers.CharField(source="product.code", read_only=True)
    price_history = serializers.SerializerMethodField()
    recent_price_changes = serializers.SerializerMethodField()

    class Meta:
        model = SupplierProduct
        fields = [
            "id",
            "product",
            "product_name",
            "product_code",
            "supplier_legacy_id",
            "cost",
            "sale_cost",
            "description",
            "currency",
            "price_list_number",
            "other_flag",
            "exchange_rate_ref",
            "price_history",
            "recent_price_changes",
            "created_at",
            "updated_at",
            "status",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_price_history(self, obj):
        """Get all price history records."""
        from apps.products.services.supplier_price_history_service import SupplierPriceHistoryService

        history = SupplierPriceHistoryService.get_price_history(obj)
        return SupplierProductPriceHistorySerializer(history, many=True).data

    def get_recent_price_changes(self, obj):
        """Get last 5 price changes."""
        from apps.products.services.supplier_price_history_service import SupplierPriceHistoryService

        history = SupplierPriceHistoryService.get_price_history(obj, limit=5)
        return SupplierProductPriceHistorySerializer(history, many=True).data


class SupplierProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating SupplierProduct records.

    Automatically creates initial price history record via signal.
    """

    class Meta:
        model = SupplierProduct
        fields = [
            "product",
            "supplier_legacy_id",
            "cost",
            "sale_cost",
            "description",
            "currency",
            "price_list_number",
            "other_flag",
            "exchange_rate_ref",
        ]

    def validate(self, attrs):
        """Validate supplier product data."""
        if not attrs.get("product"):
            raise serializers.ValidationError({"product": "Product is required."})

        # Verificar que no exista duplicado
        product = attrs.get("product")
        supplier_id = attrs.get("supplier_legacy_id")

        if supplier_id:
            exists = SupplierProduct.objects.filter(
                product=product,
                supplier_legacy_id=supplier_id,
                status=True
            ).exists()

            if exists:
                raise serializers.ValidationError(
                    "A supplier product with this product and supplier already exists."
                )

        return attrs


class SupplierProductUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating SupplierProduct records.

    Price changes are automatically tracked via signal.
    """

    class Meta:
        model = SupplierProduct
        fields = [
            "cost",
            "sale_cost",
            "description",
            "currency",
            "price_list_number",
            "other_flag",
            "exchange_rate_ref",
            "status",
        ]

    def validate(self, attrs):
        """Validate update data."""
        # Si se está actualizando el precio, podríamos agregar validaciones adicionales
        if "cost" in attrs and attrs["cost"] is not None and attrs["cost"] < 0:
            raise serializers.ValidationError({"cost": "Cost cannot be negative."})

        if "sale_cost" in attrs and attrs["sale_cost"] is not None and attrs["sale_cost"] < 0:
            raise serializers.ValidationError({"sale_cost": "Sale cost cannot be negative."})

        return attrs
