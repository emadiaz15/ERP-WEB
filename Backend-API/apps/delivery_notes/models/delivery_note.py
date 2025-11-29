from django.db import models

from apps.products.models.base_model import BaseModel


class DeliveryNote(BaseModel):
    """Remito (delivery note) importado del ERP legacy."""

    shipment = models.OneToOneField(
        "sales.SalesShipment",
        on_delete=models.CASCADE,
        related_name="delivery_note",
        null=True,
        blank=True,
        verbose_name="Remito base",
        help_text="Referencia al remito simplificado en el módulo de ventas.",
    )
    legacy_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID legacy",
        help_text="Clave primaria original del sistema legacy (rem_codi).",
    )
    number = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Número",
        help_text="Número de remito (rem_nro).",
    )
    point_of_sale = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Punto de venta",
        help_text="Identificador del punto de venta (rem_pto).",
    )
    issue_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de emisión",
        help_text="Fecha del remito (rem_fech).",
    )
    invoice_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Factura legacy",
        help_text="ID de factura asociada (fac_codi).",
    )
    order_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Pedido legacy",
        help_text="ID de pedido relacionado (ped_codi).",
    )
    customer_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Cliente legacy",
        help_text="Código de cliente (cli_codi).",
    )
    supplier_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Proveedor legacy",
        help_text="Código de proveedor (prov_codi).",
    )
    carrier_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Transporte legacy",
        help_text="Código de transporte (tran_codi).",
    )
    freight_charge = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Cargo de flete",
        help_text="Indicador de quién paga el flete (flete_cargo).",
    )
    freight_weight = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Peso del flete",
        help_text="Peso total enviado (flete_peso).",
    )
    freight_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor del flete",
        help_text="Costo del flete (flete_valor).",
    )
    freight_destination = models.TextField(
        blank=True,
        verbose_name="Lugar de entrega",
        help_text="Destino del envío (flete_lugent).",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Observaciones",
        help_text="Notas adicionales (rem_observ).",
    )
    cancellation_flag = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Marca anulado",
        help_text="Flag legacy de anulación (anulado).",
    )
    is_invoiced = models.BooleanField(
        default=False,
        verbose_name="Facturado",
        help_text="Indica si el remito fue facturado (facturado).",
    )

    class Meta:
        verbose_name = "Remito"
        verbose_name_plural = "Remitos"
        indexes = [
            models.Index(fields=["legacy_id"]),
            models.Index(fields=["issue_date"]),
        ]

    def __str__(self) -> str:
        pos = f"{self.point_of_sale:04d}" if self.point_of_sale is not None else "----"
        num = f"{self.number:08d}" if self.number is not None else "--------"
        return f"Remito {pos}-{num}"
