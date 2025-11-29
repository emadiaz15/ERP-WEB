from django.db import models

from apps.products.models.base_model import BaseModel


class SalesShipment(BaseModel):
    """Remito / remesa asociada a pedidos de venta."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        IN_TRANSIT = "in_transit", "En tránsito"
        DELIVERED = "delivered", "Entregado"
        INVOICED = "invoiced", "Facturado"
        CANCELLED = "cancelled", "Anulado"

    order = models.ForeignKey(
        "sales.SalesOrder",
        on_delete=models.SET_NULL,
        related_name="shipments",
        null=True,
        blank=True,
        verbose_name="Pedido relacionado",
    )
    customer_legacy_id = models.IntegerField(verbose_name="ID cliente legacy", db_index=True)
    shipment_date = models.DateField(verbose_name="Fecha de remito")
    reference = models.CharField(max_length=255, blank=True, verbose_name="Referencia externa")
    transport_legacy_id = models.IntegerField(null=True, blank=True, verbose_name="Transporte legacy")
    notes = models.TextField(blank=True, verbose_name="Observaciones")
    legacy_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="ID legacy")
    status_label = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Estado",
    )

    class Meta:
        verbose_name = "Remito de venta"
        verbose_name_plural = "Remitos de venta"
        ordering = ["-shipment_date", "-id"]

    def __str__(self) -> str:
        return f"Remito {self.id or '-'}"
