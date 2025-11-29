from decimal import Decimal

from django.db import models

from apps.products.models.base_model import BaseModel


class BillingLine(BaseModel):
    billing_document = models.ForeignKey(
        "billing.BillingDocument",
        on_delete=models.CASCADE,
        related_name="lines",
    )
    product_code = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0.000"))
    unit_price = models.DecimalField(max_digits=18, decimal_places=4, default=Decimal("0.0000"))
    discount_amount = models.DecimalField(max_digits=18, decimal_places=4, default=Decimal("0.0000"))

    class Meta:
        verbose_name = "Línea de documento"
        verbose_name_plural = "Líneas de documento"

    @property
    def line_total(self) -> Decimal:
        gross = self.quantity * self.unit_price
        return gross - self.discount_amount
