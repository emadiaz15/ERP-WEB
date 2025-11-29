from django.db import models

from apps.financial.choices import CurrencyChoices
from apps.products.models.base_model import BaseModel
from apps.logistics.choices import (
    ServiceLevel,
    ShipmentDirection,
    ShipmentMode,
    ShipmentStatus,
    ShipmentCostType,
)


class LogisticsShipment(BaseModel):
    """Movimiento logístico generado por compras, ventas u otros módulos."""

    legacy_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="ID legacy")
    external_reference = models.CharField(max_length=120, blank=True, verbose_name="Referencia externa")
    carrier = models.ForeignKey(
        "logistics.Carrier",
        on_delete=models.SET_NULL,
        related_name="shipments",
        null=True,
        blank=True,
        verbose_name="Transportista",
    )
    carrier_snapshot_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Transportista snapshot",
    )
    direction = models.CharField(
        max_length=20,
        choices=ShipmentDirection.choices,
        default=ShipmentDirection.OUTBOUND,
        verbose_name="Dirección",
    )
    mode = models.CharField(
        max_length=20,
        choices=ShipmentMode.choices,
        default=ShipmentMode.THIRD_PARTY,
        verbose_name="Modalidad",
    )
    service_level = models.CharField(
        max_length=20,
        choices=ServiceLevel.choices,
        default=ServiceLevel.STANDARD,
        verbose_name="Nivel de servicio",
    )
    status = models.CharField(
        max_length=20,
        choices=ShipmentStatus.choices,
        default=ShipmentStatus.PENDING,
        verbose_name="Estado",
    )
    reference_module = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Módulo origen",
        help_text="orders, purchases, manufacturing, etc.",
    )
    reference_id = models.IntegerField(null=True, blank=True, verbose_name="ID referencia")
    tracking_code = models.CharField(max_length=120, blank=True, verbose_name="Tracking")
    pickup_address = models.CharField(max_length=255, blank=True, verbose_name="Dirección retiro")
    delivery_address = models.CharField(max_length=255, blank=True, verbose_name="Dirección entrega")
    planned_pickup = models.DateTimeField(null=True, blank=True, verbose_name="Retiro planificado")
    planned_delivery = models.DateTimeField(null=True, blank=True, verbose_name="Entrega planificada")
    actual_pickup = models.DateTimeField(null=True, blank=True, verbose_name="Retiro real")
    actual_delivery = models.DateTimeField(null=True, blank=True, verbose_name="Entrega real")
    total_weight = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True, verbose_name="Peso total")
    total_volume = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True, verbose_name="Volumen total")
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.ARS,
        verbose_name="Moneda",
    )
    estimated_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Costo estimado")
    actual_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Costo real")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Metadata adicional")

    class Meta:
        verbose_name = "Envío"
        verbose_name_plural = "Envíos"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Shipment {self.id} - {self.status}"


class ShipmentCostBreakdown(BaseModel):
    shipment = models.ForeignKey(
        LogisticsShipment,
        on_delete=models.CASCADE,
        related_name="cost_breakdowns",
        verbose_name="Envío",
    )
    cost_type = models.CharField(
        max_length=20,
        choices=ShipmentCostType.choices,
        default=ShipmentCostType.FREIGHT,
        verbose_name="Tipo costo",
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Importe")
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.ARS,
        verbose_name="Moneda",
    )
    notes = models.CharField(max_length=255, blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Detalle de costo de envío"
        verbose_name_plural = "Costos de envío"


class ShipmentTrackingEvent(BaseModel):
    shipment = models.ForeignKey(
        LogisticsShipment,
        on_delete=models.CASCADE,
        related_name="tracking_events",
        verbose_name="Envío",
    )
    status = models.CharField(
        max_length=20,
        choices=ShipmentStatus.choices,
        verbose_name="Estado",
    )
    event_time = models.DateTimeField(auto_now_add=True, verbose_name="Fecha evento")
    location_description = models.CharField(max_length=255, blank=True, verbose_name="Ubicación")
    details = models.CharField(max_length=255, blank=True, verbose_name="Detalle")
    actor = models.CharField(max_length=120, blank=True, verbose_name="Actor")

    class Meta:
        verbose_name = "Evento de tracking"
        verbose_name_plural = "Eventos de tracking"
        ordering = ["-event_time"]

    def __str__(self) -> str:
        return f"{self.shipment_id} - {self.status}"
