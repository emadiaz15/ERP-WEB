from django.db import models

from apps.products.models.base_model import BaseModel


class ExpenseType(BaseModel):
    """Catálogo de tipos de gasto (legacy: ``tiposgastos``)."""

    code = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Código interno",
        help_text="Identificador legible (ej. HONORARIOS).",
    )
    name = models.CharField(max_length=120, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    legacy_id = models.IntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name="ID legacy",
        help_text="Equivalente a tipgas_codi.",
    )
    category = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Categoría",
        help_text="Permite agrupar (ej. operativos, financieros).",
    )
    is_tax_related = models.BooleanField(default=False, verbose_name="Impacta impuestos")
    requires_approval = models.BooleanField(
        default=True,
        verbose_name="Requiere aprobación",
        help_text="Define si los gastos de este tipo deben pasar por un workflow de aprobación.",
    )
    retention_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="% retención sugerido",
        help_text="Porcentaje automático para cálculos de retenciones.",
    )
    retention_minimum_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Mínimo para retener",
        help_text="Monto mínimo sobre el cual aplicar retenciones.",
    )

    class Meta:
        verbose_name = "Tipo de gasto"
        verbose_name_plural = "Tipos de gasto"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
