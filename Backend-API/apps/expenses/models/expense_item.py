from django.db import models

from apps.products.models.base_model import BaseModel


class ExpenseItem(BaseModel):
    """Detalle de artículos o conceptos asociados a un gasto (legacy: ``gastos_articulos``)."""

    expense = models.ForeignKey(
        "expenses.Expense",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Gasto",
    )
    description = models.CharField(max_length=255, verbose_name="Descripción")
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=1,
        verbose_name="Cantidad",
    )
    unit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=0,
        verbose_name="Importe unitario",
    )
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Importe total",
    )
    vat_rate_code = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Código de IVA",
        help_text="Equivalente a gasart_alicuota",
    )
    vat_rate_percent = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Alicuota %",
    )
    legacy_description_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID descripción legacy",
        help_text="Referencia a dap_codi u otras descripciones",
    )

    class Meta:
        verbose_name = "Detalle de gasto"
        verbose_name_plural = "Detalles de gasto"

    def __str__(self) -> str:
        return f"Detalle gasto {self.expense_id}"
