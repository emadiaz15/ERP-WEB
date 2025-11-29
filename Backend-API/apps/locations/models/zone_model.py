from django.db import models

from apps.products.models.base_model import BaseModel


class SalesZone(BaseModel):
    """Geographical zone assigned to traveling salespeople.

    Mapea la tabla legacy ``zonas``:
    - zona_codi (PK) → ``legacy_code``
    - zona_desc     → ``name``
    - ven_codi      → ``salesperson_legacy_id`` (referencia a vendedores)
    """

    name = models.CharField(
        max_length=120,
        verbose_name="Nombre",
        help_text="Descripción de la zona (zona_desc).",
    )
    legacy_code = models.IntegerField(
        unique=True,
        verbose_name="Código legacy",
        help_text="Identificador de la zona en el sistema legacy (zona_codi).",
    )
    salesperson_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID legacy de vendedor",
        help_text="Vendedor asignado a la zona (ven_codi).",
    )

    class Meta:
        verbose_name = "Zona de Ventas"
        verbose_name_plural = "Zonas de Ventas"
        ordering = ["name"]
        indexes = [models.Index(fields=["legacy_code"])]

    def __str__(self) -> str:
        return self.name
