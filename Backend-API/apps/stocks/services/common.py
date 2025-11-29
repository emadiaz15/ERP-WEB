# apps/stocks/services/common.py
from decimal import Decimal

def decimal_or_zero(val) -> Decimal:
    try:
        d = Decimal(val)
        return d if d.is_finite() else Decimal("0")
    except Exception:
        return Decimal("0")
