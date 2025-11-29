from django.urls import path

from apps.sales.api.views.order_views import (
    sales_order_list_create_view,
    sales_order_detail_view,
)
from apps.sales.api.views.shipment_views import (
    sales_shipment_list_create_view,
    sales_shipment_detail_view,
)
from apps.sales.api.views.invoice_views import (
    sales_invoice_list_create_view,
    sales_invoice_detail_view,
)

app_name = "sales-api"

urlpatterns = [
    path("orders/", sales_order_list_create_view, name="sales-order-list"),
    path("orders/<int:order_id>/", sales_order_detail_view, name="sales-order-detail"),
    path("shipments/", sales_shipment_list_create_view, name="sales-shipment-list"),
    path("shipments/<int:shipment_id>/", sales_shipment_detail_view, name="sales-shipment-detail"),
    path("invoices/", sales_invoice_list_create_view, name="sales-invoice-list"),
    path("invoices/<int:invoice_id>/", sales_invoice_detail_view, name="sales-invoice-detail"),
]
