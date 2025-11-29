from django.urls import path

from apps.expenses.api.views import (
    expense_type_list_create_view,
    expense_type_detail_view,
    expense_list_create_view,
    expense_detail_view,
    expense_approve_view,
    expense_payment_list_create_view,
    expense_payment_detail_view,
    expense_payment_allocation_view,
)

app_name = "expenses-api"

urlpatterns = [
    path("types/", expense_type_list_create_view, name="expense-type-list"),
    path("types/<int:type_id>/", expense_type_detail_view, name="expense-type-detail"),
    path("records/", expense_list_create_view, name="expense-list"),
    path("records/<int:expense_id>/", expense_detail_view, name="expense-detail"),
    path("records/<int:expense_id>/approve/", expense_approve_view, name="expense-approve"),
    path("payments/", expense_payment_list_create_view, name="expense-payment-list"),
    path("payments/<int:payment_id>/", expense_payment_detail_view, name="expense-payment-detail"),
    path(
        "payments/<int:payment_id>/allocations/",
        expense_payment_allocation_view,
        name="expense-payment-allocate",
    ),
]
