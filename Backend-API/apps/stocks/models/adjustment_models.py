from django.db import models
from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product


class StockAdjustment(BaseModel):
    """Ajuste de stock manual para uno o varios productos.

    Mapea la tabla legacy ``ajustes`` (aju_codi, aju_fech, aju_conc, aju_observ).
    En este nuevo modelo ``id`` es la PK real y el número de ajuste
    legible puede exponerse usando el ``id`` o un campo externo.
    """

    date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha del ajuste",
        help_text="Fecha del ajuste de stock (aju_fech).",
    )
    concept = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Concepto",
        help_text="Concepto corto del ajuste (aju_conc).",
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observaciones",
        help_text="Observaciones y detalle del ajuste (aju_observ).",
    )

    class Meta:
        verbose_name = "Ajuste de Stock"
        verbose_name_plural = "Ajustes de Stock"
        ordering = ["-date", "-created_at"]

    def __str__(self) -> str:
        return f"Ajuste #{self.pk} - {self.date or 'sin fecha'}"


class StockAdjustmentItem(BaseModel):
    """Detalle de productos incluidos en un ajuste de stock.

    Mapea la tabla legacy ``ajustes_articulos`` (aju_codi, art_codi, artaju_cant).
    Cada registro representa un movimiento de stock para un producto
    asociado al ajuste padre.
    """

    adjustment = models.ForeignKey(
        StockAdjustment,
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
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        verbose_name="Cantidad ajustada",
        help_text="Cantidad ajustada (positiva o negativa) (artaju_cant).",
    )

    class Meta:
        verbose_name = "Ítem de Ajuste de Stock"
        verbose_name_plural = "Ítems de Ajuste de Stock"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Ajuste {self.adjustment_id} - Prod {self.product_id} ({self.quantity})"
