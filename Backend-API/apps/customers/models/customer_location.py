from django.db import models

from apps.products.models.base_model import BaseModel
from apps.customers.models.postal_code import PostalCode


class CustomerLocation(BaseModel):
    """Localidades y provincias (tablas LOCALIDADES/PROVINCIAS)."""

    legacy_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="ID legacy")
    name = models.CharField(max_length=255, verbose_name="Nombre localidad")
    province_name = models.CharField(max_length=255, blank=True, verbose_name="Provincia")
    postal_code = models.ForeignKey(
        PostalCode,
        on_delete=models.SET_NULL,
        related_name="locations",
        null=True,
        blank=True,
        verbose_name="Código postal",
    )

    class Meta:
        verbose_name = "Localidad"
        verbose_name_plural = "Localidades"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.province_name})" if self.province_name else self.name
