from rest_framework import serializers

from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.purchases.models import PurchaseOrder, PurchaseOrderItem


class PurchaseOrderItemSerializer(BaseSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = [
            "id",
            "order",
            "product",
            "description",
            "quantity_ordered",
            "quantity_received",
            "unit_price",
            "discount_amount",
            "tax_code",
            "legacy_description_id",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = [
            "quantity_received",
            "status",
            "created_at",
            "modified_at",
        ]


class PurchaseOrderSerializer(BaseSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "supplier",
            "supplier_name",
            "order_date",
            "currency",
            "exchange_rate",
            "reference",
            "notes",
            "discount_percent",
            "carrier",
            "carrier_name_snapshot",
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
            "carrier_name_snapshot",
            "created_at",
            "modified_at",
        ]

    def validate_discount_percent(self, value):
        if value < 0:
            raise serializers.ValidationError("El descuento no puede ser negativo.")
        if value > 100:
            raise serializers.ValidationError("El descuento no puede superar el 100%.")
        return value
