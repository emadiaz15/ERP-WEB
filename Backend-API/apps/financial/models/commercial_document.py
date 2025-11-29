from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.customers.models.customer import Customer
from apps.products.models.base_model import BaseModel
from apps.financial.choices import (
    AfipDocumentType,
    CurrencyChoices,
    DocumentKind,
    DocumentRelationKind,
    DocumentWorkflowStatus,
)


class CommercialDocument(BaseModel):
    """Documento comercial base que representa la capa legal/contable."""

    document_kind = models.CharField(
        max_length=20,
        choices=DocumentKind.choices,
        verbose_name="Tipo lógico",
    )
    workflow_state = models.CharField(
        max_length=20,
        choices=DocumentWorkflowStatus.choices,
        default=DocumentWorkflowStatus.DRAFT,
        verbose_name="Estado",
    )
    afip_document_type = models.PositiveSmallIntegerField(
        choices=AfipDocumentType.choices,
        null=True,
        blank=True,
        verbose_name="Tipo AFIP",
    )
    point_of_sale = models.PositiveIntegerField(
        default=0,
        verbose_name="Punto de venta",
    )
    sequence_number = models.PositiveIntegerField(
        default=0,
        verbose_name="Número correlativo",
    )
    issue_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha emisión",
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha vencimiento",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        related_name="%(class)s_documents",
        related_query_name="%(class)s_document",
        null=True,
        blank=True,
        verbose_name="Cliente",
    )
    customer_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Cliente legacy",
    )
    customer_name_snapshot = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Snapshot cliente",
    )
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.ARS,
        verbose_name="Moneda",
    )
    exchange_rate = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=1,
        verbose_name="Cotización",
    )
    net_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name="Neto",
    )
    tax_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name="Impuestos",
    )
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name="Total",
    )
    balance_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name="Saldo",
    )
    legacy_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID legacy",
    )
    legacy_reference = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Referencia legacy",
    )
    afip_cae = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="CAE",
    )
    afip_cae_expiration = models.DateField(
        null=True,
        blank=True,
        verbose_name="Vencimiento CAE",
    )
    afip_payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Payload AFIP",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadatos",
    )
    notes = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        abstract = True
        ordering = ["-issue_date", "-created_at"]

    @property
    def formatted_number(self) -> str:
        return f"{self.point_of_sale:04d}-{self.sequence_number:08d}"


class InvoiceDocument(CommercialDocument):
    sales_invoice = models.OneToOneField(
        "sales.SalesInvoice",
        on_delete=models.SET_NULL,
        related_name="financial_document",
        null=True,
        blank=True,
        verbose_name="Factura ERP",
    )

    class Meta:
        verbose_name = "Factura (Financiero)"
        verbose_name_plural = "Facturas (Financiero)"


class DebitNoteDocument(CommercialDocument):
    base_invoice = models.ForeignKey(
        "financial.InvoiceDocument",
        on_delete=models.SET_NULL,
        related_name="debit_notes",
        null=True,
        blank=True,
        verbose_name="Factura ajustada",
    )

    class Meta:
        verbose_name = "Nota de débito"
        verbose_name_plural = "Notas de débito"


class CreditNoteDocument(CommercialDocument):
    base_invoice = models.ForeignKey(
        "financial.InvoiceDocument",
        on_delete=models.SET_NULL,
        related_name="credit_notes",
        null=True,
        blank=True,
        verbose_name="Factura ajustada",
    )

    class Meta:
        verbose_name = "Nota de crédito"
        verbose_name_plural = "Notas de crédito"


class CommissionDocument(CommercialDocument):
    salesperson_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Vendedor",
    )
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="% Comisión",
    )

    class Meta:
        verbose_name = "Comisión"
        verbose_name_plural = "Comisiones"


class DeliveryNoteDocument(CommercialDocument):
    shipment = models.ForeignKey(
        "sales.SalesShipment",
        on_delete=models.SET_NULL,
        related_name="financial_documents",
        null=True,
        blank=True,
        verbose_name="Remito ERP",
    )

    class Meta:
        verbose_name = "Remito"
        verbose_name_plural = "Remitos"


class OrderDocument(CommercialDocument):
    order = models.ForeignKey(
        "sales.SalesOrder",
        on_delete=models.SET_NULL,
        related_name="financial_documents",
        null=True,
        blank=True,
        verbose_name="Pedido ERP",
    )
    expected_ship_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha estimada despacho",
    )

    class Meta:
        verbose_name = "Pedido (Financiero)"
        verbose_name_plural = "Pedidos (Financiero)"


class QuoteDocument(CommercialDocument):
    order = models.ForeignKey(
        "sales.SalesOrder",
        on_delete=models.SET_NULL,
        related_name="quote_documents",
        null=True,
        blank=True,
        verbose_name="Pedido/Presupuesto ERP",
    )
    valid_until = models.DateField(
        null=True,
        blank=True,
        verbose_name="Vigencia",
    )

    class Meta:
        verbose_name = "Presupuesto"
        verbose_name_plural = "Presupuestos"


class DocumentLink(BaseModel):
    """Relaciona documentos para trazar el flujo pedido→remito→factura→cobro."""

    source_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="financial_link_sources")
    source_object_id = models.PositiveIntegerField()
    source = GenericForeignKey("source_content_type", "source_object_id")

    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="financial_link_targets")
    target_object_id = models.PositiveIntegerField()
    target = GenericForeignKey("target_content_type", "target_object_id")

    relation_kind = models.CharField(
        max_length=20,
        choices=DocumentRelationKind.choices,
        verbose_name="Tipo relación",
    )
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Relación de documentos"
        verbose_name_plural = "Relaciones de documentos"
        unique_together = (
            (
                "source_content_type",
                "source_object_id",
                "target_content_type",
                "target_object_id",
                "relation_kind",
            ),
        )