# apps/stocks/services/reservations.py
from decimal import Decimal
from django.db.models import Sum
from apps.cuts.models.cutting_order_model import CuttingOrderItem

def reserved_qty(subproduct_id: int) -> Decimal:
    return (
        CuttingOrderItem.objects
        .filter(
            subproduct_id=subproduct_id,
            order__status=True,
            order__workflow_status__in=['pending', 'in_process'],
        )
        .aggregate(total=Sum('cutting_quantity'))['total'] or Decimal('0')
    )
