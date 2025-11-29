# apps/cuts/services/cuts_services.py
from django.db import models, transaction, IntegrityError
from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils import timezone
from decimal import Decimal, InvalidOperation
import logging
from typing import List, Dict, Optional, Tuple

# Models
from apps.cuts.models.cutting_order_model import CuttingOrder, CuttingOrderItem
from apps.cuts.api.repositories.cutting_order_repository import CuttingOrderRepository
from apps.users.models.user_model import User
from apps.products.models.subproduct_model import Subproduct
from apps.products.models.product_model import Product
from apps.stocks.models import SubproductStock, StockEvent
from apps.stocks.services import (
    ensure_subproduct_status_from_stock,
    sync_parent_product_stock,
)

logger = logging.getLogger(__name__)


# ------------------ Utilidades decimales / stock lógicos ------------------

def _dec(x) -> Decimal:
    """Convierte a Decimal de forma segura."""
    try:
        return Decimal(str(x))
    except Exception:
        return Decimal("0")


def _reserved_qty_for_subproduct(subproduct_id: int, exclude_order_id: Optional[int] = None) -> Decimal:
    """
    Suma de cantidades reservadas (órdenes activas) para un subproducto.
    Considera órdenes con estado 'pending' o 'in_process'.
    """
    qs = CuttingOrderItem.objects.filter(
        subproduct_id=subproduct_id,
        order__status=True,
        order__workflow_status__in=['pending', 'in_process'],
    )
    if exclude_order_id:
        qs = qs.exclude(order_id=exclude_order_id)
    total = qs.aggregate(total=models.Sum('cutting_quantity'))['total'] or Decimal("0")
    return _dec(total)


def _available_considering_reservations(subproduct: Subproduct, exclude_order_id: Optional[int] = None) -> Decimal:
    """
    available = stock_fisico - reservas_lógicas (otras órdenes activas).
    ⚠️ Cambia 'ss.quantity' por 'ss.current_stock' si tu modelo lo usa.
    """
    try:
        ss = SubproductStock.objects.get(subproduct=subproduct, status=True)
        base_qty = _dec(ss.quantity)  # ⚠️ cambiar a ss.current_stock si corresponde
    except SubproductStock.DoesNotExist:
        base_qty = Decimal("0")
    reserved = _reserved_qty_for_subproduct(subproduct.id, exclude_order_id=exclude_order_id)
    return base_qty - reserved


def active_reservations_summary_for_order(order: CuttingOrder) -> List[Dict]:
    """
    Devuelve, por cada ítem de la orden, si hay reservas activas (de otras órdenes)
    del mismo subproducto. Útil para warnings en frontend.
    """
    if not isinstance(order, CuttingOrder) or not order.pk:
        return []

    results: List[Dict] = []
    for it in order.items.select_related("subproduct"):
        sub = it.subproduct
        other_reserved = _reserved_qty_for_subproduct(sub.id, exclude_order_id=order.id)
        other_orders_count = (
            CuttingOrderItem.objects
            .filter(
                subproduct_id=sub.id,
                order__status=True,
                order__workflow_status__in=['pending', 'in_process'],
            )
            .exclude(order_id=order.id)
            .values("order_id").distinct().count()
        )
        available = _available_considering_reservations(sub, exclude_order_id=order.id)
        if other_orders_count > 0 and other_reserved > 0:
            results.append({
                "subproduct_id": sub.id,
                "subproduct_str": str(sub),
                "other_active_orders_count": other_orders_count,
                "other_reserved_qty": _dec(other_reserved),
                "available_excluding_others": _dec(available),
            })
    return results


# ------------------ Normalización / Validación de items ------------------

def _coerce_item(raw: Dict) -> Tuple[Subproduct, Decimal]:
    """
    Acepta {'subproduct': <id|Subproduct>, 'cutting_quantity': <num>} o
           {'subproduct_id': <id>,        'cutting_quantity': <num>}
    y devuelve (Subproduct, Decimal).
    """
    sub_id_or_obj = raw.get('subproduct', raw.get('subproduct_id'))
    if isinstance(sub_id_or_obj, Subproduct):
        sub = sub_id_or_obj
    else:
        sub = get_object_or_404(Subproduct, pk=sub_id_or_obj, status=True)

    try:
        qty = _dec(raw['cutting_quantity'])
        if qty <= 0:
            raise InvalidOperation
    except (KeyError, InvalidOperation, ValueError):
        raise ValidationError(f"Cantidad inválida para subproducto {getattr(sub, 'id', '?')}.")

    return sub, qty


def _normalize_items(items: List[Dict]) -> List[Tuple[Subproduct, Decimal]]:
    """Coacciona todos los items a (Subproduct, Decimal)."""
    return [_coerce_item(it) for it in (items or [])]


