from __future__ import annotations

from decimal import Decimal

from django.db import models

from apps.products.models.base_model import BaseModel

from .work_order import WorkOrder


class ExternalTreatmentOrder(BaseModel):
    """Orden asociada al envío de piezas a un tratamiento externo (galvanizado, pintura, etc.)."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Programada"
        IN_TRANSIT = "in_transit", "En tránsito"
        PARTIAL_RETURN = "partial_return", "Retorno parcial"
        COMPLETED = "completed", "Completada"
        CANCELLED = "cancelled", "Cancelada"

    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name="treatment_orders",
        verbose_name="Orden de trabajo",
    )
    provider_name = models.CharField(
        max_length=255,
        verbose_name="Proveedor",
    )
    provider_reference = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Referencia del proveedor",
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.SCHEDULED,
        verbose_name="Estado",
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de envío",
    )
    expected_return_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Retorno estimado",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de finalización",
    )
    service_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Costo del servicio",
    )
    freight_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Costo de flete",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notas",
    )

    class Meta:
        verbose_name = "Orden de Tratamiento Externo"
        verbose_name_plural = "Órdenes de Tratamiento Externo"
        ordering = ["-sent_at", "work_order__code"]

    def __str__(self) -> str:
        return f"Tratamiento {self.provider_name} - {self.work_order.code}"


class ExternalTreatmentLot(BaseModel):
    """Envios parciales asociados a una orden de tratamiento externo."""

    treatment_order = models.ForeignKey(
        ExternalTreatmentOrder,
        on_delete=models.CASCADE,
        related_name="lots",
        verbose_name="Orden de tratamiento",
    )
    lot_code = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Código de lote",
    )
    quantity_sent = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Cantidad enviada",
    )
    quantity_received = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Cantidad recibida",
    )
    weight_kg = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Peso (kg)",
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de envío",
    )
    received_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de recepción",
    )
    remarks = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        verbose_name = "Lote de Tratamiento Externo"
        verbose_name_plural = "Lotes de Tratamiento Externo"
        ordering = ["treatment_order", "sent_at"]

    def __str__(self) -> str:
        return f"Lote {self.lot_code or 'sin código'} - {self.treatment_order}"
