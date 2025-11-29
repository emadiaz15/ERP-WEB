from django.db import models

from apps.inventory_adjustments.models import StockHistory


class StockHistoryRepository:
    """Operaciones simples sobre el historial de stock."""

    @staticmethod
    def list_history(*, product_id: int | None = None) -> models.QuerySet:
        qs = StockHistory.objects.select_related("product")
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs

    @staticmethod
    def create_entry(**fields) -> StockHistory:
        entry = StockHistory(**fields)
        entry.save(user=fields.get("user"))
        return entry
