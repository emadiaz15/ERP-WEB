from django.db import models
from django.utils import timezone

from apps.expenses.models import ExpensePayment


class ExpensePaymentRepository:
    """Acceso a datos para pagos de gastos."""

    @staticmethod
    def list_payments(
        *,
        person_legacy_id: int | None = None,
        status: str | None = None,
        date_from: timezone.datetime | None = None,
        date_to: timezone.datetime | None = None,
    ) -> models.QuerySet:
        qs = ExpensePayment.objects.prefetch_related("allocations", "payment_methods", "debit_links")
        if person_legacy_id is not None:
            qs = qs.filter(person_legacy_id=person_legacy_id)
        if status:
            qs = qs.filter(status_label=status)
        if date_from:
            qs = qs.filter(payment_date__gte=date_from)
        if date_to:
            qs = qs.filter(payment_date__lte=date_to)
        return qs

    @staticmethod
    def get_payment(payment_id: int) -> ExpensePayment | None:
        return (
            ExpensePayment.objects.prefetch_related("allocations", "payment_methods", "debit_links")
            .filter(pk=payment_id)
            .first()
        )

    @staticmethod
    def create_payment(**fields) -> ExpensePayment:
        payment = ExpensePayment(**fields)
        payment.save(user=fields.get("user"))
        return payment

    @staticmethod
    def update_payment(payment: ExpensePayment, *, user=None, **fields) -> ExpensePayment:
        changed = False
        for attr, value in fields.items():
            if hasattr(payment, attr) and value is not None and getattr(payment, attr) != value:
                setattr(payment, attr, value)
                changed = True
        if changed:
            payment.save(user=user)
        return payment

    @staticmethod
    def soft_delete(payment: ExpensePayment, *, user=None) -> ExpensePayment:
        payment.delete(user=user)
        return payment
