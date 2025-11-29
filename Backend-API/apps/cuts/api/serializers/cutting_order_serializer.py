# apps/cuts/api/serializers/cutting_order_serializer.py

from rest_framework import serializers  # Serializadores DRF
from django.contrib.auth import get_user_model  # Para obtener modelo de usuario activo
from django.utils import timezone  # Para timestamps (completed_at)
from decimal import Decimal, InvalidOperation  # Manejo de decimales correcto
from collections import defaultdict  # Para agrupar cantidades por subproducto
from django.db.models import Sum  # Agregaciones de reserva

from apps.stocks.models import SubproductStock  # Stock por subproducto
from apps.products.models.subproduct_model import Subproduct  # Modelo Subproduct
from apps.products.models.product_model import Product  # Modelo Product
from apps.cuts.models.cutting_order_model import CuttingOrder, CuttingOrderItem  # Modelos de corte
from apps.products.api.serializers.base_serializer import BaseSerializer  # Base con auditoría, etc.
from apps.orders.models.order import CustomerOrder
from apps.orders.models.order_line import CustomerOrderLine
from apps.orders.choices import OrderStatus

User = get_user_model()  # Modelo de usuario del proyecto


# ------------------ ÍTEMS ------------------

class CuttingOrderItemSerializer(serializers.ModelSerializer):
    """
    Ítem de orden con campos derivados del subproducto para uso directo en el front.
    Incluye: marca, número de bobina/rollo, tipo de forma, nombre del padre y stock actual.
    """
    # PK del subproducto, restringido a subproductos activos
    subproduct = serializers.PrimaryKeyRelatedField(
        queryset=Subproduct.objects.filter(status=True)
    )

    # 🔹 Derivados (solo lectura)
    subproduct_brand = serializers.SerializerMethodField(read_only=True)
    subproduct_number_coil = serializers.SerializerMethodField(read_only=True)
    subproduct_form_type = serializers.SerializerMethodField(read_only=True)
    parent_name = serializers.SerializerMethodField(read_only=True)
    item_current_stock = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CuttingOrderItem
        fields = [
            'id', 'subproduct', 'cutting_quantity',
            # derivados:
            'subproduct_brand', 'subproduct_number_coil', 'subproduct_form_type',
            'parent_name', 'item_current_stock',
        ]
        read_only_fields = [
            'id',
            'subproduct_brand', 'subproduct_number_coil', 'subproduct_form_type',
            'parent_name', 'item_current_stock',
        ]

    # ---------- Validaciones de campo ----------
    def validate_cutting_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad de corte debe ser mayor a cero.")
        return value

    # ---------- Getters derivados ----------

    def get_subproduct_brand(self, obj):
        sp = getattr(obj, 'subproduct', None)
        if not sp:
            return None
        # intenta en subproducto y luego en el padre
        return getattr(sp, 'brand', None) or getattr(getattr(sp, 'parent', None), 'brand', None)

    def get_subproduct_number_coil(self, obj):
        sp = getattr(obj, 'subproduct', None)
        if not sp:
            return None
        # normaliza distintos nombres posibles
        for attr in ('number_coil', 'coil_number', 'coil', 'roll_number', 'numero_bobina', 'numero_rollo'):
            v = getattr(sp, attr, None)
            if v not in (None, ''):
                return v
        return None

    def get_subproduct_form_type(self, obj):
        sp = getattr(obj, 'subproduct', None)
        return getattr(sp, 'form_type', None) if sp else None

    def get_parent_name(self, obj):
        p = getattr(getattr(obj, 'subproduct', None), 'parent', None)
        if not p:
            return None
        return getattr(p, 'name', None) or getattr(p, 'description', None) or str(p)

    def get_item_current_stock(self, obj):
        """
        Devuelve el stock actual del subproducto, si existe registro en SubproductStock.
        Ajusta a ss.current_stock si tu modelo usa ese nombre.
        """
        try:
            ss = SubproductStock.objects.get(subproduct=obj.subproduct, status=True)
            return ss.quantity  # ⬅️ CAMBIA a ss.current_stock si corresponde en tu modelo real
        except SubproductStock.DoesNotExist:
            return None


# ------------------ ORDEN ------------------

