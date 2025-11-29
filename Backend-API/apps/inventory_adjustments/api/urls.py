from django.urls import path

from apps.inventory_adjustments.api.views.adjustment_views import (
    stock_adjustment_list_create_view,
    stock_adjustment_detail_view,
)
from apps.inventory_adjustments.api.views.inventory_views import (
    inventory_count_list_create_view,
    inventory_count_detail_view,
)
from apps.inventory_adjustments.api.views.history_views import stock_history_list_view

app_name = "inventory-adjustments-api"

urlpatterns = [
    path("adjustments/", stock_adjustment_list_create_view, name="stock-adjustment-list"),
    path("adjustments/<int:adjustment_id>/", stock_adjustment_detail_view, name="stock-adjustment-detail"),
    path("counts/", inventory_count_list_create_view, name="inventory-count-list"),
    path("counts/<int:count_id>/", inventory_count_detail_view, name="inventory-count-detail"),
    path("history/", stock_history_list_view, name="stock-history-list"),
]
