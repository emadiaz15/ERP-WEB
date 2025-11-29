from django.db import models

from apps.products.models.base_model import BaseModel


class Country(BaseModel):
    """Country catalog used across clients, suppliers and sales reps.

    Aunque el legacy no define explícitamente una tabla de países, este
    modelo permite normalizar la información de ``provincias`` y
    ``localidades`` y soportar integraciones futuras.
    """

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Nombre",
        help_text="Nombre del país.",
    )
    iso_code = models.CharField(
        max_length=3,
        unique=True,
        verbose_name="Código ISO",
        help_text="Código ISO alfa-3 del país.",
    )
    legacy_code = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Código legacy",
        help_text="Identificador numérico si existiera en el sistema anterior.",
    )

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Países"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
