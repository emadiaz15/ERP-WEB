from decimal import Decimal, InvalidOperation
from rest_framework import serializers

from apps.products.models.subproduct_model import Subproduct
from apps.stocks.models.stock_subproduct_model import SubproductStock
from .base_serializer import BaseSerializer


class SubProductSerializer(BaseSerializer):
    """
    Serializer final para Subproducto.
    - Usa BaseSerializer para auditoría.
    - Calcula 'current_stock' con SerializerMethodField (lee SubproductStock activo).
    - Acepta opcionalmente ajuste de stock en PUT ('quantity_change', 'reason').
    - Usa 'parent_product' en context para validar number_coil por padre.
    - ⚠️ Regla: initial_stock_quantity es OBLIGATORIO y > 0 en creación.
    - NOTA: la inicialización de stock ahora se realiza en la view (create_subproduct), no por signal.
    """

    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    parent_type_name = serializers.CharField(source='parent.type.name', read_only=True)
    parent_code = serializers.CharField(source='parent.code', read_only=True)

    current_stock = serializers.SerializerMethodField()

    # Campos de "ajuste rápido" para updates (no intervienen en create)
    quantity_change = serializers.DecimalField(
        max_digits=15, decimal_places=2, write_only=True, required=False, allow_null=True
    )
    reason = serializers.CharField(
        max_length=255, write_only=True, required=False, allow_null=True, allow_blank=True
    )

    # Campo requerido en creación
    initial_stock_quantity = serializers.DecimalField(
        max_digits=15, decimal_places=2, required=True
    )

    class Meta:
        model = Subproduct
        fields = [
            'id', 'brand', 'number_coil',
            'initial_enumeration', 'final_enumeration',
            'gross_weight', 'net_weight',
            'initial_stock_quantity', 'location',
            'technical_sheet_photo', 'form_type', 'observations',
            'parent', 'parent_name', 'parent_type_name', 'parent_code',
            'current_stock', 'status',
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by',
            'quantity_change', 'reason'
        ]
        read_only_fields = [
            'parent', 'parent_name', 'parent_type_name', 'status', 'current_stock',
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by'
        ]

    # ---------- presentational stock ----------
    def get_current_stock(self, obj):
        # Robusto ante posibles duplicados accidentales (no debería ocurrir)
        qty = (
            SubproductStock.objects
            .filter(subproduct=obj, status=True)
            .values_list('quantity', flat=True)
            .first()
        )
        return qty if qty is not None else Decimal("0.00")

    # -------------------- Validaciones de campo --------------------
    def validate_quantity_change(self, value):
        if value is not None:
            try:
                if Decimal(value) == 0:
                    raise serializers.ValidationError("La cantidad del ajuste no puede ser cero si se proporciona.")
            except (InvalidOperation, TypeError):
                raise serializers.ValidationError("La cantidad del ajuste debe ser numérica.")
        return value

    def validate_initial_stock_quantity(self, value):
        """Stock inicial obligatorio y > 0."""
        try:
            dec = Decimal(value)
        except (InvalidOperation, TypeError):
            raise serializers.ValidationError("La cantidad inicial debe ser un número válido.")
        if dec <= 0:
            raise serializers.ValidationError("El stock inicial debe ser mayor a 0.")
        return dec

    # -------------------- Validaciones de objeto --------------------
    def validate(self, data):
        errors = {}

        # Ajustes: si hay cantidad, requerir razón
        quantity_change = data.get('quantity_change')
        reason = data.get('reason')
        try:
            if quantity_change is not None and Decimal(quantity_change) != 0 and not reason:
                errors.setdefault("reason", []).append("Se requiere una razón para el ajuste de stock.")
        except (InvalidOperation, TypeError):
            errors.setdefault("quantity_change", []).append("La cantidad del ajuste debe ser numérica.")

        # Unicidad de number_coil por padre (string, case-insensitive). Trim y vacío -> None.
        parent = self.context.get("parent_product")
        if 'number_coil' in data:
            raw_nc = data.get("number_coil")
            nc = None if raw_nc is None else str(raw_nc).strip()
            if not nc:
                data["number_coil"] = None
            else:
                data["number_coil"] = nc  # guardamos tal cual; la comparación será iexact
                if parent:
                    from apps.products.models.subproduct_model import Subproduct as SP
                    qs = SP.objects.filter(parent=parent, number_coil__iexact=nc, status=True)
                    if self.instance:
                        qs = qs.exclude(id=self.instance.id)
                    if qs.exists():
                        errors.setdefault("number_coil", []).append(
                            "Ya existe un subproducto con ese número de bobina para este producto."
                        )
                if len(nc) > 50:
                    errors.setdefault("number_coil", []).append("Máximo 50 caracteres.")

        # Enumeraciones
        ini = data.get("initial_enumeration")
        fin = data.get("final_enumeration")
        try:
            if ini is not None and fin is not None and Decimal(fin) < Decimal(ini):
                errors.setdefault("final_enumeration", []).append(
                    "Debe ser mayor o igual a la enumeración inicial."
                )
            for field_name, val in (("initial_enumeration", ini), ("final_enumeration", fin)):
                if val is not None and Decimal(val) < 0:
                    errors.setdefault(field_name, []).append("No puede ser negativo.")
        except (InvalidOperation, TypeError):
            pass

        # Pesos
        gw = data.get("gross_weight")
        nw = data.get("net_weight")
        try:
            if gw is not None and Decimal(gw) < 0:
                errors.setdefault("gross_weight", []).append("No puede ser negativo.")
            if nw is not None and Decimal(nw) < 0:
                errors.setdefault("net_weight", []).append("No puede ser negativo.")
            if gw is not None and nw is not None and Decimal(nw) > Decimal(gw):
                errors.setdefault("net_weight", []).append("No puede ser mayor que el peso bruto.")
        except (InvalidOperation, TypeError):
            pass

        # initial_stock_quantity: en creación obligatorio y > 0; en update solo numérico
        if self.instance is None:
            if 'initial_stock_quantity' not in data:
                errors.setdefault("initial_stock_quantity", []).append("Campo requerido.")
            else:
                try:
                    if Decimal(data['initial_stock_quantity']) <= 0:
                        errors.setdefault("initial_stock_quantity", []).append("Debe ser mayor a 0.")
                except (InvalidOperation, TypeError):
                    errors.setdefault("initial_stock_quantity", []).append("Debe ser un número válido.")
        else:
            if 'initial_stock_quantity' in data:
                try:
                    Decimal(data['initial_stock_quantity'])
                except (InvalidOperation, TypeError):
                    errors.setdefault("initial_stock_quantity", []).append("Debe ser un número válido.")

        if errors:
            raise serializers.ValidationError(errors)

        return data

    # -------------------- Creación --------------------
    def create(self, validated_data):
        """
        La inicialización de stock se realiza en la view create_subproduct (no por signal).
        Aquí solo se guarda la instancia.
        """
        request = self.context.get('request')
        user = request.user if request else None
        obj = Subproduct(**validated_data)
        obj.save(user=user)
        return obj
