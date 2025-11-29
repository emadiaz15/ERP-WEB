from django.db import models

from apps.logistics.choices import ShipmentMode, ShipmentStatus
from apps.products.models.base_model import BaseModel


class OrderTransportLeg(BaseModel):
    """Relaciona un pedido con un envío del módulo de logística."""

    order = models.ForeignKey(
        "orders.CustomerOrder",
        on_delete=models.CASCADE,
        related_name="transport_legs",
        verbose_name="Pedido",
    )
    shipment = models.ForeignKey(
        "logistics.LogisticsShipment",
        on_delete=models.CASCADE,
        related_name="order_links",
        verbose_name="Envío",
    )
    carrier = models.ForeignKey(
        "logistics.Carrier",
        on_delete=models.SET_NULL,
        related_name="order_legs",
        null=True,
        blank=True,
        verbose_name="Transportista",
    )
    shipment_mode = models.CharField(
        max_length=20,
        choices=ShipmentMode.choices,
        default=ShipmentMode.THIRD_PARTY,
        verbose_name="Modalidad",
    )
    carrier_snapshot_name = models.CharField(max_length=255, blank=True, verbose_name="Transportista snapshot")
    contact_name = models.CharField(max_length=255, blank=True, verbose_name="Contacto")
    contact_phone = models.CharField(max_length=50, blank=True, verbose_name="Teléfono")
    pickup_address_override = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Dirección retiro (override)",
    )
    delivery_address_override = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Dirección entrega (override)",
    )
    scheduled_departure = models.DateTimeField(null=True, blank=True, verbose_name="Salida planificada")
    scheduled_arrival = models.DateTimeField(null=True, blank=True, verbose_name="Arribo planificado")
    actual_departure = models.DateTimeField(null=True, blank=True, verbose_name="Salida real")
    actual_arrival = models.DateTimeField(null=True, blank=True, verbose_name="Arribo real")
    status = models.CharField(
        max_length=20,
        choices=ShipmentStatus.choices,
        default=ShipmentStatus.PENDING,
        verbose_name="Estado",
    )
    freight_terms = models.CharField(max_length=120, blank=True, verbose_name="Condiciones de flete")
    freight_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Costo flete",
    )
    observations = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Tramo de transporte"
        verbose_name_plural = "Transportes de pedido"
        ordering = ["scheduled_departure", "id"]

    def __str__(self) -> str:
        return f"Transporte {self.carrier_name or self.id} ({self.order_id})"
