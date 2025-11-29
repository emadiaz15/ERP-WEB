from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from apps.products.models.base_model import BaseModel
from apps.suppliers.models import Supplier
from apps.payables.choices import LedgerEntryKind, LedgerEntrySource
from apps.financial.choices import CurrencyChoices


class SupplierLedgerEntry(BaseModel):
    """Movimiento de cuentas por pagar por proveedor."""

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="ledger_entries",
        verbose_name="Proveedor",
    )
    supplier_name_snapshot = models.CharField(max_length=255, blank=True)
    entry_kind = models.CharField(max_length=20, choices=LedgerEntryKind.choices)
    entry_source = models.CharField(max_length=20, choices=LedgerEntrySource.choices)
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.ARS,
    )
    posted_at = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=255, blank=True)

    document_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    document_object_id = models.PositiveIntegerField(null=True, blank=True)
    document = GenericForeignKey("document_content_type", "document_object_id")

    payment_order = models.ForeignKey(
        "payables.PaymentOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ledger_entries",
    )
    treasury_payment = models.ForeignKey(
        "treasury.OutgoingPayment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supplier_ledger_entries",
    )
    retention_certificate = models.ForeignKey(
        "payables.RetentionCertificate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ledger_entries",
    )

    debit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    balance_after = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    extra_data = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Movimiento proveedor"
        verbose_name_plural = "Movimientos proveedores"
        ordering = ["-posted_at", "-id"]
        indexes = [
            models.Index(fields=["supplier", "posted_at"]),
            models.Index(fields=["entry_kind"]),
        ]
