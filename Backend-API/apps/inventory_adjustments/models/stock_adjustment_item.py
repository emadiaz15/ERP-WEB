from django.db import models

from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product


class StockAdjustmentItem(BaseModel):
    """Detalle de producto ajustado."""

    adjustment = models.ForeignKey(
        "inventory_adjustments.StockAdjustment",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Ajuste",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_items",
        related_query_name="%(app_label)s_%(class)s_item",
        verbose_name="Producto",
    )
    product_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Producto legacy",
        help_text="Código original de artículo (art_codi).",
    )
    system_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Cantidad sistema",
        help_text="Stock registrado antes del ajuste.",
    )
    counted_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Cantidad contada",
        help_text="Stock físico verificado para este ítem.",
    )
    difference = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=0,
        verbose_name="Cantidad de ajuste",
        help_text="Diferencia neta aplicada (artaju_cant).",
    )
    reason = models.CharField(max_length=255, blank=True, verbose_name="Motivo")
    legacy_id = models.IntegerField(null=True, blank=True, verbose_name="ID legacy detalle")

    class Meta:
        verbose_name = "Renglón de ajuste"
        verbose_name_plural = "Renglones de ajuste"

    def save(self, *args, **kwargs):
        # Si contamos stock y conocemos el valor previo, calculamos la diferencia.
        if self.counted_quantity is not None and self.system_quantity is not None:
            self.difference = self.counted_quantity - self.system_quantity
        # Si sólo tenemos la cantidad de ajuste más el valor previo, inferimos la cantidad contada.
        elif (
            self.system_quantity is not None
            and self.difference is not None
            and self.counted_quantity is None
        ):
            self.counted_quantity = self.system_quantity + self.difference
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.adjustment_id}-{self.product_id}"

    @property
    def adjustment_quantity(self):
        """Alias legible que expone la diferencia como delta de stock."""
        return self.difference
