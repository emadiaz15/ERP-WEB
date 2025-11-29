from django.db import models

from apps.products.models.base_model import BaseModel


class Bank(BaseModel):
    """Catálogo de bancos (tabla legacy ``bancos``)."""

    legacy_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID legacy",
        help_text="Identificador legado ban_codi.",
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Nombre",
        help_text="Descripción del banco (ban_desc).",
    )
    tax_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="CUIT",
        help_text="CUIT del banco (ban_cuit).",
    )
    swift_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="SWIFT/BIC",
    )
    country = models.CharField(
        max_length=60,
        null=True,
        blank=True,
        verbose_name="País",
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Notas",
    )

    class Meta:
        verbose_name = "Banco"
        verbose_name_plural = "Bancos"
        ordering = ["name"]
        indexes = [models.Index(fields=["legacy_id"]), models.Index(fields=["name"])]

    def __str__(self) -> str:
        return self.name
