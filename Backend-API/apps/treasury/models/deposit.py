from django.db import models

from apps.products.models.base_model import BaseModel
from apps.treasury.models.bank_account import BankAccount


class Deposit(BaseModel):
    """Depósito bancario (tabla ``depositos``)."""

    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.PROTECT,
        related_name="deposits",
        verbose_name="Cuenta bancaria",
    )
    legacy_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID legacy",
        help_text="Código heredado dep_codi.",
    )
    date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha",
        help_text="Fecha del depósito (dep_fech).",
    )
    voucher_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Número boleta",
        help_text="Número de boleta (dep_bolnro).",
    )
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name="Importe",
        help_text="Importe del depósito (dep_importe).",
    )
    currency = models.CharField(
        max_length=5,
        default="ARS",
        verbose_name="Moneda",
    )
    reference = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name="Referencia",
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Depósito"
        verbose_name_plural = "Depósitos"
        ordering = ["-date", "-created_at"]
        indexes = [models.Index(fields=["legacy_id"]), models.Index(fields=["date"])]

    def __str__(self) -> str:
        return f"Depósito {self.voucher_number or self.pk}"
