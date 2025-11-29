from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.inventory_adjustments.models import StockHistory


class StockHistorySerializer(BaseSerializer):
    class Meta:
        model = StockHistory
        fields = [
            "id",
            "product",
            "movement_type",
            "movement_date",
            "movement_time",
            "previous_quantity",
            "quantity_delta",
            "resulting_quantity",
            "observations",
            "detail",
            "adjustment",
            "inventory_count",
            "legacy_id",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["status", "created_at", "modified_at"]
