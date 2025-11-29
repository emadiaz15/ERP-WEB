from django.urls import path

from apps.suppliers.api.views.supplier_satellites_view import (
	supplier_description_list_create_view,
	supplier_description_detail_view,
	supplier_discount_list_create_view,
	supplier_discount_detail_view,
	supplier_cost_history_list_view,
)

app_name = "suppliers-api"

urlpatterns = [
	path(
		"products/<int:prod_pk>/suppliers/<int:sp_pk>/descriptions/",
		supplier_description_list_create_view,
		name="supplier-description-list-create",
	),
	path(
		"products/<int:prod_pk>/suppliers/<int:sp_pk>/descriptions/<int:desc_pk>/",
		supplier_description_detail_view,
		name="supplier-description-detail",
	),
	path(
		"products/<int:prod_pk>/suppliers/<int:sp_pk>/discounts/",
		supplier_discount_list_create_view,
		name="supplier-discount-list-create",
	),
	path(
		"products/<int:prod_pk>/suppliers/<int:sp_pk>/discounts/<int:disc_pk>/",
		supplier_discount_detail_view,
		name="supplier-discount-detail",
	),
	path(
		"products/<int:prod_pk>/suppliers/<int:sp_pk>/cost-history/",
		supplier_cost_history_list_view,
		name="supplier-cost-history-list",
	),
]
