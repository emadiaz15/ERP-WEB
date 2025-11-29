# apps/products/models/subproduct_model.py
from django.db.models.functions import Lower 
from decimal import Decimal
from django.db import models
from django.db.models import Q, F
from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product

class Subproduct(BaseModel):
    brand = models.CharField(max_length=100, null=True, blank=True, verbose_name="Marca")

    number_coil = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Número de Bobina",
    )

    initial_enumeration = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Enumeración Inicial")
    final_enumeration   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Enumeración Final")
    gross_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Peso Bruto (kg)")
    net_weight   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Peso Neto (kg)")
    initial_stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Cantidad de Stock Inicial")
    location = models.CharField(
        max_length=100,
        choices=[("Deposito Principal", "Depósito Principal"), ("Deposito Secundario", "Depósito Secundario")],
        default="Deposito Principal",
        verbose_name="Ubicación de Stock Inicial",
    )
    technical_sheet_photo = models.ImageField(upload_to="technical_sheets/", null=True, blank=True, verbose_name="Foto Ficha Técnica")
    form_type = models.CharField(
        max_length=50,
        choices=[("Bobina", "Bobina"), ("Rollo", "Rollo")],
        default="Bobina",
        verbose_name="Tipo de Forma",
    )
    observations = models.TextField(null=True, blank=True, verbose_name="Observaciones")

    parent = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="subproducts", null=False, blank=False, verbose_name="Producto Padre"
    )

    def save(self, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        is_new = self.pk is None
        if is_new:
            try:
                qty = Decimal(self.initial_stock_quantity or 0)
            except Exception:
                qty = Decimal("0")
            self.status = qty > 0
            logger.debug(f"Subproduct({self.pk}) new -> status={self.status} by initial_stock={self.initial_stock_quantity}")
        super().save(*args, **kwargs)


    class Meta:
        verbose_name = "Subproducto"
        verbose_name_plural = "Subproductos"
        ordering = ["-created_at"]
        constraints = [
            # Unicidad por padre + number_coil (case-insensitive), solo para subproductos activos (status=True)
            # NOTA: Django <3.2 no soporta 'expressions', así que la unicidad case-insensitive se debe reforzar a nivel aplicación
            models.UniqueConstraint(
                fields=["parent", "number_coil"],
                condition=Q(status=True) & ~Q(number_coil__isnull=True) & ~Q(number_coil=""),
                name="uniq_active_parent_numbercoil_ci",
            ),
            models.CheckConstraint(
                check=Q(final_enumeration__isnull=True) | Q(initial_enumeration__isnull=True) | Q(final_enumeration__gte=F("initial_enumeration")),
                name="final_ge_initial",
            ),
            models.CheckConstraint(
                check=Q(net_weight__isnull=True) | Q(gross_weight__isnull=True) | Q(net_weight__lte=F("gross_weight")),
                name="net_le_gross",
            ),
            models.CheckConstraint(
                check=Q(initial_stock_quantity__gte=0),
                name="initial_stock_non_negative",
            ),
        ]

    def clean(self):
        # Refuerza unicidad case-insensitive a nivel aplicación
        if self.status and self.number_coil:
            conflict = Subproduct.objects.filter(
                parent=self.parent,
                number_coil__iexact=self.number_coil,
                status=True
            )
            if self.pk:
                conflict = conflict.exclude(pk=self.pk)
            if conflict.exists():
                from django.core.exceptions import ValidationError
                raise ValidationError({
                    "number_coil": "Ya existe un subproducto activo con ese número de bobina (sin distinguir mayúsculas/minúsculas) para este producto padre."
                })

    def __str__(self):
        parent_name = getattr(self.parent, "name", "N/A")
        brand_display = self.brand or "Sin marca"
        return f"{brand_display} (Padre: {parent_name})"
