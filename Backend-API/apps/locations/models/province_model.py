from django.db import models

from apps.products.models.base_model import BaseModel
from apps.locations.models.country_model import Country


class Province(BaseModel):
    """Province/state catalog mapping legacy table ``provincias``.

    Legacy columns:
    - provi_codi (PK)  → ``legacy_code``
    - provi_nomb       → ``name``
    """

    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="provinces",
        verbose_name="País",
    )
    name = models.CharField(
        max_length=150,
        verbose_name="Nombre",
        help_text="Nombre de la provincia (provi_nomb).",
    )
    legacy_code = models.IntegerField(
        unique=True,
        verbose_name="Código legacy",
        help_text="Código numérico heredado (provi_codi).",
    )

    class Meta:
        verbose_name = "Provincia"
        verbose_name_plural = "Provincias"
        ordering = ["name"]
        indexes = [models.Index(fields=["legacy_code"])]

    def __str__(self) -> str:
        return self.name