def _merge_items(items: List[Tuple[Subproduct, Decimal]]) -> List[Tuple[Subproduct, Decimal]]:
    """
    Mergea ítems de un mismo subproducto sumando cantidades,
    para no violar UniqueConstraint(order, subproduct).
    """
    acc: Dict[int, Decimal] = {}
    cache: Dict[int, Subproduct] = {}
    for sub, qty in items:
        acc[sub.id] = acc.get(sub.id, Decimal("0")) + qty
        cache[sub.id] = sub
    return [(cache[sid], q) for sid, q in acc.items()]


# ------------------ Crear (reserva lógica, sin tocar stock real) ------------------

@transaction.atomic
def create_full_cutting_order(
    *,
    product_id: int,
    quantity_to_cut: str | Decimal,
    items: List[Dict],
    customer: str,
    user_creator: User,
    assigned_to_id: Optional[int] = None,
    order_number: Optional[int] = None,
    operator_can_edit_items: bool = False
) -> CuttingOrder:
    """
    Crea la orden en 'pending' y valida:
    - order_number único
    - product activo (y que admita subproductos)
    - quantity_to_cut > 0
    - si operator_can_edit_items=False ⇒ items requeridos
    - pertenencia subproductos ↔ product
    - suma(items) ≤ quantity_to_cut
    - disponibilidad por subproducto (stock - reservas)
    NO descuenta stock real; el descuento ocurre en 'completed'.
    """

    # Permisos
    if not user_creator.is_staff:
        raise PermissionDenied("Solo usuarios Staff pueden crear órdenes de corte.")

    # Validaciones simples
    if not customer:
        raise ValidationError("El cliente es obligatorio.")
    if order_number is None:
        raise ValidationError("El número de pedido (order_number) es obligatorio.")

    # Unicidad "optimista" antes de insertar (y la DB refuerza con UNIQUE)
    if CuttingOrder.objects.filter(order_number=order_number).exists():
        raise ValidationError("Ya existe una orden con ese número.")

    # Producto
    product = get_object_or_404(Product, pk=product_id, status=True)
    if getattr(product, "has_subproducts", False) is False:
        raise ValidationError("El producto no permite subproductos.")

    # Cantidad objetivo total
    try:
        qty_to_cut = _dec(quantity_to_cut)
    except Exception:
        raise ValidationError("Cantidad a cortar inválida.")
    if qty_to_cut <= 0:
        raise ValidationError("La cantidad a cortar debe ser mayor a cero.")

    # Items: normalizar/mergear y validar reglas duras
    norm = _normalize_items(items)
    merged = _merge_items(norm)

    if not operator_can_edit_items and len(merged) == 0:
        raise ValidationError("Debe incluir al menos un item de corte.")

    # Pertenencia + suma ≤ objetivo + disponibilidad por subproducto
    total_sum = Decimal("0")
    for sub, qty in merged:
        if sub.parent_id != product.id:
            raise ValidationError(f"El subproducto {sub.pk} no pertenece al producto indicado.")
        total_sum += qty
    if total_sum > qty_to_cut:
        raise ValidationError(f"La suma de cantidades ({total_sum}) excede la cantidad a cortar ({qty_to_cut}).")

    for sub, qty in merged:
        available = _available_considering_reservations(sub)
        if qty > available:
            raise ValidationError(
                f"Stock insuficiente para {sub}. Requiere {qty}, disponible {available}."
            )

    # Usuario asignado (opcional)
    assigned_to_user = None
    if assigned_to_id:
        assigned_to_user = get_object_or_404(User, pk=assigned_to_id, is_active=True)

    # Crear cabecera
    try:
        order = CuttingOrder.objects.create(
            order_number=order_number,
            customer=customer,
            product=product,
            quantity_to_cut=qty_to_cut,              # ← NUEVO: se persiste el objetivo total
            operator_can_edit_items=operator_can_edit_items,
            created_by=user_creator,
            assigned_to=assigned_to_user,
            workflow_status='pending',
        )
    except IntegrityError:
        # Carrera contra UNIQUE(order_number)
        raise ValidationError("Ya existe una orden con ese número.")

    # Crear líneas
    if merged:
        CuttingOrderItem.objects.bulk_create([
            CuttingOrderItem(order=order, subproduct=sub, cutting_quantity=qty)
            for sub, qty in merged
        ])

    # Devolver con relaciones resueltas
    return (
        CuttingOrder.objects
        .select_related('assigned_to', 'created_by', 'product')
        .prefetch_related('items__subproduct')
        .get(pk=order.pk)
    )


# ------------------ Asignar ------------------

