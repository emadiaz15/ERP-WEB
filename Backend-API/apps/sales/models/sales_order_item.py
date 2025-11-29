from django.db import models

from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product


class SalesOrderItem(BaseModel):
    """Detalle de un pedido de venta."""

    order = models.ForeignKey(
        "sales.SalesOrder",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Pedido",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="sales_order_items",
        verbose_name="Producto",
    )
    description = models.CharField(max_length=255, blank=True, verbose_name="Descripción")
    quantity_ordered = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="Cantidad solicitada")
    quantity_shipped = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name="Cantidad despachada")
    unit_price = models.DecimalField(max_digits=15, decimal_places=4, verbose_name="Precio unitario")
    discount_amount = models.DecimalField(max_digits=15, decimal_places=4, default=0, verbose_name="Descuento")
    vat_rate_code = models.CharField(max_length=10, blank=True, verbose_name="Código IVA")
    legacy_detail_id = models.IntegerField(null=True, blank=True, verbose_name="Detalle legacy")

    class Meta:
        verbose_name = "Renglón de pedido de venta"
        verbose_name_plural = "Renglones de pedido de venta"

    def __str__(self) -> str:
        return f"{self.order_id}-{self.product_id}"
