from django.db import models

from apps.delivery_notes.models.delivery_note import DeliveryNote
from apps.products.models.base_model import BaseModel


class DeliveryNoteLine(BaseModel):
    """Detalle de artículos incluidos en un remito."""

    delivery_note = models.ForeignKey(
        DeliveryNote,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name="Remito",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        related_name="delivery_note_lines",
        null=True,
        blank=True,
        verbose_name="Producto",
    )
    product_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Producto legacy",
        help_text="Código de artículo original (art_codi).",
    )
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        verbose_name="Cantidad",
        help_text="Cantidad entregada (artrem_cant).",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción del renglón (artrem_dasc).",
    )
    customer_discount_code = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Descuento cliente",
        help_text="Referencia a desc_articulos_clientes (dac_codi).",
    )
    supplier_discount_code = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Descuento proveedor",
        help_text="Referencia a desc_articulos_proveedores (dap_codi).",
    )
    extra_description = models.TextField(
        blank=True,
        verbose_name="Detalle adicional",
        help_text="Texto extendido (artrem_ddesc).",
    )
    stock_flag = models.CharField(
        max_length=1,
        blank=True,
        verbose_name="Indicador stock",
        help_text="Bandera legacy para control de stock (artrem_sstock).",
    )
    order_detail_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Detalle pedido",
        help_text="Código de renglón de pedido (artped_codi).",
    )
    is_invoiced = models.BooleanField(
        default=False,
        verbose_name="Facturado",
        help_text="Marca si el renglón fue facturado (facturado).",
    )

    class Meta:
        verbose_name = "Detalle de remito"
        verbose_name_plural = "Detalles de remito"
        indexes = [
            models.Index(fields=["product_legacy_id"]),
        ]

    def __str__(self) -> str:
        product_code = self.product.code if self.product and self.product.code else self.product_legacy_id
        return f"Remito {self.delivery_note_id} - {product_code or 'sin producto'}"
