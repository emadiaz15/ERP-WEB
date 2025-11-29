from django.urls import path

# Historial (GET)
from apps.stocks.api.views.stock_event_product_view import (
    product_stock_event_history,               # productos SIN subproductos
    product_subproducts_stock_event_history,   # productos CON subproductos (agregado)
)
from apps.stocks.api.views.stock_event_subproduct_view import (
    subproduct_stock_event_history,            # por product_pk + subproduct_pk
    subproduct_stock_event_history_by_id,      # solo por subproduct_id
)

# Ajustes (POST)
from apps.stocks.api.views.stock_adjust_views import (
    subproduct_stock_adjust,
    product_stock_adjust,
)

urlpatterns = [
    # Historial de eventos de stock para productos (sin subproductos)
    path(
        "products/<int:pk>/stock/events/",
        product_stock_event_history,
        name="product-stock-events",
    ),

    # Historial AGREGADO de eventos para productos (con subproductos)
    path(
        "products/<int:product_pk>/subproducts/stock/events/",
        product_subproducts_stock_event_history,
        name="product-subproducts-stock-events",
    ),

    # Historial de eventos de stock para subproductos (con product_pk)
    path(
        "products/<int:product_pk>/subproducts/<int:subproduct_pk>/stock/events/",
        subproduct_stock_event_history,
        name="subproduct-stock-events",
    ),

    # Historial de eventos de stock para subproductos (solo subproduct_id) ← UI
    path(
        "subproducts/<int:subproduct_pk>/stock/events/",
        subproduct_stock_event_history_by_id,
        name="subproduct-stock-events-by-id",
    ),

    # --- Ajustes manuales de stock (POST, staff-only) ---
    # OJO: no anteponer "stocks/" aquí, porque este módulo ya se incluye con 'api/v1/stocks/'
    path(
        "subproducts/<int:subproduct_id>/stock/adjust/",
        subproduct_stock_adjust,
        name="subproduct_stock_adjust",
    ),
    path(
        "products/<int:product_id>/stock/adjust/",
        product_stock_adjust,
        name="product_stock_adjust",
    ),
]
