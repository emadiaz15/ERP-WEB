from django.db import models

from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product


class StockHistory(BaseModel):
    """Movimiento histórico de stock, equivalente a HISTOSTOCK."""

    class MovementType(models.TextChoices):
        ADJUSTMENT = "adjustment", "Ajuste"
        INVENTORY = "inventory", "Inventario"
        RECEIPT = "receipt", "Recepción"
        SHIPMENT = "shipment", "Remito"
        SALE = "sale", "Venta"
        PURCHASE = "purchase", "Compra"
        OTHER = "other", "Otro"

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="%(class)s_records",
        related_query_name="%(class)s_record",
        verbose_name="Producto",
    )
    movement_type = models.CharField(max_length=32, choices=MovementType.choices, verbose_name="Tipo de movimiento")
    movement_date = models.DateField(verbose_name="Fecha del movimiento")
    movement_time = models.TimeField(null=True, blank=True, verbose_name="Hora del movimiento")
    previous_quantity = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name="Cantidad anterior")
    quantity_delta = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="Movimiento")
    resulting_quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="Cantidad resultante")
    observations = models.TextField(blank=True, verbose_name="Observaciones")
    detail = models.TextField(blank=True, verbose_name="Detalle")
    adjustment = models.ForeignKey(
        "inventory_adjustments.StockAdjustment",
        on_delete=models.SET_NULL,
        related_name="history_entries",
        null=True,
        blank=True,
    )
    inventory_count = models.ForeignKey(
        "inventory_adjustments.InventoryCount",
        on_delete=models.SET_NULL,
        related_name="history_entries",
        null=True,
        blank=True,
    )
    legacy_id = models.IntegerField(null=True, blank=True, verbose_name="ID legacy")

    class Meta:
        verbose_name = "Histórico de stock"
        verbose_name_plural = "Históricos de stock"
        ordering = ["-movement_date", "-id"]

    def __str__(self) -> str:
        return f"HIST-{self.id or 'new'}-{self.product_id}"
