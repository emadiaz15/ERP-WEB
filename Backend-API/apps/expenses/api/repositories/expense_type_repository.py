from django.db import models

from apps.expenses.models import ExpenseType


class ExpenseTypeRepository:
    """Acceso a datos para el catálogo de tipos de gasto."""

    @staticmethod
    def list_types(search: str | None = None) -> models.QuerySet:
        qs = ExpenseType.objects.all()
        if search:
            qs = qs.filter(models.Q(name__icontains=search) | models.Q(code__icontains=search))
        return qs

    @staticmethod
    def create_type(**fields) -> ExpenseType:
        obj = ExpenseType(**fields)
        obj.save(user=fields.get("user"))
        return obj

    @staticmethod
    def update_type(expense_type: ExpenseType, *, user=None, **fields) -> ExpenseType:
        changed = False
        for attr, value in fields.items():
            if hasattr(expense_type, attr) and value is not None and getattr(expense_type, attr) != value:
                setattr(expense_type, attr, value)
                changed = True
        if changed:
            expense_type.save(user=user)
        return expense_type

    @staticmethod
    def soft_delete(expense_type: ExpenseType, *, user=None) -> ExpenseType:
        expense_type.delete(user=user)
        return expense_type
