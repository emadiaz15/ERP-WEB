from datetime import datetime
from typing import Optional

from django.db import models

from apps.suppliers.models import Supplier
from apps.products.models.product_model import Product
from apps.products.models.supplier_product_model import SupplierProduct
from apps.products.models.supplier_discount_model import (
    SupplierProductDescription,
    SupplierProductDiscount,
)
from apps.stocks.models import SupplierCostHistory


class SupplierRepository:
    """Capa de acceso a datos para proveedores."""

    @staticmethod
    def list_active(search: str | None = None) -> models.QuerySet:
        qs = Supplier.objects.filter(status=True)
        if search:
            qs = qs.filter(name__icontains=search)
        return qs.order_by("name")

    @staticmethod
    def get_by_id(supplier_id: int) -> Supplier | None:
        return Supplier.objects.filter(pk=supplier_id, status=True).first()

    @staticmethod
    def create(**fields) -> Supplier:
        supplier = Supplier(**fields)
        supplier.save(user=fields.get("user"))
        return supplier

    @staticmethod
    def update(instance: Supplier, user=None, **fields) -> Supplier:
        changed = False
        for attr, value in fields.items():
            if hasattr(instance, attr) and getattr(instance, attr) != value:
                setattr(instance, attr, value)
                changed = True
        if changed:
            instance.save(user=user)
        return instance

    @staticmethod
    def soft_delete(instance: Supplier, user=None) -> Supplier:
        instance.delete(user=user)
        return instance


class SupplierProductRepository:
    """CRUD para ``SupplierProduct`` (articulos_proveedores)."""

    @staticmethod
    def get_all_by_product(product: Product | int) -> models.QuerySet:
        product_id = product.pk if isinstance(product, Product) else product
        return SupplierProduct.objects.filter(product_id=product_id, status=True)

    @staticmethod
    def get_by_id(supplier_product_id: int) -> SupplierProduct | None:
        return SupplierProduct.objects.filter(pk=supplier_product_id, status=True).first()

    @staticmethod
    def create(
        *,
        product: Product,
        supplier_legacy_id: int,
        cost: float | None = None,
        sale_cost: float | None = None,
        description: str | None = None,
        currency: str | None = None,
        price_list_number: int | None = None,
        other_flag: int | None = None,
        exchange_rate_ref: int | None = None,
        user=None,
    ) -> SupplierProduct:
        instance = SupplierProduct(
            product=product,
            supplier_legacy_id=supplier_legacy_id,
            cost=cost,
            sale_cost=sale_cost,
            description=description,
            currency=currency,
            price_list_number=price_list_number,
            other_flag=other_flag,
            exchange_rate_ref=exchange_rate_ref,
        )
        instance.save(user=user)
        return instance

    @staticmethod
    def update(
        instance: SupplierProduct,
        *,
        cost: float | None = None,
        sale_cost: float | None = None,
        description: str | None = None,
        currency: str | None = None,
        price_list_number: int | None = None,
        other_flag: int | None = None,
        exchange_rate_ref: int | None = None,
        user=None,
    ) -> SupplierProduct:
        changed = False
        if cost is not None and instance.cost != cost:
            instance.cost = cost
            changed = True
        if sale_cost is not None and instance.sale_cost != sale_cost:
            instance.sale_cost = sale_cost
            changed = True
        if description is not None and instance.description != description:
            instance.description = description
            changed = True
        if currency is not None and instance.currency != currency:
            instance.currency = currency
            changed = True
        if price_list_number is not None and instance.price_list_number != price_list_number:
            instance.price_list_number = price_list_number
            changed = True
        if other_flag is not None and instance.other_flag != other_flag:
            instance.other_flag = other_flag
            changed = True
        if exchange_rate_ref is not None and instance.exchange_rate_ref != exchange_rate_ref:
            instance.exchange_rate_ref = exchange_rate_ref
            changed = True
        if changed:
            instance.save(user=user)
        return instance

    @staticmethod
    def soft_delete(instance: SupplierProduct, user=None) -> SupplierProduct:
        instance.delete(user=user)
        return instance


