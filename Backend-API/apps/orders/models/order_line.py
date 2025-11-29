from django.db import models

from apps.financial.choices import CurrencyChoices
from apps.logistics.choices import ShipmentStatus
from apps.manufacturing_pro.models import ManufacturingOrder
from apps.orders.choices import DiscountApplication
from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product


class CustomerOrderLine(BaseModel):
    """Detalle del pedido (tabla legacy ``pedidos_articulos``)."""

    order = models.ForeignKey(
        "orders.CustomerOrder",
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name="Pedido",
    )
    legacy_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="ID legacy")
    legacy_sequence = models.IntegerField(null=True, blank=True, verbose_name="Secuencia legacy")
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        related_name="order_lines",
        null=True,
        blank=True,
        verbose_name="Producto",
    )
    product_snapshot_code = models.CharField(max_length=40, blank=True, verbose_name="Código producto")
    product_snapshot_name = models.CharField(max_length=255, blank=True, verbose_name="Descripción snapshot")
    unit_of_measure = models.CharField(max_length=20, blank=True, verbose_name="Unidad")
    quantity_ordered = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=0,
        verbose_name="Cantidad pedida",
    )
    quantity_allocated = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=0,
        verbose_name="Cantidad reservada",
    )
    quantity_delivered = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=0,
        verbose_name="Cantidad despachada",
    )
    quantity_invoiced = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=0,
        verbose_name="Cantidad facturada",
    )
    unit_price = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=0,
        verbose_name="Precio unitario",
    )
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.ARS,
        verbose_name="Moneda",
    )
    discount_type = models.CharField(
        max_length=20,
        choices=DiscountApplication.choices,
        default=DiscountApplication.NONE,
        verbose_name="Tipo descuento",
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="% descuento",
    )
    discount_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Monto descuento",
    )
    tax_rate = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        default=0,
        verbose_name="Alicuota",
    )
    tax_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Impuesto",
    )
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name="Total línea",
    )
    fulfillment_status = models.CharField(
        max_length=20,
        choices=ShipmentStatus.choices,
        default=ShipmentStatus.PENDING,
        verbose_name="Estado logística línea",
    )
    manufacturing_order = models.ForeignKey(
        ManufacturingOrder,
        on_delete=models.SET_NULL,
        related_name="order_lines",
        null=True,
        blank=True,
        verbose_name="Orden de fabricación vinculada",
    )
    allow_backorder = models.BooleanField(default=False, verbose_name="Permite backorder")
    notes = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Detalle de pedido"
        verbose_name_plural = "Detalles de pedido"
        ordering = ["order", "legacy_sequence", "id"]

    def __str__(self) -> str:
        return f"Línea {self.id or 'new'} de {self.order_id}"

    @property
    def pending_quantity(self):
        return max(self.quantity_ordered - self.quantity_delivered, 0)
