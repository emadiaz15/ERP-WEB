# apps/stocks/api/serializers/stock_adjust_serializer.py

from rest_framework import serializers

class StockAdjustInputSerializer(serializers.Serializer):
    event_type = serializers.ChoiceField(choices=["ingreso_ajuste", "egreso_ajuste"])
    quantity_change = serializers.DecimalField(max_digits=18, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        qty = attrs["quantity_change"]
        if qty == 0:
            raise serializers.ValidationError("quantity_change no puede ser 0")

        # Normaliza el signo según el tipo
        et = attrs["event_type"]
        if et == "ingreso_ajuste" and qty < 0:
            attrs["quantity_change"] = abs(qty)
        if et == "egreso_ajuste" and qty > 0:
            attrs["quantity_change"] = -qty
        return attrs
