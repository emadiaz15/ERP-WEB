from django.db import models

from apps.products.models.base_model import BaseModel


class SalesInvoice(BaseModel):
    """Factura generada a partir de pedidos y remitos."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        PENDING_PAYMENT = "pending_payment", "Pendiente de cobro"
        PARTIALLY_PAID = "partially_paid", "Cobro parcial"
        PAID = "paid", "Cobrado"
        CANCELLED = "cancelled", "Anulado"

    order = models.ForeignKey(
        "sales.SalesOrder",
        on_delete=models.SET_NULL,
        related_name="invoices",
        null=True,
        blank=True,
        verbose_name="Pedido relacionado",
    )
    shipment = models.ForeignKey(
        "sales.SalesShipment",
        on_delete=models.SET_NULL,
        related_name="invoices",
        null=True,
        blank=True,
        verbose_name="Remito relacionado",
    )
    customer_legacy_id = models.IntegerField(verbose_name="ID cliente legacy", db_index=True)
    invoice_type = models.CharField(max_length=3, verbose_name="Tipo comprobante")
    point_of_sale = models.IntegerField(verbose_name="Punto de venta")
    invoice_number = models.IntegerField(verbose_name="Número de comprobante")
    issue_date = models.DateField(verbose_name="Fecha de emisión")
    due_date = models.DateField(null=True, blank=True, verbose_name="Fecha de vencimiento")
    currency = models.CharField(max_length=3, default="ARS", verbose_name="Moneda")
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=1, verbose_name="Cotización")
    subtotal_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Subtotal")
    discount_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Descuentos")
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Impuestos")
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Total")
    notes = models.TextField(blank=True, verbose_name="Observaciones")
    legacy_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="ID legacy")
    status_label = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Estado",
    )

    class Meta:
        verbose_name = "Factura de venta"
        verbose_name_plural = "Facturas de venta"
        ordering = ["-issue_date", "-id"]

    def __str__(self) -> str:
        return f"Factura {self.invoice_type}-{self.point_of_sale}-{self.invoice_number}"
