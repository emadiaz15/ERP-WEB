# apps/stocks/services/queries.py
from decimal import Decimal
from django.db.models import Sum
from apps.stocks.models import SubproductStock
from apps.stocks.services.common import decimal_or_zero
from apps.products.models.subproduct_model import Subproduct

def active_subproduct_qty(subproduct: Subproduct) -> Decimal:
    """
    Cantidad 'activa' (status=True) del SubproductStock del subproducto.
    """
    try:
        ss = SubproductStock.objects.get(subproduct=subproduct, status=True)
        return decimal_or_zero(ss.quantity)
    except SubproductStock.DoesNotExist:
        return Decimal("0")
    except SubproductStock.MultipleObjectsReturned:
        total = (
            SubproductStock.objects
            .filter(subproduct=subproduct, status=True)
            .aggregate(total=Sum("quantity"))["total"] or Decimal("0")
        )
        return decimal_or_zero(total)
