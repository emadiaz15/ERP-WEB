from django.db import models

from apps.products.models.base_model import BaseModel
from apps.suppliers.models import Supplier
from apps.financial.choices import CurrencyChoices


class SupplierOpeningBalance(BaseModel):
    """Saldos iniciales migrados para proveedores."""

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="opening_balances",
        verbose_name="Proveedor",
    )
    balance_date = models.DateField(verbose_name="Fecha saldo")
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.ARS,
    )
    debit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    reference = models.CharField(max_length=120, blank=True)
    legacy_id = models.IntegerField(null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = "Saldo inicial proveedor"
        verbose_name_plural = "Saldos iniciales proveedor"
        ordering = ["-balance_date", "supplier"]
