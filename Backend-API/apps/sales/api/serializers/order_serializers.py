from rest_framework import serializers

from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.sales.models import SalesOrder, SalesOrderItem


class SalesOrderItemSerializer(BaseSerializer):
    class Meta:
        model = SalesOrderItem
        fields = [
            "id",
            "order",
            "product",
            "description",
            "quantity_ordered",
            "quantity_shipped",
            "unit_price",
            "discount_amount",
            "vat_rate_code",
            "legacy_detail_id",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = [
            "quantity_shipped",
            "status",
            "created_at",
            "modified_at",
        ]

    def validate_quantity_ordered(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser positiva.")
        return value


class SalesOrderSerializer(BaseSerializer):
    items = SalesOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = SalesOrder
        fields = [
            "id",
            "customer_legacy_id",
            "customer_legacy_name",
            "order_date",
            "currency",
            "exchange_rate",
            "reference",
            "notes",
            "discount_percent",
            "transport_legacy_id",
            "iva_condition_id",
            "legacy_id",
            "status_label",
            "items",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = [
            "status",
            "created_at",
            "modified_at",
        ]

    def validate_discount_percent(self, value):
        if value < 0:
            raise serializers.ValidationError("El descuento no puede ser negativo.")
        if value > 100:
            raise serializers.ValidationError("El descuento no puede superar el 100%.")
        return value
