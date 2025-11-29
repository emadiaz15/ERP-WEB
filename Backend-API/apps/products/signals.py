# apps/products/signals.py

import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.products.models import Product, Category, Subproduct

from apps.products.utils.cache_invalidation import (
    invalidate_product_cache, invalidate_subproduct_cache, invalidate_category_cache
)

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
