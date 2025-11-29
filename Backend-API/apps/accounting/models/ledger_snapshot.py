from decimal import Decimal

from django.db import models
from django.utils import timezone

from apps.products.models.base_model import BaseModel


class LedgerSnapshot(BaseModel):
    period = models.CharField(max_length=10)
    account_code = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    generated_on = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Snapshot contable"
        verbose_name_plural = "Snapshots contables"
        unique_together = ("period", "account_code")
