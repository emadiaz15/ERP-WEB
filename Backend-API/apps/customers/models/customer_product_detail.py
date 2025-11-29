from django.db import models

from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product
from apps.customers.models.customer import Customer


class CustomerProductDetail(BaseModel):
    """Descripción personalizada por cliente (tabla ARTICULOS_CLIENTES)."""

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="product_details",
        verbose_name="Cliente",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="customer_details",
        verbose_name="Producto",
    )
    custom_description = models.CharField(max_length=255, blank=True, verbose_name="Descripción personalizada")
    legacy_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="ID legacy")

    class Meta:
        verbose_name = "Detalle de producto por cliente"
        verbose_name_plural = "Detalles de producto por cliente"
        unique_together = ("customer", "product")

    def __str__(self) -> str:
        return f"{self.customer_id}-{self.product_id}"
