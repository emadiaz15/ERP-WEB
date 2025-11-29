from django.db import models

from apps.financial.choices import CurrencyChoices
from apps.products.models.base_model import BaseModel
from apps.logistics.choices import CarrierAccountEntryType


class CarrierAccountEntry(BaseModel):
    """Movimientos de cuenta corriente del transportista."""

    carrier = models.ForeignKey(
        "logistics.Carrier",
        on_delete=models.CASCADE,
        related_name="account_entries",
        verbose_name="Transportista",
    )
    entry_type = models.CharField(
        max_length=20,
        choices=CarrierAccountEntryType.choices,
        default=CarrierAccountEntryType.DEBIT,
        verbose_name="Tipo",
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Importe")
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.ARS,
        verbose_name="Moneda",
    )
    balance_after = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name="Saldo luego del movimiento",
    )
    reference_module = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Módulo origen",
        help_text="Ej: purchases, orders, treasury",
    )
    reference_id = models.IntegerField(null=True, blank=True, verbose_name="ID referencia")
    description = models.CharField(max_length=255, blank=True, verbose_name="Descripción")
    due_date = models.DateField(null=True, blank=True, verbose_name="Fecha de vencimiento")
    settled_date = models.DateField(null=True, blank=True, verbose_name="Fecha cancelación")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Metadata adicional")

    class Meta:
        verbose_name = "Movimiento cuenta transportista"
        verbose_name_plural = "Cuenta corriente transportistas"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.carrier.name} - {self.entry_type} - {self.amount}"
