from django.db import models

from apps.products.models.base_model import BaseModel


class SalesRepresentative(BaseModel):
    """Vendedor o viajante asociado a los pedidos (tabla ``vendedores``)."""

    legacy_id = models.IntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name="ID legacy",
        help_text="Identificador del vendedor en el sistema legacy (ven_codi)",
    )
    code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Código",
        help_text="Código interno o abreviado del vendedor",
    )
    name = models.CharField(max_length=255, verbose_name="Nombre y apellido")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone_primary = models.CharField(max_length=30, blank=True, verbose_name="Teléfono 1")
    phone_secondary = models.CharField(max_length=30, blank=True, verbose_name="Teléfono 2")
    mobile_phone = models.CharField(max_length=30, blank=True, verbose_name="Celular")
    is_traveling = models.BooleanField(
        default=False,
        verbose_name="Es viajante",
        help_text="Permite diferenciar vendedores internos de viajantes",
    )
    notes = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta:
        verbose_name = "Vendedor"
        verbose_name_plural = "Vendedores"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
