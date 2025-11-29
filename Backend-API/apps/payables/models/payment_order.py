from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from apps.products.models.base_model import BaseModel
from apps.suppliers.models import Supplier
from apps.payables.choices import PaymentOrderStatus
from apps.financial.choices import CurrencyChoices


class PaymentOrder(BaseModel):
    """Orden de pago que agrupa documentos e instruye tesorería."""

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="payment_orders",
        verbose_name="Proveedor",
    )
    supplier_name_snapshot = models.CharField(max_length=255, blank=True)
    supplier_legacy_id = models.IntegerField(null=True, blank=True, db_index=True)
    status_label = models.CharField(
        max_length=20,
        choices=PaymentOrderStatus.choices,
        default=PaymentOrderStatus.DRAFT,
        verbose_name="Estado",
    )
    order_date = models.DateField(default=timezone.now, verbose_name="Fecha de orden")
    scheduled_payment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha planificada",
    )
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.ARS,
        verbose_name="Moneda",
    )
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=4, default=1)
    gross_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    retention_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    treasury_payment = models.ForeignKey(
        "treasury.OutgoingPayment",
        on_delete=models.SET_NULL,
        related_name="payment_orders",
        null=True,
        blank=True,
        verbose_name="Pago ejecutado",
    )
    authorized_at = models.DateTimeField(null=True, blank=True)
    authorized_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="payment_orders_authorized",
        null=True,
        blank=True,
    )
    executed_at = models.DateTimeField(null=True, blank=True)
    observations = models.TextField(blank=True)
    legacy_id = models.IntegerField(null=True, blank=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Orden de pago"
        verbose_name_plural = "Órdenes de pago"
        ordering = ["-order_date", "-created_at"]

    def mark_authorized(self, *, user=None):
        if self.status_label == PaymentOrderStatus.DRAFT:
            self.status_label = PaymentOrderStatus.AUTHORIZED
            self.authorized_at = timezone.now()
            if user:
                self.authorized_by = user
            self.save(user=user)

    def mark_as_executed(self, *, user=None):
        if self.status_label != PaymentOrderStatus.EXECUTED:
            self.status_label = PaymentOrderStatus.EXECUTED
            self.executed_at = timezone.now()
            self.save(user=user)


class PaymentOrderLine(BaseModel):
    payment_order = models.ForeignKey(
        PaymentOrder,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name="Orden de pago",
    )
    document_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    document_object_id = models.PositiveIntegerField()
    document = GenericForeignKey("document_content_type", "document_object_id")
    currency = models.CharField(max_length=3, choices=CurrencyChoices.choices, default=CurrencyChoices.ARS)
    original_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    amount_to_pay = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    retention_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Detalle orden de pago"
        verbose_name_plural = "Detalles orden de pago"
        unique_together = (
            "payment_order",
            "document_content_type",
            "document_object_id",
        )
        indexes = [models.Index(fields=["payment_order"])]
