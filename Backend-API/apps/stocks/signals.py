# apps/stocks/signals.py
from decimal import Decimal
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.stocks.models.stock_subproduct_model import SubproductStock
from apps.products.models.subproduct_model import Subproduct  # ⬅️ importar modelo

logger = logging.getLogger(__name__)

@receiver(post_save, sender=SubproductStock)
def sync_status_on_stock_change(sender, instance: SubproductStock, **kwargs):
    sp = instance.subproduct
    desired = (instance.quantity or Decimal("0")) > 0
    if sp.status != desired:
        # ✅ usar la instancia directamente para evitar problemas con el manager filtrado
        sp.status = desired
        sp.save(update_fields=['status', 'modified_at', 'modified_by'])
        logger.debug("sync_status_on_stock_change: Subproduct %s -> status=%s by stock=%s", sp.pk, desired, instance.quantity)
