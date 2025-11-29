from rest_framework import serializers

from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.products.models.metrics_model import ProductMetrics
from apps.products.models.product_model import Product


class ProductMetricsSerializer(BaseSerializer):
    """Serializer maestro para métricas agregadas de artículos."""

    product = serializers.PrimaryKeyRelatedField(read_only=True)
    product_code = serializers.CharField(source="product.code", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    category_name = serializers.CharField(source="product.category.name", read_only=True)

    class Meta:
        model = ProductMetrics
        fields = [
            "id",
            "product",
            "product_code",
            "product_name",
            "category_name",
            "vend_6m",
            "vend_3m",
            "vend_prev_3m",
            "tendencia_3m",
            "rotation",
            "rotation_pct",
            "monthly_avg",
            "days_since_last_sale",
            "stock_current",
            "stock_min",
            "position",
            "purchased_pending",
            "orders_pending",
            "purchased_3m",
            "purchased_6m",
            "purchase_score",
            "calculated_at",
            "status",
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]
        read_only_fields = [
            "id",
            "product",
            "product_code",
            "product_name",
            "category_name",
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]

    def create(self, validated_data, user=None):
        product = self.context.get("product")
        if not isinstance(product, Product):
            raise serializers.ValidationError("El producto es obligatorio en el contexto.")
        validated_data["product"] = product
        return super().create(validated_data, user=user)

    def update(self, instance, validated_data, user=None):
        validated_data.pop("product", None)
        return super().update(instance, validated_data, user=user)
