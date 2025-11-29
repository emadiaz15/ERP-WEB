from django.db import models

from apps.products.models.base_model import BaseModel
from apps.suppliers.models import Supplier
from apps.purchases.models import PurchaseOrder, PurchaseReceipt
from apps.expenses.models import Expense
from apps.payables.choices import PayableDocumentKind, PayableDocumentStatus
from apps.financial.choices import AfipDocumentType, CurrencyChoices


class AccountsPayableDocument(BaseModel):
    """Documento base de cuentas por pagar (facturas, ND, gastos, etc.)."""

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="%(class)s_payable_documents",
        related_query_name="%(class)s_payable_document",
        verbose_name="Proveedor",
    )
    supplier_name_snapshot = models.CharField(max_length=255, blank=True)
    supplier_legacy_id = models.IntegerField(null=True, blank=True, db_index=True)
    document_kind = models.CharField(
        max_length=30,
        choices=PayableDocumentKind.choices,
        verbose_name="Tipo documento",
    )
    status_label = models.CharField(
        max_length=20,
        choices=PayableDocumentStatus.choices,
        default=PayableDocumentStatus.DRAFT,
        verbose_name="Estado",
    )
    afip_document_type = models.PositiveSmallIntegerField(
        choices=AfipDocumentType.choices,
        null=True,
        blank=True,
        verbose_name="Tipo AFIP",
    )
    voucher_letter = models.CharField(max_length=2, blank=True, verbose_name="Letra")
    point_of_sale = models.PositiveIntegerField(default=0, verbose_name="Punto de venta")
    voucher_number = models.PositiveIntegerField(default=0, verbose_name="Número")
    issue_date = models.DateField(null=True, blank=True, verbose_name="Fecha emisión")
    due_date = models.DateField(null=True, blank=True, verbose_name="Fecha vencimiento")
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.ARS,
        verbose_name="Moneda",
    )
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=4, default=1, verbose_name="Cotización")
    taxable_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Gravado")
    exempt_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="No gravado")
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Impuestos")
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Total")
    balance_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="Saldo")
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.SET_NULL,
        related_name="%(class)s_payable_documents",
        related_query_name="%(class)s_payable_document",
        null=True,
        blank=True,
        verbose_name="Orden de compra",
    )
    purchase_receipt = models.ForeignKey(
        PurchaseReceipt,
        on_delete=models.SET_NULL,
        related_name="%(class)s_payable_documents",
        related_query_name="%(class)s_payable_document",
        null=True,
        blank=True,
        verbose_name="Recepción",
    )
    expense = models.ForeignKey(
        Expense,
        on_delete=models.SET_NULL,
        related_name="%(class)s_payable_documents",
        related_query_name="%(class)s_payable_document",
        null=True,
        blank=True,
        verbose_name="Gasto asociado",
    )
    retention_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name="Retenciones",
    )
    other_withholding_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name="Otros descuentos",
    )
    legacy_id = models.IntegerField(null=True, blank=True, db_index=True, verbose_name="ID legacy")
    legacy_table = models.CharField(max_length=60, blank=True, verbose_name="Tabla legacy")
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True
        ordering = ["-issue_date", "-created_at"]

    @property
    def formatted_number(self) -> str:
        return f"{self.voucher_letter or ''}{self.point_of_sale:04d}-{self.voucher_number:08d}"

    def mark_as_paid(self, *, user=None):
        if self.status_label != PayableDocumentStatus.PAID:
            self.status_label = PayableDocumentStatus.PAID
            self.balance_amount = 0
            self.save(user=user)


class SupplierInvoiceDocument(AccountsPayableDocument):
    cae = models.CharField(max_length=32, blank=True)
    cae_due_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Factura proveedor"
        verbose_name_plural = "Facturas proveedor"


class SupplierDebitNoteDocument(AccountsPayableDocument):
    base_invoice = models.ForeignKey(
        "payables.SupplierInvoiceDocument",
        on_delete=models.SET_NULL,
        related_name="debit_notes",
        null=True,
        blank=True,
        verbose_name="Factura ajustada",
    )

    class Meta:
        verbose_name = "Nota de débito proveedor"
        verbose_name_plural = "Notas de débito proveedor"


class SupplierCreditNoteDocument(AccountsPayableDocument):
    base_invoice = models.ForeignKey(
        "payables.SupplierInvoiceDocument",
        on_delete=models.SET_NULL,
        related_name="credit_notes",
        null=True,
        blank=True,
        verbose_name="Factura ajustada",
    )

    class Meta:
        verbose_name = "Nota de crédito proveedor"
        verbose_name_plural = "Notas de crédito proveedor"


class ExpenseDocument(AccountsPayableDocument):
    class Meta:
        verbose_name = "Documento de gasto"
        verbose_name_plural = "Documentos de gasto"

    def clean(self):
        if not self.expense:
            raise models.ValidationError("Los documentos de gasto requieren un gasto asociado.")