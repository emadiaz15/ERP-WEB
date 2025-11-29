from django.db import models

from apps.products.models.base_model import BaseModel


class TaxCondition(BaseModel):
    """Condición frente a IVA (tabla CONDIVA)."""

    legacy_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="ID legacy")
    name = models.CharField(max_length=255, verbose_name="Descripción")

    class Meta:
        verbose_name = "Condición impositiva"
        verbose_name_plural = "Condiciones impositivas"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
