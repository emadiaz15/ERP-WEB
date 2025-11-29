from django.db import models

from apps.products.models.base_model import BaseModel
from apps.suppliers.models.supplier_model import Supplier


class Retention(BaseModel):
    """Retencion impositiva aplicada sobre pagos a proveedores (tabla ``retenciones``)."""

    payment = models.ForeignKey(
        "treasury.OutgoingPayment",
        on_delete=models.SET_NULL,
        related_name="retentions",
        null=True,
        blank=True,
        verbose_name="Pago",
        help_text="Pago al que se asocia la retencion (ret_comp).",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        related_name="retentions",
        null=True,
        blank=True,
        verbose_name="Proveedor",
    )
    supplier_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Proveedor legacy",
        help_text="Codigo prov_codi cuando el proveedor aun no existe.",
    )
    legacy_id = models.IntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name="ID legacy",
        help_text="Identificador heredado ret_codi.",
    )
    date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha",
        help_text="Fecha de la retencion (ret_fech).",
    )
    certificate_number = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Numero comprobante",
        help_text="Numero o referencia del comprobante (ret_comp).",
    )
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name="Importe",
        help_text="Importe retenido (ret_monto).",
    )
    tax_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Tipo de impuesto",
        help_text="Codigo o descripcion del impuesto aplicable.",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notas",
    )

    class Meta:
        verbose_name = "Retencion"
        verbose_name_plural = "Retenciones"
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["legacy_id"]),
            models.Index(fields=["date"]),
            models.Index(fields=["supplier_legacy_id"]),
        ]

    def __str__(self) -> str:
        number = self.certificate_number or self.legacy_id or self.pk
        return f"Retencion {number}" if number is not None else "Retencion"
