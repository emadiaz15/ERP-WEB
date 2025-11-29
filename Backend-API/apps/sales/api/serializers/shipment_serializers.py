from rest_framework import serializers

from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.sales.models import SalesShipment, SalesShipmentItem


class SalesShipmentItemSerializer(BaseSerializer):
    class Meta:
        model = SalesShipmentItem
        fields = [
            "id",
            "shipment",
            "order_item",
            "product",
            "description",
            "quantity",
            "unit_price",
            "vat_rate_code",
            "legacy_detail_id",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["status", "created_at", "modified_at"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser positiva.")
        return value


class SalesShipmentSerializer(BaseSerializer):
    items = SalesShipmentItemSerializer(many=True, read_only=True)

    class Meta:
        model = SalesShipment
        fields = [
            "id",
            "order",
            "customer_legacy_id",
            "shipment_date",
            "reference",
            "transport_legacy_id",
            "notes",
            "legacy_id",
            "status_label",
            "items",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["status", "created_at", "modified_at"]
