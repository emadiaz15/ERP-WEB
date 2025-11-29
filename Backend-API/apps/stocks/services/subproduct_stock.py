# apps/stocks/services/subproduct_stock.py

from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.stocks.models import SubproductStock, StockEvent
from apps.stocks.utils.cache_utils import invalidate_subproduct_events
from apps.stocks.services.common import decimal_or_zero
from apps.stocks.services.status import ensure_subproduct_status_from_stock
from apps.stocks.services.sync import sync_parent_product_stock
from apps.stocks.services.reservations import reserved_qty


@transaction.atomic
def initialize_subproduct_stock(
    subproduct,
    user,
    initial_quantity: Decimal = Decimal("0.00"),
    reason: str = "Stock Inicial por Creación",
):
    """
    Crea (si no existe) el SubproductStock en 0.00 y registra UN SOLO evento 'ingreso_inicial'.
    - No modifica la cantidad manualmente: el aumento lo aplica el propio StockEvent.save().
    - Idempotente: si ya hubo 'ingreso_inicial', no vuelve a crearlo.
    """
    if not getattr(subproduct, "pk", None):
        raise ValueError("Se requiere una instancia de Subproducto válida y guardada.")

    # Normalizar cantidad inicial
    try:
        initial_quantity = Decimal(str(initial_quantity or "0"))
        if initial_quantity < 0:
            raise ValidationError("La cantidad inicial no puede ser negativa.")
    except (InvalidOperation, TypeError):
        raise ValidationError("La cantidad inicial debe ser un número válido.")

    # Crear/obtener stock SIEMPRE en 0.00 (evita doble suma)
    stock = (
        SubproductStock.objects.select_for_update()
        .filter(subproduct=subproduct)
        .first()
    )
    if not stock:
        stock = SubproductStock(subproduct=subproduct, quantity=Decimal("0.00"))
        stock.save(user=user)

    # Crear el evento 'ingreso_inicial' solo si corresponde y no existe ya
    import logging
    logger = logging.getLogger(__name__)
    if initial_quantity > 0:
        already_initialized = StockEvent.objects.filter(
            subproduct_stock=stock, event_type="ingreso_inicial", status=True
        ).exists()
        if not already_initialized:
            logger.debug(
                f"initialize_subproduct_stock: Creando StockEvent ingreso_inicial para Subproduct {subproduct.pk} con cantidad {initial_quantity}"
            )
            StockEvent.objects.create(
                product_stock=None,
                subproduct_stock=stock,
                quantity_change=initial_quantity,
                event_type="ingreso_inicial",
                created_by=user,
                notes=reason,
            )
            logger.debug(
                f"initialize_subproduct_stock: StockEvent creado para Subproduct {subproduct.pk}"
            )
            # Invalida cache solo tras commit exitoso
            sub_id = subproduct.id
            transaction.on_commit(lambda: invalidate_subproduct_events(sub_id))

    # Asegurar status del subproducto y espejo del padre
    ensure_subproduct_status_from_stock(subproduct, acting_user=user)
    sync_parent_product_stock(subproduct.parent, acting_user=user)
    return stock


@transaction.atomic
def adjust_subproduct_stock(subproduct_stock: SubproductStock, quantity_change: Decimal, reason: str, user):
    """
    Ajusta stock mediante un StockEvent:
    - Valida que el resultante no sea negativo ni menor que lo reservado.
    - NO modifica manualmente la cantidad; el StockEvent aplica el cambio.
    """
    if not getattr(subproduct_stock, "pk", None):
        raise ValueError("Se requiere una instancia de SubproductStock válida.")

    try:
        quantity_change = Decimal(str(quantity_change))
    except (InvalidOperation, TypeError):
        raise ValidationError("La cantidad del ajuste debe ser un número válido.")
    if quantity_change == 0:
        raise ValidationError("La cantidad del ajuste no puede ser cero.")

    # Bloqueo para evaluar reglas con consistencia
    stock = SubproductStock.objects.select_for_update().get(pk=subproduct_stock.pk, status=True)
    current = decimal_or_zero(stock.quantity)

    # Validaciones de dominio
    if (current + quantity_change) < 0:
        raise ValidationError(
            f"Ajuste inválido. Stock resultante negativo para '{stock.subproduct.name}'. Disponible: {current}"
        )

    rsv = reserved_qty(stock.subproduct_id)
    if (current + quantity_change) < rsv:
        raise ValidationError(f"No se puede ajustar por debajo de lo reservado ({rsv}).")

    # Crear evento (aplicará el cambio en save/apply_to_target)
    event = StockEvent.objects.create(
        product_stock=None,
        subproduct_stock=stock,
        quantity_change=quantity_change,
        event_type="ingreso_ajuste" if quantity_change > 0 else "egreso_ajuste",
        created_by=user,
        notes=reason,
    )

    # Invalida cache solo tras commit exitoso
    sub_id = stock.subproduct_id
    transaction.on_commit(lambda: invalidate_subproduct_events(sub_id))

    ensure_subproduct_status_from_stock(stock.subproduct, acting_user=user)
    sync_parent_product_stock(stock.subproduct.parent, acting_user=user)
    return event


@transaction.atomic
def dispatch_subproduct_stock_for_cut(
    subproduct_stock: SubproductStock,
    quantity_to_dispatch: Decimal,
    user,
    reason: str = "Consumo por corte",
):
    """
    Descuenta stock de un subproducto por un proceso de CORTE y registra el evento 'egreso_corte'.
    - Valida que el stock resultante no sea negativo ni menor que lo reservado.
    - NO modifica manualmente la cantidad; el StockEvent aplica el cambio.
    """
    if not getattr(subproduct_stock, "pk", None):
        raise ValueError("Se requiere una instancia de SubproductStock válida.")

    try:
        qty = Decimal(str(quantity_to_dispatch))
    except (InvalidOperation, TypeError):
        raise ValidationError("La cantidad a despachar debe ser un número válido.")
    if qty <= 0:
        raise ValidationError("La cantidad a despachar debe ser mayor a cero.")

    # Bloquear fila y evaluar reglas
    stock = SubproductStock.objects.select_for_update().get(pk=subproduct_stock.pk, status=True)
    current = decimal_or_zero(stock.quantity)

    if (current - qty) < 0:
        raise ValidationError(
            f"Despacho inválido. Stock resultante negativo para '{stock.subproduct.name}'. Disponible: {current}"
        )

    rsv = reserved_qty(stock.subproduct_id)
    if (current - qty) < rsv:
        raise ValidationError(
            f"No se puede despachar por debajo de lo reservado ({rsv}). Disponible: {current}"
        )

    # Crear evento de egreso por corte (aplicará el cambio en save/apply_to_target)
    event = StockEvent.objects.create(
        product_stock=None,
        subproduct_stock=stock,
        quantity_change=(Decimal("-1") * qty),
        event_type="egreso_corte",
        created_by=user,
        notes=reason,
    )

    # Invalida cache solo tras commit exitoso
    sub_id = stock.subproduct_id
    transaction.on_commit(lambda: invalidate_subproduct_events(sub_id))

    ensure_subproduct_status_from_stock(stock.subproduct, acting_user=user)
    sync_parent_product_stock(stock.subproduct.parent, acting_user=user)
    return event
