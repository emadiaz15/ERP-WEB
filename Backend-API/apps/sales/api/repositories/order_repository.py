from django.db import models

from apps.sales.models import SalesOrder, SalesOrderItem


class SalesOrderRepository:
    """Capa de acceso para pedidos de venta."""

    @staticmethod
    def list_orders(*, search: str | None = None, status: str | None = None) -> models.QuerySet:
        qs = SalesOrder.objects.all()
        if search:
            qs = qs.filter(customer_legacy_name__icontains=search)
        if status:
            qs = qs.filter(status_label=status)
        return qs.prefetch_related("items__product")

    @staticmethod
    def get_order(order_id: int) -> SalesOrder | None:
        return (
            SalesOrder.objects
            .prefetch_related("items__product")
            .filter(pk=order_id)
            .first()
        )

    @staticmethod
    def create_order(**fields) -> SalesOrder:
        order = SalesOrder(**fields)
        order.save(user=fields.get("user"))
        return order

    @staticmethod
    def update_order(order: SalesOrder, *, user=None, **fields) -> SalesOrder:
        dirty = False
        for attr, value in fields.items():
            if value is not None and hasattr(order, attr) and getattr(order, attr) != value:
                setattr(order, attr, value)
                dirty = True
        if dirty:
            order.save(user=user)
        return order

    @staticmethod
    def soft_delete(order: SalesOrder, *, user=None) -> SalesOrder:
        order.delete(user=user)
        return order

    @staticmethod
    def add_item(order: SalesOrder, *, user=None, **fields) -> SalesOrderItem:
        item = SalesOrderItem(order=order, **fields)
        item.save(user=user)
        return item

    @staticmethod
    def list_items(order: SalesOrder) -> models.QuerySet:
        return order.items.select_related("product")
