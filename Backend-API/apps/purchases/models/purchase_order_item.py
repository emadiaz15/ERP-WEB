from django.db import models

from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product


class PurchaseOrderItem(BaseModel):
    """Renglón de una orden de compra."""

    order = models.ForeignKey(
        "purchases.PurchaseOrder",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Orden",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="purchase_order_items",
        verbose_name="Producto",
    )
    description = models.CharField(max_length=255, blank=True, verbose_name="Descripción")
    quantity_ordered = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="Cantidad solicitada")
    quantity_received = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=0,
        verbose_name="Cantidad recibida",
    )
    unit_price = models.DecimalField(max_digits=15, decimal_places=4, verbose_name="Precio unitario")
    discount_amount = models.DecimalField(max_digits=15, decimal_places=4, default=0, verbose_name="Descuento")
    tax_code = models.CharField(max_length=10, blank=True, verbose_name="Código IVA")
    legacy_description_id = models.IntegerField(null=True, blank=True, verbose_name="Dap legacy")

    class Meta:
        verbose_name = "Renglón de orden de compra"
        verbose_name_plural = "Renglones de orden de compra"

    def __str__(self) -> str:
        return f"{self.order_id} - {self.product_id}"
