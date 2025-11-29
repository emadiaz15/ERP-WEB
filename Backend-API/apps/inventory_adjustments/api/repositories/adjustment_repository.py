from django.db import models

from apps.inventory_adjustments.models import StockAdjustment, StockAdjustmentItem


class StockAdjustmentRepository:
    """Acceso a datos para ajustes de stock."""

    @staticmethod
    def list_adjustments(*, search: str | None = None, status: str | None = None) -> models.QuerySet:
        qs = StockAdjustment.objects.all()
        if search:
            qs = qs.filter(concept__icontains=search)
        if status:
            qs = qs.filter(status_label=status)
        return qs.prefetch_related("items__product")

    @staticmethod
    def get_adjustment(adjustment_id: int) -> StockAdjustment | None:
        return (
            StockAdjustment.objects
            .prefetch_related("items__product")
            .filter(pk=adjustment_id)
            .first()
        )

    @staticmethod
    def create_adjustment(**fields) -> StockAdjustment:
        adjustment = StockAdjustment(**fields)
        adjustment.save(user=fields.get("user"))
        return adjustment

    @staticmethod
    def update_adjustment(adjustment: StockAdjustment, *, user=None, **fields) -> StockAdjustment:
        dirty = False
        for attr, value in fields.items():
            if value is not None and hasattr(adjustment, attr) and getattr(adjustment, attr) != value:
                setattr(adjustment, attr, value)
                dirty = True
        if dirty:
            adjustment.save(user=user)
        return adjustment

    @staticmethod
    def soft_delete(adjustment: StockAdjustment, *, user=None) -> StockAdjustment:
        adjustment.delete(user=user)
        return adjustment

    @staticmethod
    def add_item(adjustment: StockAdjustment, *, user=None, **fields) -> StockAdjustmentItem:
        item = StockAdjustmentItem(adjustment=adjustment, **fields)
        item.save(user=user)
        return item

    @staticmethod
    def list_items(adjustment: StockAdjustment) -> models.QuerySet:
        return adjustment.items.select_related("product")
