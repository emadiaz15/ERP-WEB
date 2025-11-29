from django.db import models

from apps.products.models.base_model import BaseModel
from apps.customers.models.customer_zone import CustomerZone
from apps.customers.models.customer_location import CustomerLocation
from apps.customers.models.tax_condition import TaxCondition


class Customer(BaseModel):
    """Cliente del ERP (tabla CLIENTES)."""

    legacy_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="ID legacy")
    code = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="Código interno")
    name = models.CharField(max_length=255, verbose_name="Nombre")
    address = models.CharField(max_length=255, blank=True, verbose_name="Domicilio")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone_primary = models.CharField(max_length=30, blank=True, verbose_name="Teléfono 1")
    phone_secondary = models.CharField(max_length=30, blank=True, verbose_name="Teléfono 2")
    mobile_phone = models.CharField(max_length=30, blank=True, verbose_name="Celular")
    cuit = models.CharField(max_length=20, blank=True, verbose_name="CUIT")
    legacy_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Saldo legacy")
    legacy_credit = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Saldo a favor legacy")
    notes = models.TextField(blank=True, verbose_name="Observaciones")
    city = models.ForeignKey(
        CustomerLocation,
        on_delete=models.SET_NULL,
        related_name="customers",
        null=True,
        blank=True,
        verbose_name="Localidad",
    )
    zone = models.ForeignKey(
        CustomerZone,
        on_delete=models.SET_NULL,
        related_name="customers",
        null=True,
        blank=True,
        verbose_name="Zona",
    )
    tax_condition = models.ForeignKey(
        TaxCondition,
        on_delete=models.SET_NULL,
        related_name="customers",
        null=True,
        blank=True,
        verbose_name="Condición IVA",
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
