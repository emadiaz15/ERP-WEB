from __future__ import annotations

from decimal import Decimal

from django.db import models

from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product

from .bill_of_materials import BillOfMaterials, BillOfMaterialsItem


class WorkOrder(BaseModel):
    """Orden de trabajo para fabricar un producto."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        PLANNED = "planned", "Planificada"
        IN_PROGRESS = "in_progress", "En producción"
        EXTERNAL_TREATMENT = "external_treatment", "En tratamiento externo"
        COMPLETED = "completed", "Completada"
        CANCELLED = "cancelled", "Cancelada"

    class Priority(models.IntegerChoices):
        LOW = 5, "Baja"
        NORMAL = 3, "Normal"
        HIGH = 1, "Alta"

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código",
        help_text="Identificador único de la orden de trabajo.",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="work_orders",
        verbose_name="Producto a fabricar",
    )
    bill_of_materials = models.ForeignKey(
        BillOfMaterials,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_orders",
        verbose_name="Lista de materiales",
    )
    quantity_planned = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Cantidad planificada",
    )
    quantity_produced = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Cantidad producida",
    )
    unit_of_measure = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="Unidad de medida",
    )
    priority = models.IntegerField(
        choices=Priority.choices,
        default=Priority.NORMAL,
        verbose_name="Prioridad",
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Estado",
    )
    planned_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Inicio planificado",
    )
    planned_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin planificado",
    )
    actual_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Inicio real",
    )
    actual_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin real",
    )
    source_location = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Depósito origen",
    )
    destination_location = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Depósito destino",
    )
    external_reference = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Referencia externa",
    )
    cost_estimate = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Costo estimado",
    )
    cost_actual = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Costo real",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notas",
    )

    class Meta:
        verbose_name = "Orden de Trabajo"
        verbose_name_plural = "Órdenes de Trabajo"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"OT {self.code} - {self.product}"


class WorkOrderItem(BaseModel):
    """Consumo planificado y real de componentes asociados a la orden."""

    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Orden de trabajo",
    )
    component = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="work_order_components",
        verbose_name="Componente",
    )
    bom_item = models.ForeignKey(
        BillOfMaterialsItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_order_items",
        verbose_name="Elemento BOM",
    )
    quantity_planned = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        verbose_name="Cantidad planificada",
    )
    quantity_used = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=Decimal("0"),
        verbose_name="Cantidad utilizada",
    )
    cost_allocated = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Costo asignado",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notas",
    )

    class Meta:
        verbose_name = "Item de Orden de Trabajo"
        verbose_name_plural = "Items de Orden de Trabajo"
        unique_together = ("work_order", "component")
        ordering = ["work_order", "component__name"]

    def __str__(self) -> str:
        return f"{self.work_order.code} - {self.component.code}"


class WorkOrderLog(BaseModel):
    """Registro de eventos y seguimientos asociados a la orden."""

    class EventType(models.TextChoices):
        STATUS_CHANGE = "status_change", "Cambio de estado"
        PROGRESS_UPDATE = "progress_update", "Avance reportado"
        NOTE = "note", "Nota"
        QUALITY = "quality", "Calidad"
        WARNING = "warning", "Alerta"

    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name="logs",
        verbose_name="Orden de trabajo",
    )
    event_type = models.CharField(
        max_length=32,
        choices=EventType.choices,
        default=EventType.NOTE,
        verbose_name="Tipo de evento",
    )
    message = models.TextField(
        verbose_name="Descripción",
    )
    extra_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos adicionales",
    )

    class Meta:
        verbose_name = "Log de Orden de Trabajo"
        verbose_name_plural = "Logs de Órdenes de Trabajo"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.work_order.code} - {self.event_type}"
