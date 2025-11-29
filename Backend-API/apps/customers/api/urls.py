from django.urls import path

from apps.customers.api.views.customer_views import (
    customer_list_create_view,
    customer_detail_view,
)
from apps.customers.api.views.customer_product_views import (
    customer_product_list_create_view,
    customer_product_detail_view,
)

app_name = "customers-api"

urlpatterns = [
    path("customers/", customer_list_create_view, name="customer-list"),
    path("customers/<int:customer_id>/", customer_detail_view, name="customer-detail"),
    path("product-details/", customer_product_list_create_view, name="customer-product-detail-list"),
    path("product-details/<int:detail_id>/", customer_product_detail_view, name="customer-product-detail"),
]
