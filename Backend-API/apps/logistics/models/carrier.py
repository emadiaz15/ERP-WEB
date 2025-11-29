from django.db import models

from apps.locations.models import Locality
from apps.products.models.base_model import BaseModel


class Carrier(BaseModel):
    """Transportista (tabla legacy ``transportes``)."""

    legacy_id = models.IntegerField(null=True, blank=True, unique=True, verbose_name="ID legacy")
    name = models.CharField(max_length=255, verbose_name="Nombre comercial")
    tax_id = models.CharField(max_length=20, blank=True, verbose_name="CUIT")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone_primary = models.CharField(max_length=30, blank=True, verbose_name="Teléfono 1")
    phone_secondary = models.CharField(max_length=30, blank=True, verbose_name="Teléfono 2")
    mobile_phone = models.CharField(max_length=30, blank=True, verbose_name="Celular")
    address = models.CharField(max_length=255, blank=True, verbose_name="Domicilio")
    location = models.ForeignKey(
        Locality,
        on_delete=models.SET_NULL,
        related_name="carriers",
        null=True,
        blank=True,
        verbose_name="Localidad",
    )
    tax_condition_code = models.IntegerField(null=True, blank=True, verbose_name="Condición IVA legacy")
    payment_terms = models.CharField(max_length=120, blank=True, verbose_name="Condiciones de pago")
    bank_account_alias = models.CharField(max_length=120, blank=True, verbose_name="Alias / CBU")
    is_internal_fleet = models.BooleanField(default=False, verbose_name="Flota propia")
    notes = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta:
        verbose_name = "Transportista"
        verbose_name_plural = "Transportistas"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
