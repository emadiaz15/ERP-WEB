from django.db import models

from apps.purchases.models import PurchaseOrder, PurchaseOrderItem


class PurchaseOrderRepository:
    """Capa de acceso a datos para órdenes de compra."""

    @staticmethod
    def list_orders(*, search: str | None = None, status: str | None = None) -> models.QuerySet:
        qs = PurchaseOrder.objects.select_related("supplier")
        if search:
            qs = qs.filter(supplier__name__icontains=search)
        if status:
            qs = qs.filter(status_label=status)
        return qs

    @staticmethod
    def get_order(order_id: int) -> PurchaseOrder | None:
        return (
            PurchaseOrder.objects
            .select_related("supplier")
            .prefetch_related("items__product")
            .filter(pk=order_id)
            .first()
        )

    @staticmethod
    def create_order(**fields) -> PurchaseOrder:
        order = PurchaseOrder(**fields)
        order.save(user=fields.get("user"))
        return order

    @staticmethod
    def update_order(order: PurchaseOrder, *, user=None, **fields) -> PurchaseOrder:
        changed = False
        for attr, value in fields.items():
            if value is not None and hasattr(order, attr) and getattr(order, attr) != value:
                setattr(order, attr, value)
                changed = True
        if changed:
            order.save(user=user)
        return order

    @staticmethod
    def soft_delete(order: PurchaseOrder, *, user=None) -> PurchaseOrder:
        order.delete(user=user)
        return order

    @staticmethod
    def add_item(order: PurchaseOrder, *, user=None, **fields) -> PurchaseOrderItem:
        item = PurchaseOrderItem(order=order, **fields)
        item.save(user=user)
        return item

    @staticmethod
    def list_items(order: PurchaseOrder) -> models.QuerySet:
        return order.items.select_related("product")
