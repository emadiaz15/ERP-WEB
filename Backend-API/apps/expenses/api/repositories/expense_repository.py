from django.db import models
from django.utils import timezone

from apps.expenses.models import Expense


class ExpenseRepository:
    """Acceso a datos para gastos."""

    @staticmethod
    def list_expenses(
        *,
        search: str | None = None,
        status: str | None = None,
        expense_type: int | None = None,
        person_legacy_id: int | None = None,
        date_from: timezone.datetime | None = None,
        date_to: timezone.datetime | None = None,
    ) -> models.QuerySet:
        qs = (
            Expense.objects.select_related("expense_type")
            .prefetch_related("items")
        )
        if search:
            qs = qs.filter(models.Q(concept__icontains=search) | models.Q(notes__icontains=search))
        if status:
            qs = qs.filter(status_label=status)
        if expense_type is not None:
            qs = qs.filter(expense_type_id=expense_type)
        if person_legacy_id is not None:
            qs = qs.filter(person_legacy_id=person_legacy_id)
        if date_from:
            qs = qs.filter(expense_date__gte=date_from)
        if date_to:
            qs = qs.filter(expense_date__lte=date_to)
        return qs

    @staticmethod
    def get_expense(expense_id: int) -> Expense | None:
        return (
            Expense.objects.select_related("expense_type")
            .prefetch_related("items", "disbursements")
            .filter(pk=expense_id)
            .first()
        )

    @staticmethod
    def create_expense(**fields) -> Expense:
        expense = Expense(**fields)
        expense.save(user=fields.get("user"))
        return expense

    @staticmethod
    def update_expense(expense: Expense, *, user=None, **fields) -> Expense:
        changed = False
        for attr, value in fields.items():
            if hasattr(expense, attr) and value is not None and getattr(expense, attr) != value:
                setattr(expense, attr, value)
                changed = True
        if changed:
            expense.save(user=user)
        return expense

    @staticmethod
    def soft_delete(expense: Expense, *, user=None) -> Expense:
        expense.delete(user=user)
        return expense
