from django.db import models

from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product


class PurchaseReceiptItem(BaseModel):
    """Detalle de un comprobante de recepción."""

    receipt = models.ForeignKey(
        "purchases.PurchaseReceipt",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Recepción",
    )
    order_item = models.ForeignKey(
        "purchases.PurchaseOrderItem",
        on_delete=models.SET_NULL,
        related_name="receipt_items",
        null=True,
        blank=True,
        verbose_name="Renglón de orden",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="purchase_receipt_items",
        verbose_name="Producto",
    )
    description = models.CharField(max_length=255, blank=True, verbose_name="Descripción")
    quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="Cantidad")
    unit_price = models.DecimalField(max_digits=15, decimal_places=4, verbose_name="Precio unitario")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="IVA %")
    legacy_description_id = models.IntegerField(null=True, blank=True, verbose_name="DAP legacy")

    class Meta:
        verbose_name = "Detalle de recepción"
        verbose_name_plural = "Detalles de recepción"

    def __str__(self) -> str:
        return f"Recep {self.receipt_id} / Prod {self.product_id}"
