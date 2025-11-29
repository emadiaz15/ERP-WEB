from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.expenses.models import Expense, ExpensePayment, ExpensePaymentAllocation
from apps.expenses.services.accounting_gateway import sync_payment_with_accounting


def _validate_positive_amount(amount: Decimal):
    if amount is None or amount <= Decimal("0"):
        raise ValidationError("El importe debe ser mayor a cero.")


def approve_expense(expense: Expense, *, user, notes: str | None = None) -> Expense:
    if expense.status_label == Expense.Status.CANCELLED:
        raise ValidationError("No se puede aprobar un gasto anulado.")
    if expense.status_label == Expense.Status.PAID:
        raise ValidationError("El gasto ya fue pagado.")
    if expense.expense_type and not expense.expense_type.requires_approval:
        return expense  # No cambia estado si no aplica workflow

    expense.status_label = Expense.Status.APPROVED
    expense.approved_at = timezone.now()
    expense.approved_by = user
    if notes is not None:
        expense.approval_notes = notes
    expense.save(user=user)
    return expense


@transaction.atomic
def register_payment_allocation(
    *,
    payment: ExpensePayment,
    expense: Expense,
    amount: Decimal,
    is_partial: bool = False,
    user,
) -> ExpensePaymentAllocation:
    if payment.status_label == ExpensePayment.Status.CANCELLED:
        raise ValidationError("El pago está anulado.")
    if expense.status_label == Expense.Status.CANCELLED:
        raise ValidationError("El gasto está anulado.")

    _validate_positive_amount(amount)
    outstanding = expense.outstanding_amount()
    if amount > outstanding:
        raise ValidationError(f"El importe supera el saldo pendiente ({outstanding}).")

    allocation = ExpensePaymentAllocation(
        payment=payment,
        expense=expense,
        amount=amount,
        is_partial=is_partial or amount < outstanding,
    )
    allocation.save(user=user)

    expense.amount_paid = (expense.amount_paid or Decimal("0")) + amount
    if expense.outstanding_amount() == Decimal("0"):
        expense.status_label = Expense.Status.PAID
    else:
        expense.status_label = Expense.Status.APPROVED
    expense.save(user=user)

    _recalculate_payment_retentions(payment, user=user)
    sync_payment_with_accounting(payment)
    return allocation


def _recalculate_payment_retentions(payment: ExpensePayment, *, user):
    total = Decimal("0")
    for allocation in payment.allocations.select_related("expense__expense_type"):
        expense_type = allocation.expense.expense_type
        if not expense_type:
            continue
        percent = expense_type.retention_percent or Decimal("0")
        if percent <= 0:
            continue
        minimum = expense_type.retention_minimum_amount or Decimal("0")
        if allocation.amount < minimum:
            continue
        total += allocation.amount * (percent / Decimal("100"))

    payment.retention_total_amount = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    payment.save(user=user, update_fields=["retention_total_amount"])