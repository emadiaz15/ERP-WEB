from django.db import models

from apps.products.models.base_model import BaseModel


class InventoryCount(BaseModel):
    """Conteo físico de inventario."""

    class Status(models.TextChoices):
        OPEN = "open", "Abierto"
        IN_PROGRESS = "in_progress", "En proceso"
        CLOSED = "closed", "Cerrado"
        CANCELLED = "cancelled", "Anulado"

    count_date = models.DateField(verbose_name="Fecha del conteo")
    description = models.CharField(max_length=255, blank=True, verbose_name="Descripción")
    notes = models.TextField(blank=True, verbose_name="Notas")
    legacy_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="ID legacy")
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de cierre")
    status_label = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name="Estado",
    )

    class Meta:
        verbose_name = "Conteo de inventario"
        verbose_name_plural = "Conteos de inventario"
        ordering = ["-count_date", "-id"]

    def __str__(self) -> str:
        return f"INV-{self.id or 'new'}"
