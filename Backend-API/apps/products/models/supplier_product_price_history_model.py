from django.db import models
from django.conf import settings

from apps.products.models.base_model import BaseModel
from apps.products.models.supplier_product_model import SupplierProduct


class SupplierProductPriceHistory(BaseModel):
    """Historical record of supplier product prices.

    This model tracks all price changes for supplier products over time,
    allowing for historical analysis, price trend reporting, and auditing.

    Every time a SupplierProduct's cost or sale_cost is updated, a new
    record is created in this table. The current active price is the one
    with valid_to=NULL.

    Fields:
    - supplier_product: Reference to the SupplierProduct being tracked
    - cost: Purchase cost from supplier at this point in time
    - sale_cost: Sale cost reference at this point in time
    - currency: Currency code (P/D, USD, etc.)
    - exchange_rate_ref: Reference exchange rate if applicable
    - valid_from: Date from which this price is/was valid
    - valid_to: Date until which this price was valid (NULL if current)
    - changed_by: User who made the price change
    - notes: Optional notes about the price change
    """

    # ------------------------------------------------------------------
    # Relación con el producto de proveedor
    # ------------------------------------------------------------------
    supplier_product = models.ForeignKey(
        SupplierProduct,
        on_delete=models.CASCADE,
        related_name="price_history",
        verbose_name="Producto de proveedor",
        help_text="Producto de proveedor al que pertenece este registro de precio.",
    )

    # ------------------------------------------------------------------
    # Campos de precio (snapshot del momento)
    # ------------------------------------------------------------------
    cost = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Costo de proveedor",
        help_text="Costo de compra en este momento histórico.",
    )

    sale_cost = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Costo de venta",
        help_text="Costo de venta de referencia en este momento histórico.",
    )

    # ------------------------------------------------------------------
    # Moneda y cotización (snapshot del momento)
    # ------------------------------------------------------------------
    currency = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        verbose_name="Moneda",
        help_text="Código de moneda vigente en este momento (P/D, USD, etc.).",
    )

    exchange_rate_ref = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Cotización de referencia",
        help_text="Tipo de cambio de referencia en el momento del registro.",
    )

    # ------------------------------------------------------------------
    # Validez temporal
    # ------------------------------------------------------------------
    valid_from = models.DateTimeField(
        verbose_name="Válido desde",
        help_text="Fecha y hora desde la cual este precio es/era válido.",
    )

    valid_to = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Válido hasta",
        help_text="Fecha y hora hasta la cual este precio fue válido (NULL si es el precio actual).",
    )

    # ------------------------------------------------------------------
    # Usuario que realizó el cambio
    # ------------------------------------------------------------------
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supplier_price_changes",
        verbose_name="Modificado por",
        help_text="Usuario que registró este cambio de precio.",
    )

    # ------------------------------------------------------------------
    # Notas opcionales
    # ------------------------------------------------------------------
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Notas",
        help_text="Comentarios opcionales sobre el cambio de precio (ej: 'Aumento por inflación', 'Descuento por volumen').",
    )

    class Meta:
        verbose_name = "Histórico de precio de proveedor"
        verbose_name_plural = "Históricos de precios de proveedor"
        ordering = ["-valid_from"]
        indexes = [
            models.Index(fields=["supplier_product", "-valid_from"]),
            models.Index(fields=["valid_from", "valid_to"]),
        ]

    def __str__(self) -> str:
        """Readable representation of price history record."""
        product_name = self.supplier_product.product.name if self.supplier_product and self.supplier_product.product else "Producto"
        date_str = self.valid_from.strftime("%Y-%m-%d") if self.valid_from else "Sin fecha"
        cost_str = f"${self.cost}" if self.cost else "Sin costo"
        return f"{product_name} - {cost_str} @ {date_str}"

    def is_current(self) -> bool:
        """Check if this price record is the current active price."""
        return self.valid_to is None
