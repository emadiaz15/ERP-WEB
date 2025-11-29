from django.db import models

from apps.products.models.base_model import BaseModel


class PurchasePaymentAllocation(BaseModel):
    """Distribución de un pago sobre una recepción."""

    payment = models.ForeignKey(
        "purchases.PurchasePayment",
        on_delete=models.CASCADE,
        related_name="allocations",
        verbose_name="Pago",
    )
    receipt = models.ForeignKey(
        "purchases.PurchaseReceipt",
        on_delete=models.CASCADE,
        related_name="payment_allocations",
        verbose_name="Recepción",
    )
    allocated_amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Importe imputado")
    is_partial = models.BooleanField(default=False, verbose_name="Pago parcial")

    class Meta:
        verbose_name = "Imputación de pago"
        verbose_name_plural = "Imputaciones de pago"
        unique_together = ("payment", "receipt")

    def __str__(self) -> str:
        return f"Pago {self.payment_id} → Recep {self.receipt_id}"
