from rest_framework import serializers

from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.inventory_adjustments.models import StockAdjustment, StockAdjustmentItem


class StockAdjustmentItemSerializer(BaseSerializer):
    class Meta:
        model = StockAdjustmentItem
        fields = [
            "id",
            "adjustment",
            "product",
            "system_quantity",
            "counted_quantity",
            "difference",
            "reason",
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
            raise serializers.ValidationError("Debe informar la cantidad ajustada.")
        attrs["difference"] = counted_qty - system_qty
        return super().validate(attrs)


class StockAdjustmentSerializer(BaseSerializer):
    items = StockAdjustmentItemSerializer(many=True, read_only=True)

    class Meta:
        model = StockAdjustment
        fields = [
            "id",
            "adjustment_date",
            "concept",
            "observations",
            "legacy_id",
            "status_label",
            "items",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["status", "created_at", "modified_at"]

    def validate_adjustment_date(self, value):
        if value is None:
            raise serializers.ValidationError("Debe informar la fecha del ajuste.")
        return value
