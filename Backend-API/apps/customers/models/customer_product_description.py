from django.db import models

from apps.products.models.base_model import BaseModel
from apps.customers.models.customer_product_detail import CustomerProductDetail


class CustomerProductDescription(BaseModel):
    """Descripciones adicionales (tabla DESC_ARTICULOS_CLIENTES)."""

    detail = models.ForeignKey(
        CustomerProductDetail,
        on_delete=models.CASCADE,
        related_name="descriptions",
        verbose_name="Detalle",
    )
    description = models.CharField(max_length=255, verbose_name="Descripción")
    legacy_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="ID legacy")

    class Meta:
        verbose_name = "Descripción extendida de producto"
        verbose_name_plural = "Descripciones extendidas de producto"

    def __str__(self) -> str:
        return self.description
