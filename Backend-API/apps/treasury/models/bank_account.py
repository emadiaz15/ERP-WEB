from django.db import models

from apps.products.models.base_model import BaseModel
from apps.treasury.models.bank import Bank


class BankAccount(BaseModel):
    """Cuenta bancaria o caja (tabla ``bancos_caja``)."""

    bank = models.ForeignKey(
        Bank,
        on_delete=models.PROTECT,
        related_name="accounts",
        null=True,
        blank=True,
        verbose_name="Banco",
    )
    legacy_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID legacy",
        help_text="Código heredado (banc_codi).",
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Descripción",
        help_text="Nombre de la cuenta/caja (banc_desc).",
    )
    tax_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="CUIT",
        help_text="CUIT asociado (banc_cuit).",
    )
    account_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Número de cuenta",
        help_text="Número interno (banc_ncta).",
    )
    cbu = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name="CBU",
    )
    alias = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Alias",
    )
    currency = models.CharField(
        max_length=5,
        default="ARS",
        verbose_name="Moneda",
    )
    current_balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name="Saldo",
        help_text="Saldo cacheado (banc_saldo).",
    )
    is_cash_account = models.BooleanField(
        default=False,
        verbose_name="Es caja",
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Notas",
    )

    class Meta:
        verbose_name = "Cuenta bancaria"
        verbose_name_plural = "Cuentas bancarias"
        ordering = ["name"]
        indexes = [models.Index(fields=["legacy_id"]), models.Index(fields=["name"])]

    def __str__(self) -> str:
        return f"{self.name} ({self.currency})"
