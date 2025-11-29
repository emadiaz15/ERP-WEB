from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from apps.customers.models.customer import Customer
from apps.products.models.base_model import BaseModel
from apps.financial.choices import (
    CurrencyChoices,
    LedgerEntryKind,
    LedgerEntrySource,
)


class ReceivableLedgerEntry(BaseModel):
    """Movimiento de cuenta corriente del cliente."""

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="ledger_entries",
        verbose_name="Cliente",
    )
    customer_name_snapshot = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Snapshot cliente",
    )
    entry_kind = models.CharField(
        max_length=20,
        choices=LedgerEntryKind.choices,
        verbose_name="Tipo movimiento",
    )
    entry_source = models.CharField(
        max_length=20,
        choices=LedgerEntrySource.choices,
        verbose_name="Origen",
    )
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.ARS,
        verbose_name="Moneda",
    )
    posted_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha imputación",
    )
    description = models.CharField(max_length=255, blank=True)
    reference_number = models.CharField(max_length=120, blank=True)

    document_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    document_object_id = models.PositiveIntegerField(null=True, blank=True)
    document = GenericForeignKey("document_content_type", "document_object_id")

    treasury_payment = models.ForeignKey(
        "treasury.OutgoingPayment",
        on_delete=models.SET_NULL,
        related_name="receivable_entries",
        null=True,
        blank=True,
        verbose_name="Recibo/Pago",
    )

    debit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    balance_after = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    extra_data = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Movimiento Cta Cte"
        verbose_name_plural = "Movimientos Cta Cte"
        ordering = ["-posted_at", "-id"]
        indexes = [
            models.Index(fields=["customer", "posted_at"]),
            models.Index(fields=["currency"]),
        ]


class CustomerStatement(BaseModel):
    """Snapshot periódico de saldos por cliente y moneda."""

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="statements",
        verbose_name="Cliente",
    )
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.ARS,
        verbose_name="Moneda",
    )
    period_start = models.DateField()
    period_end = models.DateField()
    opening_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    debit_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    credit_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    last_entry_at = models.DateTimeField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Estado de cuenta"
        verbose_name_plural = "Estados de cuenta"
        unique_together = ("customer", "currency", "period_start", "period_end")
        ordering = ["-period_end", "customer"]
