from typing import Iterable, Optional

from django.db import models

from apps.products.models.customer_product_model import CustomerProduct
from apps.products.models.product_model import Product


class CustomerProductRepository:
    """Thin repository for ``CustomerProduct``.

    Encapsula las operaciones CRUD básicas para las configuraciones
    de producto/cliente heredadas de ``articulos_clientes``.
    """

    @staticmethod
    def get_all_by_product(product: Product | int) -> models.QuerySet:
        """Return all active customer-product rows for a given product.

        ``product`` can be the instance or its primary key.
        """

        product_id = product.pk if isinstance(product, Product) else product
        return CustomerProduct.objects.filter(product_id=product_id, status=True)

    @staticmethod
    def create(*, product: Product, customer_legacy_id: int, description: str | None = None, user=None) -> CustomerProduct:
        """Create a new ``CustomerProduct`` using BaseModel save logic."""

        instance = CustomerProduct(
            product=product,
            customer_legacy_id=customer_legacy_id,
            description=description,
        )
        instance.save(user=user)
        return instance

    @staticmethod
    def update(instance: CustomerProduct, *, description: str | None = None, user=None) -> CustomerProduct:
        """Update description for an existing ``CustomerProduct`` row."""

        changed = False
        if description is not None and instance.description != description:
            instance.description = description
            changed = True

        if changed:
            instance.save(user=user)
        return instance

    @staticmethod
    def soft_delete(instance: CustomerProduct, user=None) -> CustomerProduct:
        """Perform a soft delete using BaseModel logic."""

        instance.delete(user=user)
        return instance
