from django.db import models
from django.utils import timezone

from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product
from apps.manufacturing_pro.choices import (
    ManufacturingOrderStatus,
    ManufacturingPriority,
    OperationStatus,
)


class ManufacturingOrder(BaseModel):
    """Orden de fabricación principal (legacy ``fabricados`` / ``orden_fabricacion``)."""

    code = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="Código")
    legacy_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="ID legacy")
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="manufacturing_orders",
        verbose_name="Producto terminado",
    )
    sales_order = models.ForeignKey(
        "sales.SalesOrder",
        on_delete=models.SET_NULL,
        related_name="manufacturing_orders",
        null=True,
        blank=True,
        verbose_name="Pedido origen",
    )
    purchase_order = models.ForeignKey(
        "purchases.PurchaseOrder",
        on_delete=models.SET_NULL,
        related_name="manufacturing_orders",
        null=True,
        blank=True,
        verbose_name="Orden de compra asociada",
    )
    status_label = models.CharField(
        max_length=20,
        choices=ManufacturingOrderStatus.choices,
        default=ManufacturingOrderStatus.PLANNED,
        verbose_name="Estado",
    )
    priority = models.CharField(
        max_length=10,
        choices=ManufacturingPriority.choices,
        default=ManufacturingPriority.NORMAL,
        verbose_name="Prioridad",
    )
    planned_quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0, verbose_name="Cantidad planificada")
    produced_quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0, verbose_name="Cantidad producida")
    scrap_quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0, verbose_name="Merma")
    unit_cost_estimated = models.DecimalField(max_digits=18, decimal_places=4, default=0, verbose_name="Costo unitario estimado")
    unit_cost_actual = models.DecimalField(max_digits=18, decimal_places=4, default=0, verbose_name="Costo unitario real")
    total_cost_estimated = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Costo total estimado")
    total_cost_actual = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Costo total real")
    planned_start_date = models.DateField(null=True, blank=True, verbose_name="Inicio planificado")
    planned_end_date = models.DateField(null=True, blank=True, verbose_name="Fin planificado")
    actual_start_date = models.DateField(null=True, blank=True, verbose_name="Inicio real")
    actual_end_date = models.DateField(null=True, blank=True, verbose_name="Fin real")
    quality_notes = models.TextField(blank=True, verbose_name="Notas de calidad")
    observations = models.TextField(blank=True, verbose_name="Observaciones")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Orden de fabricación"
        verbose_name_plural = "Órdenes de fabricación"
        ordering = ["-planned_start_date", "-created_at"]

    def start(self, *, user=None):
        if not self.actual_start_date:
            self.actual_start_date = timezone.now().date()
        self.status_label = ManufacturingOrderStatus.IN_PROGRESS
        self.save(user=user)

    def finish(self, *, user=None):
        self.actual_end_date = timezone.now().date()
        self.status_label = ManufacturingOrderStatus.COMPLETED
        self.save(user=user)


class ManufacturingOrderMaterial(BaseModel):
    """Lista de materiales/consumos esperados y reales por orden."""

    order = models.ForeignKey(
        ManufacturingOrder,
        on_delete=models.CASCADE,
        related_name="materials",
        verbose_name="Orden",
    )
    supply_item = models.ForeignKey(
        "manufacturing_pro.SupplyItem",
        on_delete=models.SET_NULL,
        related_name="order_materials",
        null=True,
        blank=True,
        verbose_name="Insumo",
    )
    product_component = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        related_name="order_component_materials",
        null=True,
        blank=True,
        verbose_name="Producto componente",
    )
    description = models.CharField(max_length=255, blank=True)
    planned_quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    consumed_quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    unit = models.CharField(max_length=10, blank=True)
    is_optional = models.BooleanField(default=False)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Material de orden"
        verbose_name_plural = "Materiales de orden"
        unique_together = (
            "order",
            "supply_item",
            "product_component",
            "description",
        )


class ManufacturingOperation(BaseModel):
    order = models.ForeignKey(
        ManufacturingOrder,
        on_delete=models.CASCADE,
        related_name="operations",
        verbose_name="Orden",
    )
    name = models.CharField(max_length=120, verbose_name="Operación")
    sequence = models.PositiveIntegerField(default=10)
    workstation = models.CharField(max_length=120, blank=True)
    instructions = models.TextField(blank=True)
    estimated_duration_minutes = models.PositiveIntegerField(default=0)
    status_label = models.CharField(
        max_length=20,
        choices=OperationStatus.choices,
        default=OperationStatus.PENDING,
    )
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    responsible_name = models.CharField(max_length=120, blank=True)

    class Meta:
        verbose_name = "Operación"
        verbose_name_plural = "Operaciones"
        ordering = ["sequence"]

    def mark_running(self, *, user=None):
        self.status_label = OperationStatus.RUNNING
        if not self.started_at:
            self.started_at = timezone.now()
        self.save(user=user)

    def mark_finished(self, *, user=None):
        self.status_label = OperationStatus.FINISHED
        self.finished_at = timezone.now()
        self.save(user=user)


class ManufacturingOperationLog(BaseModel):
    operation = models.ForeignKey(
        ManufacturingOperation,
        on_delete=models.CASCADE,
        related_name="logs",
        verbose_name="Operación",
    )
    status_snapshot = models.CharField(max_length=20, choices=OperationStatus.choices)
    message = models.TextField(blank=True)
    logged_at = models.DateTimeField(default=timezone.now)
    author_name = models.CharField(max_length=120, blank=True)

    class Meta:
        verbose_name = "Log de operación"
        verbose_name_plural = "Logs de operación"
        ordering = ["-logged_at", "-id"]
