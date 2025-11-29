from decimal import Decimal

from django.db import models
from django.utils import timezone

from apps.billing.models import BillingDocument
from apps.products.models.base_model import BaseModel


class AccountingEntryStatus(models.TextChoices):
    PENDING = "pending", "Pendiente"
    POSTED = "posted", "Registrado"
    REVERSED = "reversed", "Revertido"


class AccountingEntry(BaseModel):
    billing_document = models.OneToOneField(
        BillingDocument,
        on_delete=models.CASCADE,
        related_name="accounting_entry",
    )
    entry_date = models.DateField(default=timezone.now)
    reference = models.CharField(max_length=100, blank=True)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(
        max_length=20,
        choices=AccountingEntryStatus.choices,
        default=AccountingEntryStatus.PENDING,
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Asiento contable"
        verbose_name_plural = "Asientos contables"
        ordering = ["-entry_date", "-created_at"]

    def __str__(self) -> str:
        suffix = self.reference or f"#{self.pk or 'nuevo'}"
        return f"Asiento {suffix} ({self.get_status_display()})"
