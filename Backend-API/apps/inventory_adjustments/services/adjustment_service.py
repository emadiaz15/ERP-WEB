from django.utils import timezone

from apps.inventory_adjustments.api.repositories import (
    StockAdjustmentRepository,
    StockHistoryRepository,
)
from apps.inventory_adjustments.models import StockAdjustment, StockAdjustmentItem, StockHistory


class AdjustmentService:
    """Lógica de negocio para aplicar ajustes e impactar el historial de stock."""

    @staticmethod
    def post_adjustment(adjustment: StockAdjustment, *, user=None) -> StockAdjustment:
        if adjustment.status_label == StockAdjustment.Status.POSTED:
            return adjustment

        items = StockAdjustmentRepository.list_items(adjustment)
        movement_date = adjustment.adjustment_date
        now_time = timezone.now().time()
        for item in items:
            StockHistoryRepository.create_entry(
                product=item.product,
                movement_type=StockHistory.MovementType.ADJUSTMENT,
                movement_date=movement_date,
                movement_time=now_time,
                previous_quantity=item.system_quantity,
                quantity_delta=item.difference,
                resulting_quantity=item.system_quantity + item.difference,
                observations=item.reason,
                detail=adjustment.observations,
                adjustment=adjustment,
                user=user,
            )
        adjustment.status_label = StockAdjustment.Status.POSTED
        adjustment.save(user=user)
        return adjustment
