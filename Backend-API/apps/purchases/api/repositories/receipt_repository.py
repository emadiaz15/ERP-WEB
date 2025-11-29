from django.db import models

from apps.purchases.models import PurchaseReceipt, PurchaseReceiptItem


class PurchaseReceiptRepository:
    """Operaciones CRUD para recepciones de compra."""

    @staticmethod
    def list_receipts(*, search: str | None = None) -> models.QuerySet:
        qs = PurchaseReceipt.objects.select_related("supplier", "order")
        if search:
            qs = qs.filter(supplier__name__icontains=search)
        return qs

    @staticmethod
    def get_receipt(receipt_id: int) -> PurchaseReceipt | None:
        return (
            PurchaseReceipt.objects
            .select_related("supplier", "order")
            .prefetch_related("items__product")
            .filter(pk=receipt_id)
            .first()
        )

    @staticmethod
    def create_receipt(**fields) -> PurchaseReceipt:
        receipt = PurchaseReceipt(**fields)
        receipt.save(user=fields.get("user"))
        return receipt

    @staticmethod
    def add_item(receipt: PurchaseReceipt, *, user=None, **fields) -> PurchaseReceiptItem:
        item = PurchaseReceiptItem(receipt=receipt, **fields)
        item.save(user=user)
        return item

    @staticmethod
    def update_receipt(receipt: PurchaseReceipt, *, user=None, **fields) -> PurchaseReceipt:
        changed = False
        for attr, value in fields.items():
            if value is not None and hasattr(receipt, attr) and getattr(receipt, attr) != value:
                setattr(receipt, attr, value)
                changed = True
        if changed:
            receipt.save(user=user)
        return receipt

    @staticmethod
    def soft_delete(receipt: PurchaseReceipt, *, user=None) -> PurchaseReceipt:
        receipt.delete(user=user)
        return receipt