@transaction.atomic
def assign_order_to_operator(order_id: int, operator_id: int, user_assigning: User) -> CuttingOrder:
    """Staff asigna una orden 'pending' a un operador."""
    if not user_assigning.is_staff:
        raise PermissionDenied("Solo usuarios Staff pueden asignar órdenes.")

    order = CuttingOrderRepository.get_by_id(order_id)
    if not order:
        raise ValidationError(f"Orden de corte ID {order_id} no encontrada o inactiva.")
    if order.workflow_status != 'pending':
        raise ValidationError(f"La orden no se puede asignar en estado '{order.get_workflow_status_display()}'.")

    operator = get_object_or_404(User, pk=operator_id, is_active=True)

    return CuttingOrderRepository.update(
        order_instance=order,
        user_modifier=user_assigning,
        data={'assigned_to': operator}
    )


# ------------------ Completar (descuenta y crea eventos) ------------------

@transaction.atomic
def complete_order_processing(order_id: int, user_completing: User) -> CuttingOrder:
    """
    Cambia a 'completed' y realiza el descuento real de stock + eventos por ítem.
    Requiere que la orden esté 'in_process' y que el usuario sea staff o el asignado.
    """
    order = CuttingOrderRepository.get_by_id(order_id)
    if not order:
        raise ValidationError(f"Orden de corte ID {order_id} no encontrada o inactiva.")

    if not user_completing.is_staff and order.assigned_to != user_completing:
        raise PermissionDenied("No tienes permiso para completar esta orden.")

    return complete_cutting_logic(order, user_completing)


@transaction.atomic
def complete_cutting_logic(order: CuttingOrder, user_completing: User) -> CuttingOrder:
    """Descuenta stock real y registra StockEvent por cada ítem; luego marca completed."""
    if order.workflow_status != 'in_process':
        raise ValidationError("Debe estar en 'En Proceso' para completarse.")

    if not user_completing or not user_completing.is_authenticated:
        raise ValidationError("Usuario inválido.")

    # Seguridad adicional: la suma de ítems no puede exceder el objetivo
    total_items = order.items.aggregate(t=models.Sum('cutting_quantity'))['t'] or Decimal("0")
    if total_items > (order.quantity_to_cut or Decimal("0")):
        raise ValidationError(
            f"La suma de ítems ({total_items}) excede la cantidad a cortar ({order.quantity_to_cut})."
        )

    # Descontar stock real por ítem con bloqueo
    for item in order.items.select_for_update():
        try:
            ss = SubproductStock.objects.select_for_update().get(subproduct=item.subproduct, status=True)
        except SubproductStock.DoesNotExist:
            raise ValidationError(f"No hay stock activo para {item.subproduct}.")

        # ⚠️ Cambia ss.quantity si tu campo real es current_stock
        if item.cutting_quantity > _dec(ss.quantity):
            raise ValidationError(
                f"Stock insuficiente al completar para {item.subproduct}. "
                f"Requiere {item.cutting_quantity}, disponible {ss.quantity}."
            )

        ss.quantity = _dec(ss.quantity) - _dec(item.cutting_quantity)   # ⚠️ idem
        ss.save(user=user_completing)

        # Evento de egreso por corte
        StockEvent.objects.create(
            product_stock=None,
            subproduct_stock=ss,
            quantity_change=-_dec(item.cutting_quantity),
            event_type="egreso_corte",
            created_by=user_completing,
            notes=f"Egreso por Orden de Corte #{order.pk}",
            status=True,
        )

        # Sincronizaciones (estado del subproducto + stock del padre)
        ensure_subproduct_status_from_stock(ss.subproduct, acting_user=user_completing)
        sync_parent_product_stock(ss.subproduct.parent, acting_user=user_completing)

    # Marcar completada
    order.workflow_status = 'completed'
    order.completed_at = timezone.now()
    order.save(
        user=user_completing,
        update_fields=['workflow_status', 'completed_at', 'modified_at', 'modified_by']
    )
    return order


# ------------------ Cancelar (libera reservas lógicas) ------------------

@transaction.atomic
def cancel_cutting_order(order_id: int, admin_user: User) -> CuttingOrder:
    """
    Cancela una orden 'pending' o 'in_process'.
    Con reservas lógicas, no hay que reponer stock real (no se descontó aún).
    """
    if not admin_user or not getattr(admin_user, "is_staff", False):
        raise PermissionDenied("Solo staff puede cancelar órdenes de corte.")

    order = CuttingOrderRepository.get_by_id(order_id)
    if not order:
        raise ValidationError(f"Orden de corte ID {order_id} no encontrada o inactiva.")

    if order.workflow_status not in ("pending", "in_process"):
        raise ValidationError(f"No se puede cancelar una orden en estado '{order.get_workflow_status_display()}'.")

    order.workflow_status = "cancelled"
    order.save(user=admin_user, update_fields=["workflow_status", "modified_at", "modified_by"])
    logger.info("Orden de corte %s cancelada por %s.", order.pk, admin_user)
    return order
