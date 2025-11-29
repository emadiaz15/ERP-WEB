from django.urls import path

from apps.locations.api.views import (
    country_list_create,
    country_detail,
    province_list_create,
    province_detail,
    postal_code_list_create,
    postal_code_detail,
    sales_zone_list_create,
    sales_zone_detail,
    locality_list_create,
    locality_detail,
)

app_name = "locations"

urlpatterns = [
    # Countries
    path("countries/", country_list_create, name="country-list-create"),
    path("countries/<int:country_id>/", country_detail, name="country-detail"),

    # Provinces
    path("provinces/", province_list_create, name="province-list-create"),
    path("provinces/<int:province_id>/", province_detail, name="province-detail"),

    # Postal codes
    path("postal-codes/", postal_code_list_create, name="postal-code-list-create"),
    path("postal-codes/<int:postal_code_id>/", postal_code_detail, name="postal-code-detail"),

    # Sales zones
    path("sales-zones/", sales_zone_list_create, name="sales-zone-list-create"),
    path("sales-zones/<int:zone_id>/", sales_zone_detail, name="sales-zone-detail"),

    # Localities
    path("localities/", locality_list_create, name="locality-list-create"),
    path("localities/<int:locality_id>/", locality_detail, name="locality-detail"),
]
