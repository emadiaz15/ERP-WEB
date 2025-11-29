from __future__ import annotations

from decimal import Decimal

from django.db import models

from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product


class BillOfMaterials(BaseModel):
    """Plantilla de materiales y costos para fabricar un producto."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        ACTIVE = "active", "Activa"
        ARCHIVED = "archived", "Archivada"

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="boms",
        verbose_name="Producto fabricado",
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código",
        help_text="Identificador único de la lista de materiales.",
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre descriptivo",
    )
    version = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="Versión",
        help_text="Versión o revisión de la lista de materiales.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Estado",
    )
    effective_from = models.DateField(
        null=True,
        blank=True,
        verbose_name="Vigente desde",
    )
    effective_to = models.DateField(
        null=True,
        blank=True,
        verbose_name="Vigente hasta",
    )
    cost_estimate = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Costo estimado",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notas",)

    class Meta:
        verbose_name = "Lista de Materiales"
        verbose_name_plural = "Listas de Materiales"
        ordering = ["product", "code"]

    def __str__(self) -> str:
        return f"{self.product} - {self.code}"


class BillOfMaterialsItem(BaseModel):
    """Detalle de insumos y costos asociados a una lista de materiales."""

    class InputType(models.TextChoices):
        RAW_MATERIAL = "raw_material", "Materia prima"
        CONSUMABLE = "consumable", "Consumible"
        LABOR = "labor", "Mano de obra"
        SERVICE = "service", "Servicio externo"
        PACKAGING = "packaging", "Empaque"
        OTHER = "other", "Otro"

    bom = models.ForeignKey(
        BillOfMaterials,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Lista de Materiales",
    )
    component = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="manufacturing_components",
        verbose_name="Componente",
    )
    input_type = models.CharField(
        max_length=20,
        choices=InputType.choices,
        default=InputType.RAW_MATERIAL,
        verbose_name="Tipo de insumo",
    )
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        verbose_name="Cantidad requerida",
    )
    unit_of_measure = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="Unidad de medida",
    )
    unit_cost = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=Decimal("0"),
        verbose_name="Costo unitario",
    )
    scrap_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Merma (%)",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notas",
    )

    class Meta:
        verbose_name = "Elemento de Lista de Materiales"
        verbose_name_plural = "Elementos de Lista de Materiales"
        ordering = ["bom", "component__name"]
        unique_together = ("bom", "component")

    def __str__(self) -> str:
        return f"{self.bom.code} - {self.component.code}"
