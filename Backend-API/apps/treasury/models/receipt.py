from django.db import models

from apps.products.models.base_model import BaseModel
from apps.customers.models.customer import Customer
from apps.treasury.models.bank_account import BankAccount


class Receipt(BaseModel):
    """Recibo de cobranzas (tabla ``recibos``)."""

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        related_name="receipts",
        null=True,
        blank=True,
        verbose_name="Cliente",
    )
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.PROTECT,
        related_name="receipts",
        null=True,
        blank=True,
        verbose_name="Cuenta bancaria",
    )
    legacy_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID legacy",
        help_text="Código heredado rec_codi.",
    )
    number = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Número",
        help_text="Número interno del recibo (rec_nro).",
    )
    receipt_type = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="Tipo",
        help_text="Tipo/talón (rec_tipo).",
    )
    date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha",
        help_text="Fecha del recibo (rec_fec).",
    )
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name="Importe",
        help_text="Importe total (rec_impo).",
    )
    advance_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Anticipo",
        help_text="Importe anticipo (rec_antic).",
    )
    currency = models.CharField(
        max_length=5,
        default="ARS",
        verbose_name="Moneda",
    )
    customer_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID cliente legacy",
        help_text="Referencia cli_codi por si el cliente todavía no existe.",
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observaciones",
        help_text="Contenido de rec_obser.",
    )
    legacy_status = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="Estado legacy",
    )

    class Meta:
        verbose_name = "Recibo"
        verbose_name_plural = "Recibos"
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["legacy_id"]),
            models.Index(fields=["date"]),
            models.Index(fields=["customer_legacy_id"]),
        ]

    def __str__(self) -> str:
        return f"Recibo {self.number or self.pk}"
