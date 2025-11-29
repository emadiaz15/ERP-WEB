from django.db import models


class DocumentKind(models.TextChoices):
    INVOICE = "invoice", "Factura"
    DEBIT_NOTE = "debit_note", "Nota de débito"
    CREDIT_NOTE = "credit_note", "Nota de crédito"
    COMMISSION = "commission", "Comisión"
    DELIVERY_NOTE = "delivery_note", "Remito"
    ORDER = "order", "Pedido"
    QUOTE = "quote", "Presupuesto"


class DocumentWorkflowStatus(models.TextChoices):
    DRAFT = "draft", "Borrador"
    AUTHORIZED = "authorized", "Autorizado"
    ACCOUNTED = "accounted", "Contabilizado"
    SETTLED = "settled", "Cancelado"
    CANCELLED = "cancelled", "Anulado"


class CurrencyChoices(models.TextChoices):
    ARS = "ARS", "Peso Argentino"
    USD = "USD", "Dólar"
    EUR = "EUR", "Euro"
    BRL = "BRL", "Real"


class AfipDocumentType(models.IntegerChoices):
    FACTURA_A = 1, "Factura A"
    NOTA_DEBITO_A = 2, "Nota de Débito A"
    NOTA_CREDITO_A = 3, "Nota de Crédito A"
    RECIBO_A = 4, "Recibo A"
    FACTURA_B = 6, "Factura B"
    NOTA_DEBITO_B = 7, "Nota de Débito B"
    NOTA_CREDITO_B = 8, "Nota de Crédito B"
    RECIBO_B = 9, "Recibo B"
    FACTURA_E = 19, "Factura E"
    NOTA_DEBITO_E = 20, "Nota de Débito E"
    NOTA_CREDITO_E = 21, "Nota de Crédito E"
    FACTURA_M = 51, "Factura M"
    NOTA_DEBITO_M = 52, "Nota de Débito M"
    NOTA_CREDITO_M = 53, "Nota de Crédito M"


class LedgerEntryKind(models.TextChoices):
    DOCUMENT = "document", "Documento"
    PAYMENT = "payment", "Cobro"
    ADJUSTMENT = "adjustment", "Ajuste"
    COMMISSION = "commission", "Comisión"


class LedgerEntrySource(models.TextChoices):
    SALES = "sales", "Ventas"
    TREASURY = "treasury", "Tesorería"
    LEGACY = "legacy", "Migración"
    MANUAL = "manual", "Manual"


class DocumentRelationKind(models.TextChoices):
    ORIGINATES = "originates", "Origina"
    CLOSES = "closes", "Cancela"
    REFERS = "refers", "Referencia"
    ADJUSTS = "adjusts", "Ajusta"
