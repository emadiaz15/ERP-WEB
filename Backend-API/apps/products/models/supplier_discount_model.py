from django.db import models

from apps.products.models.base_model import BaseModel
from apps.products.models.supplier_product_model import SupplierProduct


class SupplierProductDescription(BaseModel):
    """Alternative descriptions for a supplier-product pair.

    Mapea la tabla legacy ``desc_articulos_proveedores``:
    - dap_codi   (PK)         → id de Django
    - artpro_codi (FK)        → ``supplier_product``
    - dap_desc   (varchar)    → ``description``
    """

    supplier_product = models.ForeignKey(
        SupplierProduct,
        on_delete=models.CASCADE,
        related_name="descriptions",
        verbose_name="Producto-proveedor",
    )
    description = models.CharField(
        max_length=255,
        verbose_name="Descripción",
        help_text="Descripción alternativa del artículo para este proveedor (dap_desc).",
    )

    class Meta:
        verbose_name = "Descripción de producto por proveedor"
        verbose_name_plural = "Descripciones de producto por proveedor"
        ordering = ["supplier_product", "description"]

    def __str__(self) -> str:
        return f"{self.supplier_product_id} - {self.description}"


class SupplierProductDiscount(BaseModel):
    """Discount configuration for a supplier-product.

    Mapea la tabla legacy ``articulos_proveedores_descuentos``:
    - arpdes_codi (PK)     → id de Django
    - artpro_codi (FK)     → ``supplier_product``
    - dto_codi    (int)    → ``discount_legacy_id`` (referencia a tabla ``descuentos``)
    - negativo    (int)    → ``is_negative`` (0/1)
    """

    supplier_product = models.ForeignKey(
        SupplierProduct,
        on_delete=models.CASCADE,
        related_name="discounts",
        verbose_name="Producto-proveedor",
    )
    discount_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID legacy de descuento",
        help_text="Identificador legacy del descuento (dto_codi → descuentos).",
    )
    is_negative = models.BooleanField(
        default=False,
        verbose_name="Descuento negativo",
        help_text="Indica si el descuento es negativo (campo negativo).",
    )

    class Meta:
        verbose_name = "Descuento de producto por proveedor"
        verbose_name_plural = "Descuentos de producto por proveedor"
        ordering = ["supplier_product", "discount_legacy_id"]

    def __str__(self) -> str:
        return f"{self.supplier_product_id} - dto {self.discount_legacy_id} ({'neg' if self.is_negative else 'pos'})"
