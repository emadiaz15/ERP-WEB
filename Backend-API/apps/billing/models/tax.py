from decimal import Decimal

from django.db import models

from apps.products.models.base_model import BaseModel


class BillingTax(BaseModel):
    billing_document = models.ForeignKey(
        "billing.BillingDocument",
        on_delete=models.CASCADE,
        related_name="taxes",
    )
    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=6, decimal_places=4, default=Decimal("0.0000"))
    amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name = "Impuesto de facturación"
        verbose_name_plural = "Impuestos de facturación"
