# apps/stocks/services/validators.py
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from django.db.models import Sum
from apps.stocks.models import SubproductStock
from apps.products.models.subproduct_model import Subproduct

def check_subproduct_stock(subproduct: Subproduct, quantity_needed: Decimal, location: str = None):
    """
    Verifica disponibilidad; lanza ValidationError si no alcanza.
    """
    if not isinstance(subproduct, Subproduct) or not subproduct.pk:
        raise ValidationError("Subproducto inválido.")

    try:
        quantity_needed = Decimal(quantity_needed)
        if quantity_needed <= 0:
            raise ValidationError("La cantidad requerida debe ser positiva.")
    except (InvalidOperation, TypeError):
        raise ValidationError("La cantidad requerida debe ser un número válido.")

    qs = SubproductStock.objects.filter(subproduct=subproduct, status=True)
    total_available = qs.aggregate(total=Sum("quantity"))["total"] or Decimal("0")

    if quantity_needed > total_available:
        raise ValidationError(
            f"Stock insuficiente para el subproducto {subproduct.pk}. "
            f"Requiere {quantity_needed}, disponible {total_available}."
        )
    return True
