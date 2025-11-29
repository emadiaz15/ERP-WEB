from django.db import models
from apps.products.models.base_model import BaseModel


class Category(BaseModel):
    """Modelo de Categoría reutilizando lógica de BaseModel.

    Conceptualmente representa el "rubro" del artículo en el sistema legacy
    (tabla ``rubros``), pero en el código del backend se mantiene el nombre
    genérico "Category" para evitar romper dependencias actuales.
    """

    # Campo para el nombre de la categoría / rubro
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Nombre de la categoría",
        help_text="Nombre del rubro/categoría (rub_desc).",
    )

    # Campo opcional para la descripción de la categoría
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción",
        help_text="Descripción adicional de la categoría.",
    )

    def __str__(self) -> str:
        """Retorna el nombre de la categoría como representación."""

        return self.name
