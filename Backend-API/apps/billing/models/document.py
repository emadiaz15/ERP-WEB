from decimal import Decimal

from django.db import models
from django.utils import timezone

from apps.customers.models import Customer
from apps.orders.models import CustomerOrder
from apps.products.models.base_model import BaseModel


class BillingDocumentType(models.TextChoices):
    INVOICE_A = "invoice_a", "Factura A"
    INVOICE_B = "invoice_b", "Factura B"
    CREDIT_NOTE = "credit_note", "Nota de crédito"
    DEBIT_NOTE = "debit_note", "Nota de débito"
    RECEIPT = "receipt", "Recibo"


class BillingDocumentStatus(models.TextChoices):
    DRAFT = "draft", "Borrador"
    PENDING = "pending", "Pendiente"
    AUTHORIZED = "authorized", "Autorizada"
    REJECTED = "rejected", "Rechazada"
    CANCELED = "canceled", "Cancelada"


class BillingDocument(BaseModel):
    document_type = models.CharField(max_length=30, choices=BillingDocumentType.choices)
    document_number = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name="Número de comprobante",
    )
    client = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="billing_documents",
    )
    order = models.ForeignKey(
        CustomerOrder,
        on_delete=models.SET_NULL,
        related_name="billing_documents",
        null=True,
        blank=True,
    )
    issue_date = models.DateField(default=timezone.now)
    currency = models.CharField(max_length=3, default="ARS")
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal("1.0000"))
    net_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(
        max_length=20,
        choices=BillingDocumentStatus.choices,
        default=BillingDocumentStatus.DRAFT,
    )
    remarks = models.TextField(blank=True)

    class Meta:
        verbose_name = "Documento de facturación"
        verbose_name_plural = "Documentos de facturación"
        ordering = ["-issue_date", "-created_at"]

    def __str__(self) -> str:
        display_number = self.document_number or f"#{self.pk or 'nuevo'}"
        return f"{self.get_document_type_display()} {display_number}"

    @property
    def has_order(self) -> bool:
        return self.order_id is not None
