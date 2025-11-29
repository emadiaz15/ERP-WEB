from django.db import models

from apps.products.models.base_model import BaseModel


class ExpensePaymentAllocation(BaseModel):
    """Aplicación de un pago a un gasto específico (legacy: ``pagosgas_gastos``)."""

    payment = models.ForeignKey(
        "expenses.ExpensePayment",
        on_delete=models.CASCADE,
        related_name="allocations",
        verbose_name="Pago",
    )
    expense = models.ForeignKey(
        "expenses.Expense",
        on_delete=models.CASCADE,
        related_name="payment_allocations",
        verbose_name="Gasto",
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Importe aplicado",
    )
    is_partial = models.BooleanField(
        default=False,
        verbose_name="Aplicación parcial",
        help_text="Equivalente a paggas_parci",
    )
    legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID legacy",
        help_text="paggas_codi",
    )

    class Meta:
        verbose_name = "Aplicación de pago"
        verbose_name_plural = "Aplicaciones de pago"
        constraints = [
            models.UniqueConstraint(
                fields=["payment", "expense", "legacy_id"],
                name="uniq_payment_expense_legacy",
                condition=models.Q(legacy_id__isnull=False),
            )
        ]

    def __str__(self) -> str:
        return f"Pago {self.payment_id} → Gasto {self.expense_id}"
