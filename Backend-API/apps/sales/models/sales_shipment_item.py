from django.db import models

from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product


class SalesShipmentItem(BaseModel):
    """Detalle de remito de venta."""

    shipment = models.ForeignKey(
        "sales.SalesShipment",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Remito",
    )
    order_item = models.ForeignKey(
        "sales.SalesOrderItem",
        on_delete=models.SET_NULL,
        related_name="shipment_items",
        null=True,
        blank=True,
        verbose_name="Renglón de pedido",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="sales_shipment_items",
        verbose_name="Producto",
    )
    description = models.CharField(max_length=255, blank=True, verbose_name="Descripción")
    quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="Cantidad")
    unit_price = models.DecimalField(max_digits=15, decimal_places=4, verbose_name="Precio unitario")
    vat_rate_code = models.CharField(max_length=10, blank=True, verbose_name="Código IVA")
    legacy_detail_id = models.IntegerField(null=True, blank=True, verbose_name="Detalle legacy")

    class Meta:
        verbose_name = "Renglón de remito de venta"
        verbose_name_plural = "Renglones de remito de venta"

    def __str__(self) -> str:
        return f"{self.shipment_id}-{self.product_id}"
