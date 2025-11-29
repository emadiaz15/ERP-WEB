from rest_framework import serializers

from apps.stocks.models.history_models import ProductStockHistory


class ProductStockHistorySerializer(serializers.ModelSerializer):
    """Serializer compacto para exponer movimientos de HISTOSTOCK."""

    class Meta:
        model = ProductStockHistory
        fields = [
            "id",
            "product",
            "date",
            "time",
            "movement_type",
            "previous_quantity",
            "quantity_change",
            "balance",
            "notes",
            "detail",
        ]
        read_only_fields = fields
