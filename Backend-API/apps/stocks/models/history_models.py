from django.db import models
from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product
from apps.products.models.supplier_product_model import SupplierProduct


class ProductStockHistory(BaseModel):
    """Histórico de movimientos de stock por producto.

    Mapea la tabla legacy ``histostock`` pero se apoya en la lógica
    de ``StockEvent``. Puede usarse como tabla de auditoría detallada
    para análisis e integraciones externas.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="%(class)s_records",
        related_query_name="%(class)s_record",
        verbose_name="Producto",
        null=True,
        blank=True,
    )
    date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha",
    )
    time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Hora",
    )
    movement_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Tipo de movimiento",
        help_text="Tipo de movimiento de stock (hs_tipmov).",
    )
    previous_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Stock anterior",
    )
    quantity_change = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Cantidad",
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Saldo resultante",
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observaciones",
    )
    detail = models.TextField(
        null=True,
        blank=True,
        verbose_name="Detalle",
    )

    class Meta:
        verbose_name = "Histórico de Stock de Producto"
        verbose_name_plural = "Históricos de Stock de Producto"
        ordering = ["-date", "-time", "-created_at"]

    def __str__(self) -> str:
        return f"Histórico prod {self.product_id} - {self.date} {self.time}"


class SupplierCostHistory(BaseModel):
    """Histórico de costos por proveedor y producto.

    Mapea la tabla legacy ``histocosto`` (histo_*, artpro_codi, moneda).
    Se apoya en ``SupplierProduct`` para mantener la referencia
    proveedor-producto.
    """

    supplier_product = models.ForeignKey(
        SupplierProduct,
        on_delete=models.CASCADE,
        related_name="cost_history",
        verbose_name="Configuración proveedor-producto",
    )
    date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha del cambio",
    )
    previous_cost = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Costo anterior",
    )
    new_cost = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Costo nuevo",
    )
    previous_sale_cost = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Costo de venta anterior",
    )
    new_sale_cost = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Costo de venta nuevo",
    )
    currency = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name="Moneda",
        help_text="Moneda del costo (moneda).",
    )

    class Meta:
        verbose_name = "Histórico de Costo de Proveedor"
        verbose_name_plural = "Históricos de Costo de Proveedor"
        ordering = ["-date", "-created_at"]

    def __str__(self) -> str:
        return f"Histórico costo {self.supplier_product_id} - {self.date}"
