from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from apps.products.models.base_model import BaseModel
from apps.financial.choices import CurrencyChoices
from apps.suppliers.models import Supplier
from apps.manufacturing_pro.choices import MovementType, SupplyUnit


class SupplyCategory(BaseModel):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=30, unique=True, null=True, blank=True)
    legacy_id = models.IntegerField(null=True, blank=True, db_index=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Rubro de insumo"
        verbose_name_plural = "Rubros de insumo"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class SupplyItem(BaseModel):
    category = models.ForeignKey(
        SupplyCategory,
        on_delete=models.PROTECT,
        related_name="supplies",
        null=True,
        blank=True,
        verbose_name="Rubro",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        related_name="supply_links",
        null=True,
        blank=True,
        verbose_name="Producto vinculado",
    )
    code = models.CharField(max_length=30, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    unit = models.CharField(
        max_length=10,
        choices=SupplyUnit.choices,
        default=SupplyUnit.UNIT,
        verbose_name="Unidad",
    )
    stock_quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    min_stock = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    cost_current = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    last_purchase_cost = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    last_purchase_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    legacy_id = models.IntegerField(null=True, blank=True, db_index=True)
    details = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class SupplyVendor(BaseModel):
    supply_item = models.ForeignKey(
        SupplyItem,
        on_delete=models.CASCADE,
        related_name="vendors",
        verbose_name="Insumo",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="supply_vendors",
        verbose_name="Proveedor",
    )
    preferred = models.BooleanField(default=False)
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.ARS,
    )
    cost = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    lead_time_days = models.PositiveIntegerField(default=0)
    last_purchase_at = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Proveedor de insumo"
        verbose_name_plural = "Proveedores de insumo"
        unique_together = ("supply_item", "supplier")


class SupplyCostHistory(BaseModel):
    supply_item = models.ForeignKey(
        SupplyItem,
        on_delete=models.CASCADE,
        related_name="cost_history",
        verbose_name="Insumo",
    )
    supply_vendor = models.ForeignKey(
        SupplyVendor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cost_history",
    )
    previous_cost = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    new_cost = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    currency = models.CharField(max_length=3, choices=CurrencyChoices.choices, default=CurrencyChoices.ARS)
    recorded_at = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Histórico costo insumo"
        verbose_name_plural = "Histórico costo insumo"
        ordering = ["-recorded_at"]


class SupplyStockMovement(BaseModel):
    supply_item = models.ForeignKey(
        SupplyItem,
        on_delete=models.CASCADE,
        related_name="stock_movements",
        verbose_name="Insumo",
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices,
        default=MovementType.CONSUMPTION,
    )
    quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    balance_after = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    movement_date = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=255, blank=True)

    reference_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    reference_object_id = models.PositiveIntegerField(null=True, blank=True)
    reference = GenericForeignKey("reference_content_type", "reference_object_id")

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Movimiento insumo"
        verbose_name_plural = "Movimientos insumo"
        ordering = ["-movement_date", "-id"]
        indexes = [
            models.Index(fields=["supply_item", "movement_date"]),
            models.Index(fields=["movement_type"]),
        ]
