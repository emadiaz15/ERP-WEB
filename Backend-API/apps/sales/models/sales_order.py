from django.db import models

from apps.products.models.base_model import BaseModel


class SalesOrder(BaseModel):
    """Pedido de venta proveniente del ERP legacy."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        CONFIRMED = "confirmed", "Confirmado"
        PARTIALLY_SHIPPED = "partially_shipped", "Parcialmente despachado"
        COMPLETED = "completed", "Completado"
        CANCELLED = "cancelled", "Anulado"

    customer_legacy_id = models.IntegerField(verbose_name="ID cliente legacy", db_index=True)
    customer_legacy_name = models.CharField(max_length=255, blank=True, verbose_name="Nombre cliente legacy")
    order_date = models.DateField(verbose_name="Fecha de pedido")
    currency = models.CharField(max_length=3, default="ARS", verbose_name="Moneda")
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=1, verbose_name="Cotización")
    reference = models.CharField(max_length=255, blank=True, verbose_name="Referencia externa")
    notes = models.TextField(blank=True, verbose_name="Observaciones")
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Descuento %")
    transport_legacy_id = models.IntegerField(null=True, blank=True, verbose_name="Transporte legacy")
    iva_condition_id = models.IntegerField(null=True, blank=True, verbose_name="Condición IVA legacy")
    legacy_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="ID legacy")
    status_label = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Estado",
    )

    class Meta:
        verbose_name = "Pedido de venta"
        verbose_name_plural = "Pedidos de venta"
        ordering = ["-order_date", "-id"]

    def __str__(self) -> str:
        return f"SO-{self.id or 'new'} ({self.customer_legacy_id})"