class CuttingOrderSerializer(BaseSerializer):
    """
    Serializer de CuttingOrder con:
    - items opcionales (si operator_can_edit_items=True).
    - validaciones de coherencia/stock/reservas.
    - transición de estados segura.
    - order_number único.
    - quantity_to_cut (cantidad objetivo total).
    """
    # Lista de ítems (puede venir vacía si el operario luego edita)
    items = CuttingOrderItemSerializer(many=True, required=False, allow_empty=True)

    # Pedido base y línea opcional para sincronizar datos
    order = serializers.PrimaryKeyRelatedField(queryset=CustomerOrder.objects.filter(status=True))
    order_line = serializers.PrimaryKeyRelatedField(
        queryset=CustomerOrderLine.objects.filter(status=True),
        required=False,
        allow_null=True
    )

    # Producto elegido, restringido a activos
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter(status=True))
    product_id = serializers.IntegerField(read_only=True)

    # Si True, se permite crear sin ítems y que el operario los seleccione luego
    operator_can_edit_items = serializers.BooleanField(required=False)

    # Cliente (snapshot derivado del pedido)
    customer = serializers.CharField(read_only=True)

    # Usuario asignado (opcional)
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        required=False, allow_null=True
    )

    # Estado de workflow (opcional en update, proxied al pedido)
    workflow_status = serializers.ChoiceField(
        choices=OrderStatus.choices,
        required=False
    )

    # Número de pedido (solo lectura, proviene del pedido)
    order_number = serializers.IntegerField(read_only=True)

    # Cantidad total a cortar (objetivo)
    quantity_to_cut = serializers.DecimalField(
        max_digits=12, decimal_places=2
    )

    # Solo lectura: label de estado
    workflow_status_display = serializers.CharField(
        source='get_workflow_status_display', read_only=True
    )

    # Solo lectura: advertencias por reservas en otras órdenes
    warnings = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CuttingOrder
        fields = [
            'id', 'order', 'order_line', 'product', 'operator_can_edit_items',
            'customer', 'workflow_status', 'workflow_status_display',
            'assigned_to', 'completed_at',
            'order_number', 'quantity_to_cut',
            'items',
            'status', 'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by',
            'warnings','product_id',
        ]
        read_only_fields = [
            'id', 'status', 'completed_at', 'order_number', 'customer',
            'created_at', 'modified_at', 'deleted_at',
            'created_by', 'modified_by', 'deleted_by',
            'workflow_status_display', 'warnings','product_id',
        ]

    # ------------------ HELPERS DE STOCK/RESERVAS ------------------

    def _reserved_qty(self, subproduct_id: int, exclude_order_id=None) -> Decimal:
        """
        Cantidad reservada (suma de cutting_quantity) para un subproducto
        en órdenes activas (pending/in_process). Puede excluir una orden (update).
        """
        qs = CuttingOrderItem.objects.filter(
            subproduct_id=subproduct_id,
            order__status=True,
            order__order__status__in=[OrderStatus.PENDING, OrderStatus.IN_PROCESS],
        )
        if exclude_order_id:
            qs = qs.exclude(order_id=exclude_order_id)
        return qs.aggregate(total=Sum('cutting_quantity'))['total'] or Decimal("0")

    def _available(self, subproduct: Subproduct, exclude_order_id=None) -> Decimal:
        """
        Disponibilidad = stock físico - reservas lógicas (otras órdenes activas).
        Ajusta el campo 'quantity' si en tu modelo real es 'current_stock'.
        """
        try:
            ss = SubproductStock.objects.get(subproduct=subproduct, status=True)
            qty = ss.quantity  # ⬅️ CAMBIAR a ss.current_stock si corresponde
        except SubproductStock.DoesNotExist:
            qty = Decimal("0")

        reserved = self._reserved_qty(subproduct.id, exclude_order_id=exclude_order_id)
        return Decimal(qty) - Decimal(reserved)

    # ------------------ VALIDACIONES DE ALTO NIVEL ------------------

    def validate(self, data):
        """
        Valida:
        - items requeridos si operator_can_edit_items == False (create o reemplazo).
        - coherencia subproducto ↔ producto.
        - stock suficiente (si vienen ítems a validar).
        - suma de ítems ≤ quantity_to_cut (con payload o con existentes).
        - transiciones válidas.
        - order_number único.
        """
        # Pedido base y línea seleccionada
        order_obj = data.get('order') or (self.instance.order if self.instance else None)
        if self.instance is None and order_obj is None:
            raise serializers.ValidationError({'order': 'Debe seleccionar un pedido.'})

        order_line = data.get('order_line') or (self.instance.order_line if self.instance else None)
        if order_line and order_obj and order_line.order_id != order_obj.id:
            raise serializers.ValidationError({'order_line': 'La línea no pertenece al pedido indicado.'})

        # Ítems del payload (None si no mandaron la clave; [] si mandaron vacío)
        items = data.get('items', None)

        # ¿se permite que el operario edite luego?
        op_can_edit = data.get('operator_can_edit_items')
        if op_can_edit is None and self.instance:
            op_can_edit = self.instance.operator_can_edit_items
        op_can_edit = bool(op_can_edit)

        # 1) Items requeridos si NO puede editar luego
        if not op_can_edit:
            if self.instance is None:
                if items is None or (isinstance(items, list) and len(items) == 0):
                    raise serializers.ValidationError("Debe incluir al menos un item de corte.")
            else:
                if items is not None and isinstance(items, list) and len(items) == 0:
                    raise serializers.ValidationError("Debe incluir al menos un item de corte.")

        # 2) Coherencia producto/subproducto y preparar validación de stock
        product = data.get('product') or (self.instance.product if self.instance else None)
        qty_per_subproduct = defaultdict(Decimal)

        if isinstance(items, list):
            for item in items:
                # Cantidad > 0 (Decimal)
                try:
                    qty = Decimal(str(item['cutting_quantity']))
                    if qty <= 0:
                        raise ValueError
                except (InvalidOperation, ValueError, KeyError):
                    raise serializers.ValidationError("Cantidad inválida en uno de los items.")

                # Subproducto debe pertenecer al producto
                subproduct = item.get('subproduct')
                if not isinstance(subproduct, Subproduct):
                    raise serializers.ValidationError("Subproducto inválido en uno de los items.")
                if product and subproduct.parent_id != product.id:
                    raise serializers.ValidationError({
                        'items': f"El subproducto {subproduct.id} no pertenece al producto indicado."
                    })

                # Acumular
                qty_per_subproduct[subproduct.id] += qty

            # 2.a) Disponibilidad (stock físico - reservas en otras órdenes)
            exclude_order_id = self.instance.id if self.instance else None
            for subproduct_id, total_needed in qty_per_subproduct.items():
                sub = Subproduct.objects.get(pk=subproduct_id, status=True)
                available = self._available(sub, exclude_order_id=exclude_order_id)
                if total_needed > available:
                    raise serializers.ValidationError({
                        'items': (
                            f"Stock insuficiente para el subproducto ID {subproduct_id}. "
                            f"Necesita {total_needed}, disponible {available} (considerando reservas)."
                        )
                    })

        # 3) Suma de ítems ≤ quantity_to_cut
        if 'quantity_to_cut' in data:
            qty_to_cut = Decimal(str(data['quantity_to_cut']))
        elif order_line and getattr(order_line, 'quantity_ordered', None) is not None:
            qty_to_cut = Decimal(str(order_line.quantity_ordered))
        else:
            qty_to_cut = self.instance.quantity_to_cut if self.instance else Decimal("0")

        if isinstance(items, list):
            total_needed = sum(Decimal(str(it['cutting_quantity'])) for it in items)
        else:
            if order_line and order_line.quantity_ordered is not None:
                total_needed = Decimal(str(order_line.quantity_ordered))
            elif self.instance:
                total_needed = self.instance.items.aggregate(t=Sum('cutting_quantity'))['t'] or Decimal("0")
            else:
                total_needed = Decimal("0")

        if total_needed > qty_to_cut:
            raise serializers.ValidationError({
                'items': f"La suma de cantidades ({total_needed}) excede la cantidad a cortar ({qty_to_cut})."
            })

        # 4) Transición de estado válida (si mandan workflow_status en update)
        target_status = data.get('workflow_status', None)
        if self.instance and target_status:
            current = self.instance.workflow_status
            allowed = {
                (OrderStatus.PENDING, OrderStatus.IN_PROCESS),
                (OrderStatus.IN_PROCESS, OrderStatus.COMPLETED),
                (OrderStatus.PENDING, OrderStatus.CANCELLED),
                (OrderStatus.IN_PROCESS, OrderStatus.CANCELLED),
            }
            if (current, target_status) not in allowed and current != target_status:
                raise serializers.ValidationError({
                    'workflow_status': (
                        f"Transición inválida: {current} → {target_status}. "
                        f"Permitidas: pending→in_process, in_process→completed, "
                        f"pending→cancelled, in_process→cancelled."
                    )
                })

        # 5) order_number único (create y update) – se deriva del pedido
        if order_obj:
            candidate_number = order_obj.legacy_id or order_obj.pk
            qs = CuttingOrder.objects.filter(order_number=candidate_number)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"order": "El pedido ya tiene una orden de corte asociada."})

        return data

    # ------------------ CRUD ------------------

    def create(self, validated_data):
        """
        Crea la orden y los ítems (si vinieron).
        """
        items_data = validated_data.pop('items', [])
        order = super().create(validated_data)  # BaseSerializer: crea con auditoría si aplica
        if items_data:
            CuttingOrderItem.objects.bulk_create([
                CuttingOrderItem(
                    order=order,
                    subproduct=item['subproduct'],
                    cutting_quantity=item['cutting_quantity']
                ) for item in items_data
            ])
        return order

    def update(self, instance, validated_data):
        """
        Update total o parcial:
        - Si viene 'workflow_status' y pasa a 'completed', setea completed_at.
        - Si viene 'items', se hace reemplazo completo de ítems.
        """
        items_data = validated_data.pop('items', None)

        # Detectar transición a completed
        target_status = validated_data.get('workflow_status', None)
        going_completed = (
            target_status == 'completed' and instance.workflow_status != 'completed'
        )

        order = super().update(instance, validated_data)

        # Setear completed_at si corresponde
        if going_completed and not order.completed_at:
            order.completed_at = timezone.now()
            order.save(update_fields=['completed_at'])

        # Reemplazo completo de ítems si la clave 'items' vino en el payload
        if items_data is not None:
            order.items.all().delete()
            if items_data:
                CuttingOrderItem.objects.bulk_create([
                    CuttingOrderItem(
                        order=order,
                        subproduct=item['subproduct'],
                        cutting_quantity=item['cutting_quantity']
                    ) for item in items_data
                ])
        return order

    # ------------------ SALIDA ------------------

    def to_representation(self, instance):
        """
        Ajusta la respuesta:
        - assigned_to (id) → username (o None)
        - product (id) → name/description/str(product)
        (El resto sale de ModelSerializer/BaseSerializer)
        """
        data = super().to_representation(instance)

        # assigned_to → username legible
        if instance.assigned_to_id:
            data["assigned_to"] = getattr(instance.assigned_to, "username", None)
        else:
            data["assigned_to"] = None

        # product → nombre/desc/str
        prod = getattr(instance, "product", None)
        if prod is not None:
            name = getattr(prod, "name", None)
            description = getattr(prod, "description", None)
            data["product"] = name or description or str(prod)
        else:
            data["product"] = None

        return data

    # ------------------ Warnings ------------------

    def get_warnings(self, instance):
        """
        Para cada subproducto ítem de esta orden, calcula:
        - cuántas otras órdenes activas (pending/in_process) lo reservan,
        - cuánto reservaron,
        - cuánto quedaría disponible excluyendo esas reservas.
        Además devuelve marca / número de bobina / nombre del padre por campos separados.
        """
        if not isinstance(instance, CuttingOrder) or not instance.pk:
            return []

        results = []
        items = instance.items.select_related('subproduct', 'subproduct__parent')
        seen = set()

        for it in items:
            sub = it.subproduct
            if sub.id in seen:
                continue
            seen.add(sub.id)

            # Reservas en otras órdenes
            qs = (
                CuttingOrderItem.objects
                .filter(
                    subproduct_id=sub.id,
                    order__status=True,
                    order__order__status__in=[OrderStatus.PENDING, OrderStatus.IN_PROCESS],
                )
                .exclude(order_id=instance.id)
            )

            other_reserved = qs.aggregate(total=Sum('cutting_quantity'))['total'] or Decimal("0")
            other_orders_count = qs.values('order_id').distinct().count()

            # Stock base del subproducto (ajustar 'quantity' si tu campo real es 'current_stock')
            try:
                ss = SubproductStock.objects.get(subproduct=sub, status=True)
                base_qty = Decimal(ss.quantity)  # ⬅️ CAMBIAR a ss.current_stock si corresponde
            except SubproductStock.DoesNotExist:
                base_qty = Decimal("0")

            available_excl_others = base_qty - Decimal(other_reserved)

            # Derivados separados
            brand = getattr(sub, 'brand', None) or getattr(getattr(sub, 'parent', None), 'brand', None)
            number_coil = None
            for attr in ('number_coil', 'coil_number', 'coil', 'roll_number', 'numero_bobina', 'numero_rollo'):
                v = getattr(sub, attr, None)
                if v not in (None, ''):
                    number_coil = v
                    break
            parent_name = None
            if getattr(sub, 'parent', None):
                parent = sub.parent
                parent_name = getattr(parent, 'name', None) or getattr(parent, 'description', None) or str(parent)

            if other_orders_count > 0 and other_reserved > 0:
                results.append({
                    "subproduct_id": sub.id,
                    # separados:
                    "subproduct_brand": brand,
                    "subproduct_number_coil": number_coil,
                    "parent_name": parent_name,
                    # compat:
                    "subproduct_str": str(sub),
                    # reservas:
                    "other_active_orders_count": other_orders_count,
                    "other_reserved_qty": other_reserved,
                    "available_excluding_others": available_excl_others,
                })

        return results
