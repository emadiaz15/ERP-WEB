from django.db import models

from apps.purchases.models import PurchasePayment, PurchasePaymentAllocation


class PurchasePaymentRepository:
    """Persistencia de pagos a proveedores."""

    @staticmethod
    def list_payments(*, supplier_id: int | None = None) -> models.QuerySet:
        qs = PurchasePayment.objects.select_related("supplier")
        if supplier_id:
            qs = qs.filter(supplier_id=supplier_id)
        return qs

    @staticmethod
    def get_payment(payment_id: int) -> PurchasePayment | None:
        return (
            PurchasePayment.objects
            .select_related("supplier")
            .prefetch_related("allocations__receipt")
            .filter(pk=payment_id)
            .first()
        )

    @staticmethod
    def create_payment(**fields) -> PurchasePayment:
        payment = PurchasePayment(**fields)
        payment.save(user=fields.get("user"))
        return payment

    @staticmethod
    def add_allocation(payment: PurchasePayment, *, user=None, **fields) -> PurchasePaymentAllocation:
        allocation = PurchasePaymentAllocation(payment=payment, **fields)
        allocation.save(user=user)
        return allocation

    @staticmethod
    def soft_delete(payment: PurchasePayment, *, user=None) -> PurchasePayment:
        payment.delete(user=user)
        return payment
