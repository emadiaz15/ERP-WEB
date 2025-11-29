from django.db import models

from apps.inventory_adjustments.models import InventoryCount, InventoryCountItem


class InventoryCountRepository:
    """Acceso a datos para conteos físicos."""

    @staticmethod
    def list_counts(*, search: str | None = None, status: str | None = None) -> models.QuerySet:
        qs = InventoryCount.objects.all()
        if search:
            qs = qs.filter(description__icontains=search)
        if status:
            qs = qs.filter(status_label=status)
        return qs.prefetch_related("items__product")

    @staticmethod
    def get_count(count_id: int) -> InventoryCount | None:
        return (
            InventoryCount.objects
            .prefetch_related("items__product")
            .filter(pk=count_id)
            .first()
        )

    @staticmethod
    def create_count(**fields) -> InventoryCount:
        count = InventoryCount(**fields)
        count.save(user=fields.get("user"))
        return count

    @staticmethod
    def update_count(count: InventoryCount, *, user=None, **fields) -> InventoryCount:
        dirty = False
        for attr, value in fields.items():
            if value is not None and hasattr(count, attr) and getattr(count, attr) != value:
                setattr(count, attr, value)
                dirty = True
        if dirty:
            count.save(user=user)
        return count

    @staticmethod
    def soft_delete(count: InventoryCount, *, user=None) -> InventoryCount:
        count.delete(user=user)
        return count

    @staticmethod
    def add_item(count: InventoryCount, *, user=None, **fields) -> InventoryCountItem:
        item = InventoryCountItem(count=count, **fields)
        item.save(user=user)
        return item

    @staticmethod
    def list_items(count: InventoryCount) -> models.QuerySet:
        return count.items.select_related("product")
