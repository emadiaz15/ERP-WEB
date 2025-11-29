from datetime import time

from django.conf import settings
from django.db import models

from apps.customers.models import Customer
from apps.financial.choices import CurrencyChoices
from apps.logistics.choices import ShipmentMode, ShipmentStatus
from apps.products.models.base_model import BaseModel
from apps.orders.choices import (
    DiscountApplication,
    OrderOrigin,
    OrderPriority,
    OrderStatus,
)


class CustomerOrder(BaseModel):
    """Pedido de cliente alineado con la tabla legacy ``pedidos``."""

    legacy_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="ID legacy")
    number = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Número de pedido",
        help_text="Identificador formateado (pto-nro) usado en reportes",
    )
    reference_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Referencia externa",
        help_text="Referencias adicionales: presupuesto, marketplace, etc.",
    )
    quotation_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Presupuesto legacy",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
        verbose_name="Cliente",
    )
    salesperson = models.ForeignKey(
        "sales.SalesRepresentative",
        on_delete=models.SET_NULL,
        related_name="customer_orders",
        null=True,
        blank=True,
        verbose_name="Vendedor",
    )
    customer_snapshot_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre snapshot",
    )
    customer_snapshot_tax_id = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="CUIT snapshot",
    )
    salesperson_snapshot_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Vendedor snapshot",
    )
    salesperson_snapshot_code = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Código vendedor snapshot",
    )
    salesperson_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID legacy vendedor",
    )
    issue_date = models.DateField(verbose_name="Fecha del pedido", null=True, blank=True)
    issue_time = models.TimeField(
        default=time(hour=23, minute=59, second=59),
        verbose_name="Hora pedido",
    )
    expected_shipping_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha estimada despacho",
    )
    commitment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Compromiso con el cliente",
    )
    finalization_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha cierre",
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        verbose_name="Estado",
    )
    fulfillment_status = models.CharField(
        max_length=20,
        choices=ShipmentStatus.choices,
        default=ShipmentStatus.PENDING,
        verbose_name="Estado logístico",
    )
    priority = models.CharField(
        max_length=20,
        choices=OrderPriority.choices,
        default=OrderPriority.NORMAL,
        verbose_name="Prioridad",
    )
    origin = models.CharField(
        max_length=20,
        choices=OrderOrigin.choices,
        default=OrderOrigin.MANUAL,
        verbose_name="Origen",
    )
    shipment_mode = models.CharField(
        max_length=20,
        choices=ShipmentMode.choices,
        default=ShipmentMode.PICKUP,
        verbose_name="Modalidad de entrega",
    )
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.ARS,
        verbose_name="Moneda",
    )
    exchange_rate = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=1,
        verbose_name="Cotización",
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
    surcharge_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Recargos",
    )
    net_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name="Importe neto",
    )
    tax_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name="Impuestos",
    )
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name="Total",
    )
    balance_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name="Saldo pendiente",
    )
    iva_condition_code = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Condición IVA legacy",
    )
    transport_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Transporte legacy",
    )
    transport_notes = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Notas de transporte",
    )
    prepared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="prepared_orders",
        null=True,
        blank=True,
        verbose_name="Preparado por",
    )
    prepared_by_snapshot = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Preparador snapshot",
    )
    prepared_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de preparación")
    delivery_instructions = models.TextField(blank=True, verbose_name="Instrucciones de entrega")
    notes = models.TextField(blank=True, verbose_name="Observaciones")
    internal_notes = models.TextField(blank=True, verbose_name="Notas internas")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Metadata adicional")

    class Meta:
        verbose_name = "Pedido de cliente"
        verbose_name_plural = "Pedidos de clientes"
        ordering = ["-issue_date", "-created_at"]

    def __str__(self) -> str:
        number = self.number or self.legacy_id or "new"
        return f"Pedido {number}"

    @property
    def has_pending_delivery(self) -> bool:
        return self.fulfillment_status not in (ShipmentStatus.DELIVERED,)

    def mark_completed(self, save: bool = True) -> None:
        self.status = OrderStatus.COMPLETED
        self.fulfillment_status = ShipmentStatus.DELIVERED
        if save:
            self.save(update_fields=["status", "fulfillment_status", "modified_at"])
