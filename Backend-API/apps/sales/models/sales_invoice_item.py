from django.db import models

from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product


class SalesInvoiceItem(BaseModel):
    """Detalle asociado a una factura de venta."""

    invoice = models.ForeignKey(
        "sales.SalesInvoice",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Factura",
    )
    order_item = models.ForeignKey(
        "sales.SalesOrderItem",
        on_delete=models.SET_NULL,
        related_name="invoice_items",
        null=True,
        blank=True,
        verbose_name="Renglón de pedido",
    )
    shipment_item = models.ForeignKey(
        "sales.SalesShipmentItem",
        on_delete=models.SET_NULL,
        related_name="invoice_items",
        null=True,
        blank=True,
        verbose_name="Renglón de remito",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="sales_invoice_items",
        verbose_name="Producto",
    )
    description = models.CharField(max_length=255, blank=True, verbose_name="Descripción")
    quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="Cantidad")
    unit_price = models.DecimalField(max_digits=15, decimal_places=4, verbose_name="Precio unitario")
    discount_amount = models.DecimalField(max_digits=15, decimal_places=4, default=0, verbose_name="Descuento")
    vat_rate_code = models.CharField(max_length=10, blank=True, verbose_name="Código IVA")
    legacy_detail_id = models.IntegerField(null=True, blank=True, verbose_name="Detalle legacy")

    class Meta:
        verbose_name = "Renglón de factura de venta"
        verbose_name_plural = "Renglones de factura de venta"

    def __str__(self) -> str:
        return f"{self.invoice_id}-{self.product_id}"
