from django.db import models

from apps.customers.models import Customer


class CustomerRepository:
    """Operaciones de acceso a datos para clientes."""

    @staticmethod
    def list_customers(*, search: str | None = None, zone: int | None = None) -> models.QuerySet:
        qs = Customer.objects.select_related("zone", "city", "tax_condition")
        if search:
            qs = qs.filter(name__icontains=search)
        if zone:
            qs = qs.filter(zone_id=zone)
        return qs

    @staticmethod
    def get_customer(customer_id: int) -> Customer | None:
        return (
            Customer.objects
            .select_related("zone", "city", "tax_condition")
            .filter(pk=customer_id)
            .first()
        )

    @staticmethod
    def create_customer(**fields) -> Customer:
        customer = Customer(**fields)
        customer.save(user=fields.get("user"))
        return customer

    @staticmethod
    def update_customer(customer: Customer, *, user=None, **fields) -> Customer:
        dirty = False
        for attr, value in fields.items():
            if value is not None and hasattr(customer, attr) and getattr(customer, attr) != value:
                setattr(customer, attr, value)
                dirty = True
        if dirty:
            customer.save(user=user)
        return customer

    @staticmethod
    def soft_delete(customer: Customer, *, user=None) -> Customer:
        customer.delete(user=user)
        return customer
