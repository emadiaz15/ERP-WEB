from django.db import models

from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product


class InventoryCountItem(BaseModel):
    """Detalle de conteo físico."""

    count = models.ForeignKey(
        "inventory_adjustments.InventoryCount",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Conteo",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="inventory_count_items",
        verbose_name="Producto",
    )
    system_quantity = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name="Cantidad sistema")
    counted_quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="Cantidad contada")
    difference = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="Diferencia")
    observations = models.CharField(max_length=255, blank=True, verbose_name="Observaciones")
    legacy_id = models.IntegerField(null=True, blank=True, verbose_name="ID legacy detalle")

    class Meta:
        verbose_name = "Detalle de conteo"
        verbose_name_plural = "Detalles de conteo"

    def save(self, *args, **kwargs):
        if self.counted_quantity is not None and self.system_quantity is not None:
            self.difference = self.counted_quantity - self.system_quantity
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.count_id}-{self.product_id}"
