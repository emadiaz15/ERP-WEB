from django.db import models

from apps.products.models.base_model import BaseModel
from apps.suppliers.models import Supplier


class PurchasePayment(BaseModel):
    """Pago a proveedor asociado a recepciones u ordenes."""

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="purchase_payments",
        verbose_name="Proveedor",
    )
    payment_date = models.DateField(verbose_name="Fecha del pago")
    amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Importe")
    currency = models.CharField(max_length=3, default="ARS", verbose_name="Moneda")
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=1, verbose_name="Cotización")
    reference = models.CharField(max_length=255, blank=True, verbose_name="Referencia externa")
    notes = models.TextField(blank=True, verbose_name="Observaciones")
    legacy_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="ID legacy")

    class Meta:
        verbose_name = "Pago a proveedor"
        verbose_name_plural = "Pagos a proveedores"
        ordering = ["-payment_date", "-id"]

    def __str__(self) -> str:
        return f"Pago {self.id or '-'}"
