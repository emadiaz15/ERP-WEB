from django.db import models

from apps.products.models.base_model import BaseModel
from apps.suppliers.models.supplier_model import Supplier
from apps.treasury.models.bank_account import BankAccount
from apps.treasury.models.payment_method import PaymentMethod


class OutgoingPayment(BaseModel):
    """Pago a proveedores (tabla ``pagosprov``)."""

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        related_name="payments",
        null=True,
        blank=True,
        verbose_name="Proveedor",
    )
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.PROTECT,
        related_name="payments",
        null=True,
        blank=True,
        verbose_name="Cuenta bancaria",
    )
    legacy_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID legacy",
        help_text="Código heredado pag_codi.",
    )
    date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha",
        help_text="Fecha del pago (pag_fech).",
    )
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name="Importe",
        help_text="Importe total pag_impo.",
    )
    currency = models.CharField(
        max_length=5,
        default="ARS",
        verbose_name="Moneda",
    )
    exchange_rate = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Cotización",
        help_text="cotiz_dolar",
    )
    supplier_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Proveedor legacy",
        help_text="prov_codi cuando no existe Supplier.",
    )
    reference = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name="Referencia",
        help_text="Nro comprobante / pag_obser.",
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Notas",
    )
    retention_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Retención",
        help_text="Importe total retenido informado por el ERP legacy.",
    )
    status_flag = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="Estado legacy",
    )

    class Meta:
        verbose_name = "Pago de proveedor"
        verbose_name_plural = "Pagos de proveedores"
        ordering = ["-date", "-created_at"]
        indexes = [models.Index(fields=["legacy_id"]), models.Index(fields=["date"])]

    def __str__(self) -> str:
        supplier = self.supplier.name if self.supplier else self.supplier_legacy_id
        return f"Pago {self.legacy_id or self.pk} -> {supplier}"

    @property
    def retained_total(self):
        """Suma el importe retenido registrado en los comprobantes asociados."""
        return sum(ret.amount for ret in self.retentions.all())


class PaymentInstrument(BaseModel):
    """Detalle de medios de pago aplicados (tablas pagosprov_pagos / pagosgas_pagos)."""

    payment = models.ForeignKey(
        OutgoingPayment,
        on_delete=models.CASCADE,
        related_name="instruments",
        verbose_name="Pago",
    )
    method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        related_name="payment_instruments",
        verbose_name="Medio de pago",
    )
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.PROTECT,
        related_name="payment_instruments",
        null=True,
        blank=True,
        verbose_name="Cuenta bancaria",
    )
    reference_number = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name="Referencia",
        help_text="Cheque/transferencia/etc (chequenro, movtippag_nro).",
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha vencimiento",
        help_text="movtippag_fvto",
    )
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name="Importe",
    )
    currency = models.CharField(
        max_length=5,
        default="ARS",
        verbose_name="Moneda",
    )

    class Meta:
        verbose_name = "Instrumento de pago"
        verbose_name_plural = "Instrumentos de pago"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.method} {self.amount}"
