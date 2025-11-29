from rest_framework import serializers

from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.inventory_adjustments.models import InventoryCount, InventoryCountItem


class InventoryCountItemSerializer(BaseSerializer):
    class Meta:
        model = InventoryCountItem
        fields = [
            "id",
            "count",
            "product",
            "system_quantity",
            "counted_quantity",
            "difference",
            "observations",
            "legacy_id",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["difference", "status", "created_at", "modified_at"]

    def validate(self, attrs):
        system_qty = attrs.get("system_quantity", getattr(self.instance, "system_quantity", 0))
        counted_qty = attrs.get("counted_quantity", getattr(self.instance, "counted_quantity", 0))
        if counted_qty is None:
            raise serializers.ValidationError("Debe informar la cantidad contada.")
        attrs["difference"] = counted_qty - system_qty
        return super().validate(attrs)


class InventoryCountSerializer(BaseSerializer):
    items = InventoryCountItemSerializer(many=True, read_only=True)

    class Meta:
        model = InventoryCount
        fields = [
            "id",
            "count_date",
            "description",
            "notes",
            "legacy_id",
            "closed_at",
            "status_label",
            "items",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["status", "created_at", "modified_at", "closed_at"]

    def validate_count_date(self, value):
        if value is None:
            raise serializers.ValidationError("Debe informar la fecha del conteo.")
        return value
