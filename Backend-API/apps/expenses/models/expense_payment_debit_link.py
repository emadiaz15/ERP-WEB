from django.db import models

from apps.products.models.base_model import BaseModel


class ExpensePaymentDebitLink(BaseModel):
    """Relación entre pagos y débitos internos (legacy: ``pagosgas_debintg``)."""

    payment = models.ForeignKey(
        "expenses.ExpensePayment",
        on_delete=models.CASCADE,
        related_name="debit_links",
        verbose_name="Pago",
    )
    debit_legacy_id = models.IntegerField(
        verbose_name="ID débito legacy",
        help_text="debg_codi",
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Importe aplicado",
        help_text="pagdebi_imp",
    )
    is_partial = models.BooleanField(
        default=False,
        verbose_name="Aplicación parcial",
        help_text="pagdebi_parci",
    )
    legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID legacy",
        help_text="pagdebi_cod",
    )

    class Meta:
        verbose_name = "Vinculación de débito"
        verbose_name_plural = "Vinculaciones de débito"

    def __str__(self) -> str:
        return f"Pago {self.payment_id} ↔ Débito {self.debit_legacy_id}"
