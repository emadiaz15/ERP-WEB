from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.stocks.models import ProductStock, StockEvent
from apps.stocks.utils.cache_utils import invalidate_product_events
from apps.stocks.services.common import decimal_or_zero

@transaction.atomic
def initialize_product_stock(
    product,
    user,
    initial_quantity: Decimal = Decimal("0.00"),
    reason: str = "Stock Inicial por Creación",
):
    if not getattr(product, "pk", None):
        raise ValueError("Se requiere una instancia de Producto válida y guardada.")
    try:
        initial_quantity = Decimal(initial_quantity)
        if initial_quantity < 0:
            raise ValidationError("La cantidad inicial no puede ser negativa.")
    except (InvalidOperation, TypeError):
        raise ValidationError("La cantidad inicial debe ser un número válido.")

    if ProductStock.objects.filter(product=product).exists():
        raise ValueError(f"Ya existe stock para '{product.name}'. Use ajuste de stock.")

    stock_instance = ProductStock(product=product, quantity=Decimal("0.00"))
    stock_instance.save(user=user)

    if initial_quantity > 0:
        StockEvent.objects.create(
            product_stock=stock_instance,
            subproduct_stock=None,
            quantity_change=initial_quantity,
            event_type="ingreso_inicial",
            created_by=user,
            notes=reason,
        )
        # ⬇️ invalidar caché solo cuando el commit se confirme
        prod_id = product.id
        transaction.on_commit(lambda: invalidate_product_events(prod_id))

    return stock_instance


@transaction.atomic
def adjust_product_stock(product_stock: ProductStock, quantity_change: Decimal, reason: str, user):
    if not getattr(product_stock, "pk", None):
        raise ValueError("Se requiere una instancia de ProductStock válida.")
    if product_stock.product.has_subproducts:
        raise ValidationError("No se puede ajustar stock del producto padre; ajuste subproductos.")
    try:
        quantity_change = Decimal(str(quantity_change))
        if quantity_change == 0:
            raise ValidationError("La cantidad del ajuste no puede ser cero.")
    except (InvalidOperation, TypeError):
        raise ValidationError("La cantidad del ajuste debe ser un número válido.")

    # 🔒 Bloquear la fila para validaciones consistentes
    ps = ProductStock.objects.select_for_update().get(pk=product_stock.pk, status=True)
    current = decimal_or_zero(ps.quantity)
    if (current + quantity_change) < 0:
        raise ValidationError(
            f"Ajuste inválido. Stock resultante negativo para '{ps.product.name}'. Disponible: {current}"
        )

    # Crear el evento (aplicará el cambio en save/apply_to_target)
    event = StockEvent.objects.create(
        product_stock=ps,
        subproduct_stock=None,
        quantity_change=quantity_change,
        event_type="ingreso_ajuste" if quantity_change > 0 else "egreso_ajuste",
        created_by=user,
        notes=reason,
    )

    # ⬇️ invalidar caché solo cuando el commit se confirme
    prod_id = ps.product_id
    transaction.on_commit(lambda: invalidate_product_events(prod_id))

    return event
