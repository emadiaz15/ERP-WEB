from django.db import models


class PayableDocumentKind(models.TextChoices):
    SUPPLIER_INVOICE = "supplier_invoice", "Factura proveedor"
    SUPPLIER_DEBIT = "supplier_debit", "Nota de débito"
    SUPPLIER_CREDIT = "supplier_credit", "Nota de crédito"
    EXPENSE = "expense", "Gasto"
    RETENTION = "retention", "Retención"
    ADJUSTMENT = "adjustment", "Ajuste"


class PayableDocumentStatus(models.TextChoices):
    DRAFT = "draft", "Borrador"
    VALIDATED = "validated", "Validada"
    POSTED = "posted", "Contabilizada"
    PAID = "paid", "Pagada"
    CANCELLED = "cancelled", "Anulada"


class PaymentOrderStatus(models.TextChoices):
    DRAFT = "draft", "Borrador"
    AUTHORIZED = "authorized", "Autorizada"
    EXECUTED = "executed", "Ejecutada"
    CANCELLED = "cancelled", "Cancelada"


class LedgerEntryKind(models.TextChoices):
    DOCUMENT = "document", "Documento"
    PAYMENT = "payment", "Pago"
    RETENTION = "retention", "Retención"
    ADJUSTMENT = "adjustment", "Ajuste"


class LedgerEntrySource(models.TextChoices):
    PURCHASES = "purchases", "Compras"
    EXPENSES = "expenses", "Gastos"
    TREASURY = "treasury", "Tesorería"
    MANUAL = "manual", "Manual"
    LEGACY = "legacy", "Migración"


class RetentionType(models.TextChoices):
    VAT = "vat", "IVA"
    GROSS_INCOME = "gross_income", "Ingresos brutos"
    PROFESSION = "profession", "Honorarios"
    OTHER = "other", "Otros"
