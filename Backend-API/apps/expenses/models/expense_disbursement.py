from django.db import models

from apps.products.models.base_model import BaseModel


class ExpenseDisbursement(BaseModel):
    """Pagos asociados directamente a un gasto puntual (legacy: ``gastos_pagos``)."""

    expense = models.ForeignKey(
        "expenses.Expense",
        on_delete=models.CASCADE,
        related_name="disbursements",
        verbose_name="Gasto",
    )
    expense_type_code = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Tipo de gasto legacy",
        help_text="tipgas_codi",
    )
    transaction_number = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Nro transacción",
        help_text="movtippag_nro",
    )
    bank_code = models.IntegerField(null=True, blank=True, verbose_name="Banco legacy")
    document_piece = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Pieza",
        help_text="movtippag_pza",
    )
    due_date = models.DateField(null=True, blank=True, verbose_name="Vencimiento")
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Importe",
        help_text="movtippag_imp",
    )
    taxpayer_number = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="CUIT librador",
        help_text="cuit_lib",
    )
    legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID legacy",
        help_text="gaspag_codi",
    )

    class Meta:
        verbose_name = "Pago directo de gasto"
        verbose_name_plural = "Pagos directos de gasto"

    def __str__(self) -> str:
        return f"Pago directo {self.id or 'nuevo'}"
