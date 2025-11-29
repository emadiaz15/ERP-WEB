from django.db import models

from apps.customers.models import CustomerProductDetail, CustomerProductDescription


class CustomerProductRepository:
    """Acceso a datos para descripciones personalizadas."""

    @staticmethod
    def list_details(*, customer_id: int | None = None, product_id: int | None = None) -> models.QuerySet:
        qs = CustomerProductDetail.objects.select_related("customer", "product").prefetch_related("descriptions")
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs

    @staticmethod
    def create_detail(**fields) -> CustomerProductDetail:
        detail = CustomerProductDetail(**fields)
        detail.save(user=fields.get("user"))
        return detail

    @staticmethod
    def update_detail(detail: CustomerProductDetail, *, user=None, **fields) -> CustomerProductDetail:
        dirty = False
        for attr, value in fields.items():
            if value is not None and hasattr(detail, attr) and getattr(detail, attr) != value:
                setattr(detail, attr, value)
                dirty = True
        if dirty:
            detail.save(user=user)
        return detail

    @staticmethod
    def soft_delete(detail: CustomerProductDetail, *, user=None) -> CustomerProductDetail:
        detail.delete(user=user)
        return detail

    @staticmethod
    def add_description(detail: CustomerProductDetail, *, user=None, **fields) -> CustomerProductDescription:
        description = CustomerProductDescription(detail=detail, **fields)
        description.save(user=user)
        return description

    @staticmethod
    def list_descriptions(detail: CustomerProductDetail) -> models.QuerySet:
        return detail.descriptions.all()
