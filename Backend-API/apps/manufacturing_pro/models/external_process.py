from django.db import models
from django.utils import timezone

from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product
from apps.suppliers.models import Supplier
from apps.manufacturing_pro.choices import ExternalProcessType, ExternalProcessStatus, MovementType


class ExternalProcess(BaseModel):
    order = models.ForeignKey(
        "manufacturing_pro.ManufacturingOrder",
        on_delete=models.CASCADE,
        related_name="external_processes",
        verbose_name="Orden",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="external_processes",
        verbose_name="Proveedor",
    )
    process_type = models.CharField(
        max_length=20,
        choices=ExternalProcessType.choices,
        default=ExternalProcessType.OTHER,
        verbose_name="Tipo",
    )
    status_label = models.CharField(
        max_length=20,
        choices=ExternalProcessStatus.choices,
        default=ExternalProcessStatus.PLANNED,
        verbose_name="Estado",
    )
    expected_quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    total_sent_quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    total_received_quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    send_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    estimated_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    reference_number = models.CharField(max_length=60, blank=True)
    observations = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Proceso externo"
        verbose_name_plural = "Procesos externos"
        ordering = ["-send_date", "-created_at"]

    def mark_sent(self, *, user=None):
        self.status_label = ExternalProcessStatus.SENT
        if not self.send_date:
            self.send_date = timezone.now().date()
        self.save(user=user)

    def mark_received(self, *, user=None):
        self.status_label = ExternalProcessStatus.RECEIVED
        self.received_date = timezone.now().date()
        self.save(user=user)


class ExternalProcessDetail(BaseModel):
    external_process = models.ForeignKey(
        ExternalProcess,
        on_delete=models.CASCADE,
        related_name="details",
        verbose_name="Proceso",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        related_name="external_process_details",
        null=True,
        blank=True,
        verbose_name="Producto",
    )
    supply_item = models.ForeignKey(
        "manufacturing_pro.SupplyItem",
        on_delete=models.SET_NULL,
        related_name="external_process_details",
        null=True,
        blank=True,
        verbose_name="Insumo",
    )
    description = models.CharField(max_length=255, blank=True)
    quantity_sent = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_received = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    unit = models.CharField(max_length=10, blank=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Detalle proceso externo"
        verbose_name_plural = "Detalles procesos externos"


class ExternalProcessMovement(BaseModel):
    detail = models.ForeignKey(
        ExternalProcessDetail,
        on_delete=models.CASCADE,
        related_name="movements",
        verbose_name="Detalle",
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices,
        default=MovementType.ISSUE,
    )
    movement_date = models.DateTimeField(default=timezone.now)
    quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    reference_document = models.CharField(max_length=120, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Movimiento proceso externo"
        verbose_name_plural = "Movimientos proceso externo"
        ordering = ["-movement_date", "-id"]
