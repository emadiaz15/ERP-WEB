from django.db import models

from apps.products.models.base_model import BaseModel


class CustomerZone(BaseModel):
    """Zonas comerciales para agrupar clientes (tabla legacy ZONAS)."""

    legacy_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="ID legacy")
    name = models.CharField(max_length=255, verbose_name="Descripción")
    vendor_legacy_id = models.IntegerField(null=True, blank=True, verbose_name="Vendedor legacy")

    class Meta:
        verbose_name = "Zona de cliente"
        verbose_name_plural = "Zonas de clientes"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
