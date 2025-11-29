from django.db import models

from apps.products.models.base_model import BaseModel
from apps.locations.models.province_model import Province
from apps.locations.models.postal_code_model import PostalCode
from apps.locations.models.zone_model import SalesZone


class Locality(BaseModel):
    """City/locality catalog mapping legacy table ``localidades``.

    Legacy columns:
    - loca_codi (PK)  → ``legacy_code``
    - loca_nomb       → ``name``
    - provi_codi      → FK Provincia
    - cp_codi         → FK Código Postal
    - zona_codi       → FK Zona
    """

    province = models.ForeignKey(
        Province,
        on_delete=models.PROTECT,
        related_name="localities",
        verbose_name="Provincia",
    )
    postal_code = models.ForeignKey(
        PostalCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="localities",
        verbose_name="Código postal",
    )
    zone = models.ForeignKey(
        SalesZone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="localities",
        verbose_name="Zona",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Nombre",
        help_text="Nombre de la localidad (loca_nomb).",
    )
    legacy_code = models.IntegerField(
        unique=True,
        verbose_name="Código legacy",
        help_text="Identificador de localidad en el legacy (loca_codi).",
    )

    class Meta:
        verbose_name = "Localidad"
        verbose_name_plural = "Localidades"
        ordering = ["name"]
        indexes = [models.Index(fields=["legacy_code"])]

    def __str__(self) -> str:
        return self.name
