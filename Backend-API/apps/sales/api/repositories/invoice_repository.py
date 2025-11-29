from django.db import models

from apps.sales.models import SalesInvoice, SalesInvoiceItem


class SalesInvoiceRepository:
    """Acceso a datos para facturas."""

    @staticmethod
    def list_invoices(*, search: str | None = None, status: str | None = None) -> models.QuerySet:
        qs = SalesInvoice.objects.select_related("order", "shipment")
        if search:
            qs = qs.filter(invoice_number__icontains=search)
        if status:
            qs = qs.filter(status_label=status)
        return qs.prefetch_related("items__product")

    @staticmethod
    def get_invoice(invoice_id: int) -> SalesInvoice | None:
        return (
            SalesInvoice.objects
            .select_related("order", "shipment")
            .prefetch_related("items__product")
            .filter(pk=invoice_id)
            .first()
        )

    @staticmethod
    def create_invoice(**fields) -> SalesInvoice:
        invoice = SalesInvoice(**fields)
        invoice.save(user=fields.get("user"))
        return invoice

    @staticmethod
    def update_invoice(invoice: SalesInvoice, *, user=None, **fields) -> SalesInvoice:
        dirty = False
        for attr, value in fields.items():
            if value is not None and hasattr(invoice, attr) and getattr(invoice, attr) != value:
                setattr(invoice, attr, value)
                dirty = True
        if dirty:
            invoice.save(user=user)
        return invoice

    @staticmethod
    def soft_delete(invoice: SalesInvoice, *, user=None) -> SalesInvoice:
        invoice.delete(user=user)
        return invoice

    @staticmethod
    def add_item(invoice: SalesInvoice, *, user=None, **fields) -> SalesInvoiceItem:
        item = SalesInvoiceItem(invoice=invoice, **fields)
        item.save(user=user)
        return item

    @staticmethod
    def list_items(invoice: SalesInvoice) -> models.QuerySet:
        return invoice.items.select_related("product")
