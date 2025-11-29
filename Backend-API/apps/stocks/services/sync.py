# apps/stocks/services/sync.py
from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from apps.products.models.product_model import Product
from apps.stocks.models import ProductStock, SubproductStock


@transaction.atomic
def sync_parent_product_stock(parent: Product, acting_user=None) -> None:
    """
    Espeja ProductStock con la suma de SubproductStock activos del padre.
    Solo si ya existe ProductStock.
    """
    if not isinstance(parent, Product) or not parent.pk or not parent.has_subproducts:
        return

    total = (
        SubproductStock.objects
        .filter(subproduct__parent=parent, status=True, subproduct__status=True)
        .aggregate(total=Sum("quantity"))["total"] or Decimal("0.00")
    )

    try:
        ps = ProductStock.objects.select_for_update().get(product=parent)
    except ProductStock.DoesNotExist:
        return

    if ps.quantity != total:
        ps.quantity = total
        try:
            ps.save(user=acting_user)
        except TypeError:
            ps.save()


@transaction.atomic
def validate_and_correct_stock():
    """
    Corrige ProductStock con la suma de subproductos activos.
    """
    for product in Product.objects.filter(has_subproducts=True):
        total = (
            SubproductStock.objects
            .filter(subproduct__parent=product, status=True, subproduct__status=True)
            .aggregate(total=Sum("quantity"))["total"] or Decimal("0.00")
        )
        try:
            stock_record = ProductStock.objects.select_for_update().get(product=product)
        except ProductStock.DoesNotExist:
            continue

        if stock_record.quantity != total:
            stock_record.quantity = total
            try:
                stock_record.save(user=None)
            except TypeError:
                stock_record.save()
