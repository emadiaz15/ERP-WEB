# apps/products/signals.py

import logging

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from apps.products.models import Product, Category, Subproduct, SupplierProduct

from apps.products.utils.cache_invalidation import (
    invalidate_product_cache, invalidate_subproduct_cache, invalidate_category_cache
)
from apps.products.services.supplier_price_history_service import SupplierPriceHistoryService

logger = logging.getLogger(__name__)



@receiver([post_save, post_delete], sender=Category)
def clear_category_cache(sender, **kwargs):
    invalidate_category_cache()
    logger.debug("[Cache][Signal] category_list invalidada.")



@receiver([post_save, post_delete], sender=Product)
def clear_product_cache(sender, **kwargs):
    invalidate_product_cache()
    logger.debug("[Cache][Signal] product_list y product_detail invalidados.")



@receiver([post_save, post_delete], sender=Subproduct)
def clear_subproduct_cache(sender, **kwargs):
    invalidate_subproduct_cache()
    logger.debug("[Cache][Signal] subproduct_list y subproduct_detail invalidados.")


@receiver(post_save, sender=SupplierProduct)
def track_supplier_price_changes(sender, instance, created, **kwargs):
    """Automatically create price history record when SupplierProduct price changes.

    Este signal se ejecuta después de guardar un SupplierProduct.
    Si es una creación o si los precios cambiaron, crea un registro en el histórico.
    """
    try:
        # Si es un nuevo registro, crear histórico inicial
        if created:
            SupplierPriceHistoryService.create_price_history_record(
                supplier_product=instance,
                notes="Precio inicial"
            )
            logger.info(f"Created initial price history for SupplierProduct #{instance.id}")
            return

        # Si es una actualización, verificar si cambió el precio
        current_history = SupplierPriceHistoryService.get_current_price(instance)

        if current_history:
            # Comparar precios actuales con el histórico
            cost_changed = current_history.cost != instance.cost
            sale_cost_changed = current_history.sale_cost != instance.sale_cost
            currency_changed = current_history.currency != instance.currency

            if cost_changed or sale_cost_changed or currency_changed:
                # Crear nuevo registro de histórico
                SupplierPriceHistoryService.create_price_history_record(
                    supplier_product=instance,
                    notes="Actualización de precio automática"
                )
                logger.info(
                    f"Price change detected for SupplierProduct #{instance.id}. "
                    f"Created new history record."
                )
        else:
            # Si no hay histórico previo, crear uno
            SupplierPriceHistoryService.create_price_history_record(
                supplier_product=instance,
                notes="Primer registro de histórico"
            )
            logger.info(f"Created first price history for SupplierProduct #{instance.id}")

    except Exception as e:
        logger.error(
            f"Error tracking price change for SupplierProduct #{instance.id}: {e}",
            exc_info=True
        )