class SupplierProductDescriptionRepository:
    """Operaciones para descripciones alternativas."""

    @staticmethod
    def list_active(supplier_product: SupplierProduct, search: str | None = None) -> models.QuerySet:
        qs = SupplierProductDescription.objects.filter(
            supplier_product=supplier_product,
            status=True,
        )
        if search:
            qs = qs.filter(description__icontains=search)
        return qs.order_by("description")

    @staticmethod
    def get_by_id(supplier_product: SupplierProduct, description_id: int) -> SupplierProductDescription | None:
        return (
            SupplierProductDescription.objects
            .filter(pk=description_id, supplier_product=supplier_product, status=True)
            .first()
        )

    @staticmethod
    def create(*, supplier_product: SupplierProduct, description: str, user=None) -> SupplierProductDescription:
        instance = SupplierProductDescription(
            supplier_product=supplier_product,
            description=description,
        )
        instance.save(user=user)
        return instance

    @staticmethod
    def update(instance: SupplierProductDescription, *, description: str | None = None, user=None) -> SupplierProductDescription:
        if description is not None and instance.description != description:
            instance.description = description
            instance.save(user=user)
        return instance

    @staticmethod
    def soft_delete(instance: SupplierProductDescription, user=None) -> SupplierProductDescription:
        instance.delete(user=user)
        return instance


class SupplierProductDiscountRepository:
    """Operaciones para descuentos de proveedor."""

    @staticmethod
    def list_active(
        supplier_product: SupplierProduct,
        search: str | None = None,
        negative_only: Optional[bool] = None,
    ) -> models.QuerySet:
        qs = SupplierProductDiscount.objects.filter(
            supplier_product=supplier_product,
            status=True,
        )
        if search:
            qs = qs.filter(discount_legacy_id__icontains=search)
        if negative_only is True:
            qs = qs.filter(is_negative=True)
        elif negative_only is False:
            qs = qs.filter(is_negative=False)
        return qs.order_by("discount_legacy_id")

    @staticmethod
    def get_by_id(supplier_product: SupplierProduct, discount_id: int) -> SupplierProductDiscount | None:
        return (
            SupplierProductDiscount.objects
            .filter(pk=discount_id, supplier_product=supplier_product, status=True)
            .first()
        )

    @staticmethod
    def create(*, supplier_product: SupplierProduct, discount_legacy_id: int, is_negative: bool, user=None) -> SupplierProductDiscount:
        instance = SupplierProductDiscount(
            supplier_product=supplier_product,
            discount_legacy_id=discount_legacy_id,
            is_negative=is_negative,
        )
        instance.save(user=user)
        return instance

    @staticmethod
    def update(
        instance: SupplierProductDiscount,
        *,
        discount_legacy_id: int | None = None,
        is_negative: bool | None = None,
        user=None,
    ) -> SupplierProductDiscount:
        changed = False
        if discount_legacy_id is not None and instance.discount_legacy_id != discount_legacy_id:
            instance.discount_legacy_id = discount_legacy_id
            changed = True
        if is_negative is not None and instance.is_negative != is_negative:
            instance.is_negative = is_negative
            changed = True
        if changed:
            instance.save(user=user)
        return instance

    @staticmethod
    def soft_delete(instance: SupplierProductDiscount, user=None) -> SupplierProductDiscount:
        instance.delete(user=user)
        return instance


class SupplierCostHistoryRepository:
    """Consultas avanzadas del histórico de costos."""

    @staticmethod
    def list_by_supplier_product(
        supplier_product: SupplierProduct,
        *,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        currency: str | None = None,
    ) -> models.QuerySet:
        qs = SupplierCostHistory.objects.filter(
            supplier_product=supplier_product,
            status=True,
        ).order_by("-date")
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        if currency:
            qs = qs.filter(currency__iexact=currency)
        return qs
