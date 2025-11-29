from django.db import models

from apps.products.models.base_model import BaseModel


class PostalCode(BaseModel):
    """Código postal (tabla CODIGOPOSTALES)."""

    legacy_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="ID legacy")
    code = models.CharField(max_length=20, verbose_name="Código postal")
    number = models.IntegerField(null=True, blank=True, verbose_name="Número postal")

    class Meta:
        verbose_name = "Código postal"
        verbose_name_plural = "Códigos postales"
        ordering = ["code"]

    def __str__(self) -> str:
        return self.code
