from django.urls import path

from apps.purchases.api.views.order_views import (
    purchase_order_list_create_view,
    purchase_order_detail_view,
)
from apps.purchases.api.views.receipt_views import (
    purchase_receipt_list_create_view,
    purchase_receipt_detail_view,
)
from apps.purchases.api.views.payment_views import (
    purchase_payment_list_create_view,
    purchase_payment_detail_view,
)

app_name = "purchases-api"

urlpatterns = [
    path("orders/", purchase_order_list_create_view, name="purchase-order-list"),
    path("orders/<int:order_id>/", purchase_order_detail_view, name="purchase-order-detail"),
    path("receipts/", purchase_receipt_list_create_view, name="purchase-receipt-list"),
    path("receipts/<int:receipt_id>/", purchase_receipt_detail_view, name="purchase-receipt-detail"),
    path("payments/", purchase_payment_list_create_view, name="purchase-payment-list"),
    path("payments/<int:payment_id>/", purchase_payment_detail_view, name="purchase-payment-detail"),
]
