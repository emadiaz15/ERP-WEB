from django.db import models

from apps.logistics.models import Carrier
from apps.products.models.base_model import BaseModel
from apps.suppliers.models import Supplier


class PurchaseOrder(BaseModel):
    """Orden de compra registrada en el ERP."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        APPROVED = "approved", "Aprobada"
        RECEIVED = "received", "Recibida"
        CANCELLED = "cancelled", "Anulada"

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="purchase_orders",
        verbose_name="Proveedor",
    )
    order_date = models.DateField(verbose_name="Fecha de orden")
    currency = models.CharField(max_length=3, default="ARS", verbose_name="Moneda")
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=1, verbose_name="Cotización")
    reference = models.CharField(max_length=255, blank=True, verbose_name="Referencia externa")
    notes = models.TextField(blank=True, verbose_name="Observaciones")
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Descuento %")
    carrier = models.ForeignKey(
        Carrier,
        on_delete=models.SET_NULL,
        related_name="purchase_orders",
        null=True,
        blank=True,
        verbose_name="Transportista",
    )
    carrier_name_snapshot = models.CharField(max_length=255, blank=True, verbose_name="Transportista snapshot")
    transport_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Transporte legacy",
        help_text="Solo referencia histórica",
    )
    iva_condition_id = models.IntegerField(null=True, blank=True, verbose_name="Condición IVA legacy")
    legacy_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="ID legacy")
    status_label = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Estado",
    )

    class Meta:
        verbose_name = "Orden de compra"
        verbose_name_plural = "Ordenes de compra"
        ordering = ["-order_date", "-id"]

    def __str__(self) -> str:
        return f"OC-{self.id or 'new'} {self.supplier.name}"
