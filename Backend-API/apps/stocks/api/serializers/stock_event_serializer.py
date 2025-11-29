# apps/stocks/api/serializers/stock_event_serializer.py

from rest_framework import serializers
from apps.stocks.models.stock_event_model import StockEvent
from apps.stocks.models.stock_product_model import ProductStock
from apps.stocks.models.stock_subproduct_model import SubproductStock
from apps.products.api.serializers.base_serializer import BaseSerializer


class StockEventSerializer(BaseSerializer):
    """Serializer para eventos de stock, con auditoría y validaciones de consistencia."""

    product_stock = serializers.PrimaryKeyRelatedField(
        queryset=ProductStock.objects.all(),
        required=False,
        allow_null=True,
    )
    subproduct_stock = serializers.PrimaryKeyRelatedField(
        queryset=SubproductStock.objects.all(),
        required=False,
        allow_null=True,
    )

    # Representación
    product_stock_info = serializers.StringRelatedField(source='product_stock', read_only=True)
    subproduct_stock_info = serializers.StringRelatedField(source='subproduct_stock', read_only=True)

    # (Opcional pero útil para docs/autocompletado)
    event_type = serializers.ChoiceField(choices=StockEvent.EVENT_TYPES)

    # ------- Campos de conveniencia para el frontend -------
    # Mantengo los nombres que tu UI espera (date, type, quantity, description, user)
    date = serializers.DateTimeField(source='created_at', read_only=True)
    type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    user = serializers.SerializerMethodField(read_only=True)
    quantity = serializers.DecimalField(source='quantity_change', max_digits=15, decimal_places=2, read_only=True)
    description = serializers.CharField(source='notes', read_only=True, allow_null=True)

    # Nuevos campos presentacionales
    direction = serializers.SerializerMethodField(read_only=True)     # "ingreso" | "egreso"
    abs_quantity = serializers.SerializerMethodField(read_only=True)  # |quantity_change|

    class Meta:
        model = StockEvent
        fields = [
            'id',
            # Datos crudos
            'quantity_change', 'event_type', 'notes',
            'product_stock', 'subproduct_stock',
            'product_stock_info', 'subproduct_stock_info',
            'created_at', 'created_by',

            # Conveniencia para UI
            'date', 'type_display', 'user', 'quantity', 'description',

            # Nuevos
            'direction', 'abs_quantity',
        ]
        read_only_fields = [
            'created_at',
            'created_by',
            'product_stock_info', 'subproduct_stock_info',
            'date', 'type_display', 'user', 'quantity', 'description',
            'direction', 'abs_quantity',
        ]

    def get_user(self, obj):
        u = getattr(obj, 'created_by', None)
        return getattr(u, 'username', None) if u else None

    def get_direction(self, obj):
        qc = getattr(obj, 'quantity_change', None)
        if qc is None:
            return None
        return "ingreso" if qc > 0 else "egreso"

    def get_abs_quantity(self, obj):
        qc = getattr(obj, 'quantity_change', None)
        return abs(qc) if qc is not None else None

    def validate(self, data):
        product_stock = data.get('product_stock', getattr(self.instance, 'product_stock', None))
        subproduct_stock = data.get('subproduct_stock', getattr(self.instance, 'subproduct_stock', None))
        quantity_change = data.get('quantity_change', getattr(self.instance, 'quantity_change', 0))
        event_type = data.get('event_type', getattr(self.instance, 'event_type', None))

        if not product_stock and not subproduct_stock:
            raise serializers.ValidationError("Asocia el evento a ProductStock o SubproductStock.")
        if product_stock and subproduct_stock:
            raise serializers.ValidationError("El evento no puede referenciar ambos stocks a la vez.")
        if quantity_change == 0:
            raise serializers.ValidationError("La cantidad de cambio no puede ser cero.")

        # Reglas de signo coherentes con el tipo de evento
        salidas = {'egreso_venta', 'egreso_corte', 'egreso_ajuste', 'traslado_salida'}
        entradas = {'ingreso_ajuste', 'ingreso', 'traslado_entrada', 'ingreso_inicial'}
        if event_type in salidas and quantity_change > 0:
            raise serializers.ValidationError("Para eventos de egreso, 'quantity_change' debe ser negativo.")
        if event_type in entradas and quantity_change < 0:
            raise serializers.ValidationError("Para eventos de ingreso, 'quantity_change' debe ser positivo.")

        return data
