# apps/stocks/models/stock_event_model.py
from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.db.models import Q
from apps.products.models.base_model import BaseModel
from apps.stocks.models.stock_product_model import ProductStock
from apps.stocks.models.stock_subproduct_model import SubproductStock

class StockEvent(BaseModel):
    """Registra cada movimiento (entrada/salida/ajuste) de stock."""

    EVENT_TYPES = [
        ('ingreso_inicial', 'Ingreso Inicial'),
        ('ingreso', 'Ingreso'),
        ('egreso_venta', 'Egreso por Venta'),
        ('egreso_corte', 'Egreso por Corte'),
        ('egreso_ajuste', 'Egreso por Ajuste'),
        ('ingreso_ajuste', 'Ingreso por Ajuste'),
        ('traslado_salida', 'Salida por Traslado'),
        ('traslado_entrada', 'Entrada por Traslado'),
    ]

    product_stock = models.ForeignKey(
        ProductStock,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='events',
        verbose_name="Stock de Producto Afectado"
    )
    subproduct_stock = models.ForeignKey(
        SubproductStock,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='events',
        verbose_name="Stock de Subproducto Afectado"
    )

    quantity_change = models.DecimalField(
        max_digits=15, decimal_places=2,
        help_text="Cambio en la cantidad (+ entrada, - salida)"
    )
    event_type = models.CharField(
        max_length=50, choices=EVENT_TYPES, help_text="Tipo de evento de stock"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="Notas Adicionales")

    class Meta:
        verbose_name = "Evento de Stock"
        verbose_name_plural = "Eventos de Stock"
        ordering = ['-created_at']
        constraints = [
            # exactamente uno de los targets distinto de NULL
            models.CheckConstraint(
                name="stockevent_exactly_one_target",
                check=(
                    (Q(product_stock__isnull=False) & Q(subproduct_stock__isnull=True)) |
                    (Q(product_stock__isnull=True) & Q(subproduct_stock__isnull=False))
                ),
            ),
        ]

    def __str__(self):
        target = self.product_stock or self.subproduct_stock or "Stock Desconocido"
        op = "+" if self.quantity_change > 0 else ""
        return f"{self.get_event_type_display()}: {op}{self.quantity_change} para {target}"

    def clean(self):
        super().clean()
        # ya tenemos constraint, pero mantenemos validación clara en Python
        if bool(self.product_stock) == bool(self.subproduct_stock):
            raise ValidationError("Asigna SOLO product_stock o SOLO subproduct_stock.")
        if self.quantity_change == 0:
            raise ValidationError("La cantidad de cambio no puede ser cero.")

    def apply_to_target(self):
        """Aplica quantity_change al target correspondiente y sincroniza status."""
        if self.product_stock:
            ps = self.product_stock
            ps.quantity = (ps.quantity or Decimal('0')) + self.quantity_change
            if ps.quantity < 0:
                ps.quantity = Decimal('0')
            ps.save(update_fields=['quantity', 'modified_at', 'modified_by'])
            return

        ss: SubproductStock = self.subproduct_stock
        ss.quantity = (ss.quantity or Decimal('0')) + self.quantity_change
        if ss.quantity < 0:
            ss.quantity = Decimal('0')
        ss.save(update_fields=['quantity', 'modified_at', 'modified_by'])

        # 🔧 Sincronizar status del Subproduct (Disponible si > 0), usar instancia directamente
        import logging
        logger = logging.getLogger(__name__)
        sp = ss.subproduct
        new_status = ss.quantity > 0
        if sp.status != new_status:
            sp.status = new_status
            sp.save(update_fields=['status', 'modified_at', 'modified_by'])
            logger.debug(f"StockEvent.apply_to_target: Subproduct {sp.pk} -> status={new_status} by qty={ss.quantity}")

    def save(self, *args, **kwargs):
        # Aplica el cambio SOLO al crear el evento (evita re-aplicar en updates)
        is_create = self.pk is None
        with transaction.atomic():
            super().save(*args, **kwargs)
            if is_create:
                self.apply_to_target()
