# apps/stocks/services/status.py
from typing import Optional
from django.conf import settings
from apps.products.models.subproduct_model import Subproduct
from apps.stocks.services.queries import active_subproduct_qty

User = settings.AUTH_USER_MODEL  # solo anotación

def ensure_subproduct_status_from_stock(subproduct: Subproduct, acting_user: Optional[User] = None) -> None:
    """
    status := (stock_actual > 0). Guarda solo si cambia.
    """
    if not isinstance(subproduct, Subproduct) or not subproduct.pk:
        raise ValueError("Se requiere una instancia de Subproducto válida.")

    import logging
    logger = logging.getLogger(__name__)
    qty = active_subproduct_qty(subproduct)
    should_be_active = qty > 0

    logger.debug(f"ensure_subproduct_status_from_stock: Subproduct {subproduct.pk} qty={qty} should_be_active={should_be_active} status_before={subproduct.status}")
    if bool(subproduct.status) != bool(should_be_active):
        subproduct.status = should_be_active
        try:
            subproduct.save(user=acting_user)
        except TypeError:
            subproduct.save()
        logger.debug(f"ensure_subproduct_status_from_stock: Subproduct {subproduct.pk} status updated to {should_be_active}")
