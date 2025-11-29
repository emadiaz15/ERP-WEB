# apps/cuts/api/repositories/cutting_order_repository.py
from typing import Optional, Dict, Any, List, Iterable, Tuple
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Sum, Q, Prefetch
from django.utils import timezone

from apps.cuts.models.cutting_order_model import CuttingOrder, CuttingOrderItem
from apps.users.models.user_model import User
from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct
from apps.stocks.models import SubproductStock  # ⬅️ Ajusta si tu módulo difiere


class CuttingOrderRepository:
    """
    Repository con reglas de negocio nucleares:
    - order_number único
    - quantity_to_cut requerido (>= 0.01)
    - coherencia producto/subproductos
    - suma(items) <= quantity_to_cut
    - disponibilidad de stock = físico - reservas (pending/in_process)
    - transiciones de estado válidas
    - completed_at al pasar a completed
    """

    # -----------------------
    # Lecturas convenientes
    # -----------------------

    @staticmethod
    def get_by_id(order_id: int) -> Optional[CuttingOrder]:
        try:
            return (
                CuttingOrder.objects
                .select_related('assigned_to', 'created_by', 'product')
                .prefetch_related(
                    Prefetch(
                        'items',
                        queryset=CuttingOrderItem.objects.select_related('subproduct', 'subproduct__parent')
                    )
                )
                .get(id=order_id, status=True)
            )
        except CuttingOrder.DoesNotExist:
            return None

    @staticmethod
    def get_all_active() -> models.QuerySet:
        return (
            CuttingOrder.objects
            .filter(status=True)
            .select_related('assigned_to', 'created_by', 'product')
            .prefetch_related(
                Prefetch(
                    'items',
                    queryset=CuttingOrderItem.objects.select_related('subproduct', 'subproduct__parent')
                )
            )
        )

    @staticmethod
    def get_cutting_orders_assigned_to(user: User) -> models.QuerySet:
        if not isinstance(user, User):
            return CuttingOrder.objects.none()
        return (
            CuttingOrder.objects
            .filter(assigned_to=user, status=True)
            .select_related('assigned_to', 'created_by', 'product')
            .prefetch_related(
                Prefetch(
                    'items',
                    queryset=CuttingOrderItem.objects.select_related('subproduct', 'subproduct__parent')
                )
            )
        )

    # -----------------------
    # Helpers de validación
    # -----------------------

    @staticmethod
    def _reserved_qty(subproduct_id: int, exclude_order_id: Optional[int] = None) -> Decimal:
        """
        Suma de cutting_quantity en órdenes activas (pending/in_process) para un subproducto.
        """
        qs = CuttingOrderItem.objects.filter(
            subproduct_id=subproduct_id,
            order__status=True,
            order__workflow_status__in=['pending', 'in_process'],
        )
        if exclude_order_id:
            qs = qs.exclude(order_id=exclude_order_id)
        return qs.aggregate(total=Sum('cutting_quantity'))['total'] or Decimal("0")

    @staticmethod
    def _available(subproduct: Subproduct, exclude_order_id: Optional[int] = None) -> Decimal:
        """
        Disponibilidad = stock físico - reservas lógicas (otras órdenes activas).
        ⚠️ Si tu modelo usa 'current_stock' en vez de 'quantity', cambia la línea marcada.
        """
        try:
            ss = SubproductStock.objects.get(subproduct=subproduct, status=True)
            base_qty = Decimal(ss.quantity)  # ⬅️ CAMBIA a ss.current_stock si corresponde
        except SubproductStock.DoesNotExist:
            base_qty = Decimal("0")
        reserved = CuttingOrderRepository._reserved_qty(subproduct.id, exclude_order_id=exclude_order_id)
        return base_qty - Decimal(reserved)

    @staticmethod
    def _coerce_items(items: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normaliza items: garantiza instancias de Subproduct y Decimal en cutting_quantity.
        """
        norm_items = []
        for idx, it in enumerate(items or []):
            sub = it.get('subproduct')
            qty = it.get('cutting_quantity')

            # subproduct puede venir como id o instancia
            if isinstance(sub, int):
                try:
                    sub = Subproduct.objects.get(pk=sub, status=True)
                except Subproduct.DoesNotExist:
                    raise ValidationError(f"Subproducto inválido en ítem #{idx+1}.")
            elif not isinstance(sub, Subproduct):
                raise ValidationError(f"Subproducto inválido en ítem #{idx+1}.")

            # qty debe ser Decimal > 0
            try:
                qty = Decimal(str(qty))
                if qty <= 0:
                    raise InvalidOperation
            except (InvalidOperation, TypeError):
                raise ValidationError(f"Cantidad inválida en ítem para subproducto {getattr(sub, 'id', '?')}.")

            norm_items.append({'subproduct': sub, 'cutting_quantity': qty})
        return norm_items

    @staticmethod
    def _merge_duplicate_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Si el payload tiene subproductos repetidos, los mergea sumando cantidades,
        para evitar violar la UniqueConstraint (order, subproduct).
        """
        acc = {}
        for it in items:
            sub_id = it['subproduct'].id
            acc[sub_id] = acc.get(sub_id, Decimal("0")) + it['cutting_quantity']
        merged = [{'subproduct': Subproduct.objects.get(pk=sid), 'cutting_quantity': qty} for sid, qty in acc.items()]
        return merged

    @staticmethod
    def _validate_items_vs_product_and_stock(
        *,
        product: Product,
        items: List[Dict[str, Any]],
        quantity_to_cut: Decimal,
        exclude_order_id: Optional[int] = None
    ) -> None:
        """
        Regla dura:
        - Todos los subproductos deben pertenecer a 'product'.
        - Suma de cantidades <= quantity_to_cut.
        - Para cada subproducto: cutting_quantity_total <= available(subproduct).
        """
        if product is None or not isinstance(product, Product):
            raise ValidationError("Producto requerido.")

        # 1) Pertenencia: subproduct.parent_id == product.id
        total_sum = Decimal("0")
        for it in items:
            sub = it['subproduct']
            qty = it['cutting_quantity']
            if sub.parent_id != product.id:
                raise ValidationError(f"El subproducto {sub.id} no pertenece al producto indicado.")
            total_sum += qty

        # 2) Suma de items <= objetivo
        if total_sum > quantity_to_cut:
            raise ValidationError(f"La suma de cantidades ({total_sum}) excede la cantidad a cortar ({quantity_to_cut}).")

        # 3) Disponibilidad por subproducto (considerando reservas lógicas)
        # Re-merge para sumar por subproducto (por si vinieron duplicados)
        merged = CuttingOrderRepository._merge_duplicate_items(items)
        for it in merged:
            sub = it['subproduct']
            qty_needed = it['cutting_quantity']
            available = CuttingOrderRepository._available(sub, exclude_order_id=exclude_order_id)
            if qty_needed > available:
                raise ValidationError(
                    f"Stock insuficiente para el subproducto ID {sub.id}. "
                    f"Necesita {qty_needed}, disponible {available} (considerando reservas)."
                )

    @staticmethod
    def _validate_transition(current: str, target: str) -> None:
        """Transiciones permitidas del workflow."""
        if current == target:
            return
        allowed = {
            ('pending', 'in_process'),
            ('in_process', 'completed'),
            ('pending', 'cancelled'),
            ('in_process', 'cancelled'),
        }
        if (current, target) not in allowed:
            raise ValidationError(
                f"Transición inválida: {current} → {target}. "
                f"Permitidas: pending→in_process, in_process→completed, "
                f"pending→cancelled, in_process→cancelled."
            )

    @staticmethod
    def _ensure_order_number_unique(order_number: int, exclude_order_id: Optional[int] = None) -> None:
        qs = CuttingOrder.objects.filter(order_number=order_number)
        if exclude_order_id:
            qs = qs.exclude(pk=exclude_order_id)
        if qs.exists():
            raise ValidationError("Ya existe una orden con ese número.")

    @staticmethod
    def _validate_create_input(
        *,
        order_number: int,
        customer: str,
        product: Product,
        user_creator: User,
        quantity_to_cut: Decimal,
        operator_can_edit_items: bool,
        items: List[Dict[str, Any]]
    ) -> None:
        if not order_number:
            raise ValidationError("Número de pedido requerido.")
        CuttingOrderRepository._ensure_order_number_unique(order_number)

        if not customer:
            raise ValidationError("Cliente requerido.")
        if not product or not isinstance(product, Product):
            raise ValidationError("Producto requerido.")
        if not user_creator or not getattr(user_creator, 'is_authenticated', False):
            raise ValidationError("Usuario creador inválido.")

        try:
            qty = Decimal(str(quantity_to_cut))
        except (InvalidOperation, TypeError):
            raise ValidationError("Cantidad a cortar inválida.")
        if qty <= 0:
            raise ValidationError("La cantidad a cortar debe ser mayor a cero.")

        # Si no se permite edición por operario, deben venir ítems no vacíos
        if not operator_can_edit_items and len(items) == 0:
            raise ValidationError("Debe incluir al menos un item de corte.")

    # -----------------------
    # Escrituras (CUD)
    # -----------------------

    @staticmethod
    @transaction.atomic
    def create(
        *,
        order_number: int,
        customer: str,
        product: Product,
        quantity_to_cut: Decimal,
        items: List[Dict[str, Any]],
        user_creator: User,
        assigned_to: Optional[User] = None,
        workflow_status: str = 'pending',
        operator_can_edit_items: bool = False
    ) -> CuttingOrder:
        """
        Crea la orden:
        - valida inputs y reglas duras,
        - normaliza items,
        - crea la orden + bulk de items (mergeando duplicados),
        - NO toca stock físico aquí (si reservás stock, delega a un servicio).
        """
        # 1) Normalizar y validar inputs básicos
        norm_items = CuttingOrderRepository._coerce_items(items)
        CuttingOrderRepository._validate_create_input(
            order_number=order_number,
            customer=customer,
            product=product,
            user_creator=user_creator,
            quantity_to_cut=quantity_to_cut,
            operator_can_edit_items=operator_can_edit_items,
            items=norm_items
        )

        # 2) Si vinieron ítems, validar vs producto, quantity_to_cut y disponibilidad
        if norm_items:
            CuttingOrderRepository._validate_items_vs_product_and_stock(
                product=product,
                items=norm_items,
                quantity_to_cut=Decimal(str(quantity_to_cut)),
                exclude_order_id=None
            )

        # 3) Crear orden
        order = CuttingOrder(
            order_number=order_number,
            customer=customer,
            product=product,
            quantity_to_cut=Decimal(str(quantity_to_cut)),
            operator_can_edit_items=operator_can_edit_items,
            assigned_to=assigned_to,
            workflow_status=workflow_status
        )
        order.save(user=user_creator)

        # 4) Crear items (mergeando duplicados)
        if norm_items:
            merged = CuttingOrderRepository._merge_duplicate_items(norm_items)
            CuttingOrderItem.objects.bulk_create([
                CuttingOrderItem(
                    order=order,
                    subproduct=it['subproduct'],
                    cutting_quantity=it['cutting_quantity']
                ) for it in merged
            ])

        return (
            CuttingOrder.objects
            .select_related('assigned_to', 'created_by', 'product')
            .prefetch_related(
                Prefetch(
                    'items',
                    queryset=CuttingOrderItem.objects.select_related('subproduct', 'subproduct__parent')
                )
            )
            .get(pk=order.pk)
        )

    @staticmethod
    @transaction.atomic
    def update(
        *,
        order_instance: CuttingOrder,
        user_modifier: User,
        data: Dict[str, Any],
        items: Optional[List[Dict[str, Any]]] = None
    ) -> CuttingOrder:
        """
        Update seguro:
        - Puede cambiar: customer, workflow_status, assigned_to, product, operator_can_edit_items, quantity_to_cut.
        - order_number: por defecto NO permitimos cambiarlo (más simple y seguro).
          Si quisieras permitirlo, valida unicidad con _ensure_order_number_unique().
        - Si cambian product o quantity_to_cut, o si llegan nuevos items:
          valida coherencia, suma y disponibilidad (excluyendo esta orden).
        - Si pasa a completed, setea completed_at.
        """
        if not isinstance(order_instance, CuttingOrder):
            raise ValidationError("Instancia inválida de orden.")
        if not user_modifier or not getattr(user_modifier, 'is_authenticated', False):
            raise ValidationError("Usuario modificador inválido.")

        # Releer con bloqueo para update seguro (bloquea solo la tabla base)
        order = (
            CuttingOrder.objects
            .select_for_update()
            .get(pk=order_instance.pk)
        )
        # Si necesitas los relacionados, accede después:
        # order.product, order.assigned_to

        # Prohibir cambio de order_number (simple). Si quieres permitir, descomenta y valida unicidad.
        if 'order_number' in data and data['order_number'] != order.order_number:
            raise ValidationError("No se permite modificar el número de pedido de una orden existente.")

        # Campos actualizables
        updatable_fields = {'customer', 'workflow_status', 'assigned_to', 'product', 'operator_can_edit_items', 'quantity_to_cut'}
        changed = False
        for field, value in data.items():
            if field in updatable_fields and getattr(order, field) != value:
                setattr(order, field, value)
                changed = True

        # Preparar validaciones según nuevos valores (o actuales si no cambiaron)
        new_product = order.product
        new_qty_to_cut = Decimal(str(order.quantity_to_cut))

        # Normalizar items nuevos (si vienen)
        norm_items = None
        if items is not None:
            norm_items = CuttingOrderRepository._coerce_items(items)

        # Si no se permite edición por operario:
        if not order.operator_can_edit_items:
            if items is not None and len(norm_items) == 0:
                raise ValidationError("Debe incluir al menos un item de corte.")
            if items is None and order.items.count() == 0:
                raise ValidationError("Debe incluir al menos un item de corte.")

        # Validar coherencia y disponibilidad
        if norm_items is not None and len(norm_items) > 0:
            CuttingOrderRepository._validate_items_vs_product_and_stock(
                product=new_product,
                items=norm_items,
                quantity_to_cut=new_qty_to_cut,
                exclude_order_id=order.id
            )
        else:
            if ('product' in data or 'quantity_to_cut' in data) and order.items.exists():
                current_items = [
                    {'subproduct': it.subproduct, 'cutting_quantity': it.cutting_quantity}
                    for it in order.items.select_related('subproduct')
                ]
                CuttingOrderRepository._validate_items_vs_product_and_stock(
                    product=new_product,
                    items=current_items,
                    quantity_to_cut=new_qty_to_cut,
                    exclude_order_id=order.id
                )

        # Transición de workflow (si se solicitó)
        if 'workflow_status' in data:
            CuttingOrderRepository._validate_transition(order_instance.workflow_status, data['workflow_status'])

        # Persistir cambios de cabecera
        if changed:
            order.save(user=user_modifier)

        # Reemplazo completo de items si vino la clave 'items'
        if items is not None:
            order.items.all().delete()
            if len(norm_items) > 0:
                merged = CuttingOrderRepository._merge_duplicate_items(norm_items)
                CuttingOrderItem.objects.bulk_create([
                    CuttingOrderItem(
                        order=order,
                        subproduct=it['subproduct'],
                        cutting_quantity=it['cutting_quantity']
                    ) for it in merged
                ])

        # completed_at al pasar a completed
        if 'workflow_status' in data and data['workflow_status'] == 'completed' and not order.completed_at:
            order.completed_at = timezone.now()
            order.save(update_fields=['completed_at'])

        return (
            CuttingOrder.objects
            .select_related('assigned_to', 'created_by', 'product')
            .prefetch_related(
                Prefetch(
                    'items',
                    queryset=CuttingOrderItem.objects.select_related('subproduct', 'subproduct__parent')
                )
            )
            .get(pk=order.pk)
        )

    @staticmethod
    def soft_delete(order_instance: CuttingOrder, user_deletor: User) -> CuttingOrder:
        if not isinstance(order_instance, CuttingOrder):
            raise ValidationError("Instancia inválida de orden.")
        if not user_deletor or not getattr(user_deletor, 'is_authenticated', False):
            raise ValidationError("Usuario eliminador inválido.")
        order_instance.delete(user=user_deletor)
        return order_instance
