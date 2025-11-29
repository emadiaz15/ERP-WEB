from decimal import Decimal

from django.db import models

from apps.products.models.base_model import BaseModel


class AccountingEntryLine(BaseModel):
    entry = models.ForeignKey(
        "accounting.AccountingEntry",
        on_delete=models.CASCADE,
        related_name="lines",
    )
    account_code = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    debit = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    credit = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name = "Línea contable"
        verbose_name_plural = "Líneas contables"
