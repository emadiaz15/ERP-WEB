from django.db import models

from apps.products.models.base_model import BaseModel


class StockAdjustment(BaseModel):
    """Cabecera de un ajuste de stock administrativo."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        POSTED = "posted", "Aplicado"
        CANCELLED = "cancelled", "Anulado"

    adjustment_date = models.DateField(verbose_name="Fecha del ajuste")
    concept = models.CharField(max_length=255, blank=True, verbose_name="Concepto")
    observations = models.TextField(blank=True, verbose_name="Observaciones")
    legacy_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        unique=True,
        verbose_name="Código legacy",
        help_text="Equivalente a la columna aju_codi del ERP.",
    )
    legacy_concept_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Código concepto legacy",
        help_text="Valor original sin procesar de aju_conc.",
    )
    status_label = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Estado",
    )

    class Meta:
        verbose_name = "Ajuste de stock"
        verbose_name_plural = "Ajustes de stock"
        ordering = ["-adjustment_date", "-id"]

    def __str__(self) -> str:
        return f"AJU-{self.id or 'new'}"

    @property
    def total_adjustment_quantity(self):
        """Suma la cantidad ajustada (delta) de todos los renglones."""
        return sum(item.adjustment_quantity for item in self.items.all())
