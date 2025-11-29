from django.db import models

from apps.products.models.base_model import BaseModel
from apps.suppliers.models import Supplier


class PurchaseReceipt(BaseModel):
    """Comprobante de recepción / factura de proveedor."""

    order = models.ForeignKey(
        "purchases.PurchaseOrder",
        on_delete=models.SET_NULL,
        related_name="receipts",
        null=True,
        blank=True,
        verbose_name="Orden vinculada",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="purchase_receipts",
        verbose_name="Proveedor",
    )
    receipt_date = models.DateField(verbose_name="Fecha de recepción")
    invoice_letter = models.CharField(max_length=1, blank=True, verbose_name="Letra factura")
    invoice_pos = models.IntegerField(null=True, blank=True, verbose_name="Punto de venta")
    invoice_number = models.IntegerField(null=True, blank=True, verbose_name="Número factura")
    total_gross = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Neto gravado")
    total_tax = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Impuestos")
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Total")
    currency = models.CharField(max_length=3, default="ARS", verbose_name="Moneda")
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=1, verbose_name="Cotización")
    notes = models.TextField(blank=True, verbose_name="Observaciones")
    legacy_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="ID legacy")

    class Meta:
        verbose_name = "Recepción de compra"
        verbose_name_plural = "Recepciones de compra"
        ordering = ["-receipt_date", "-id"]

    def __str__(self) -> str:
        return f"Recep {self.id or '-'}"
