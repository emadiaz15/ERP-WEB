from drf_spectacular.utils import OpenApiParameter, OpenApiResponse

from apps.inventory_adjustments.api.serializers import (
    StockAdjustmentSerializer,
    InventoryCountSerializer,
    StockHistorySerializer,
)

INV_TAG = "InventoryAdjustments"
CACHE_NOTE = "⚠️ Listados cacheados 5 minutos."

stock_adjustment_list_doc = {
    "tags": [INV_TAG],
    "summary": "Listar ajustes de stock",
    "description": "Permite filtrar por concepto o estado. " + CACHE_NOTE,
    "operation_id": "list_stock_adjustments",
    "parameters": [
        OpenApiParameter("search", location=OpenApiParameter.QUERY, description="Concepto", type=str),
        OpenApiParameter("status", location=OpenApiParameter.QUERY, description="Estado", type=str),
    ],
    "responses": {200: OpenApiResponse(response=StockAdjustmentSerializer)},
}

stock_adjustment_create_doc = {
    "tags": [INV_TAG],
    "summary": "Crear ajuste",
    "operation_id": "create_stock_adjustment",
    "request": StockAdjustmentSerializer,
    "responses": {
        201: OpenApiResponse(response=StockAdjustmentSerializer, description="Ajuste creado"),
        400: OpenApiResponse(description="Datos inválidos"),
    },
}

stock_adjustment_detail_doc = {
    "tags": [INV_TAG],
    "summary": "Detalle ajuste",
    "operation_id": "retrieve_stock_adjustment",
    "responses": {200: OpenApiResponse(response=StockAdjustmentSerializer)},
}

stock_adjustment_update_doc = {
    "tags": [INV_TAG],
    "summary": "Actualizar ajuste",
    "operation_id": "update_stock_adjustment",
    "request": StockAdjustmentSerializer,
    "responses": {200: OpenApiResponse(response=StockAdjustmentSerializer)},
}

stock_adjustment_delete_doc = {
    "tags": [INV_TAG],
    "summary": "Eliminar ajuste",
    "operation_id": "delete_stock_adjustment",
    "responses": {204: OpenApiResponse(description="Eliminado")},
}

inventory_count_list_doc = {
    "tags": [INV_TAG],
    "summary": "Listar conteos de inventario",
    "description": CACHE_NOTE,
    "operation_id": "list_inventory_counts",
    "parameters": [
        OpenApiParameter("search", location=OpenApiParameter.QUERY, description="Descripción", type=str),
        OpenApiParameter("status", location=OpenApiParameter.QUERY, description="Estado", type=str),
    ],
    "responses": {200: OpenApiResponse(response=InventoryCountSerializer)},
}

inventory_count_create_doc = {
    "tags": [INV_TAG],
    "summary": "Crear conteo",
    "operation_id": "create_inventory_count",
    "request": InventoryCountSerializer,
    "responses": {
        201: OpenApiResponse(response=InventoryCountSerializer, description="Conteo creado"),
        400: OpenApiResponse(description="Datos inválidos"),
    },
}

inventory_count_detail_doc = {
    "tags": [INV_TAG],
    "summary": "Detalle conteo",
    "operation_id": "retrieve_inventory_count",
    "responses": {200: OpenApiResponse(response=InventoryCountSerializer)},
}

inventory_count_update_doc = {
    "tags": [INV_TAG],
    "summary": "Actualizar conteo",
    "operation_id": "update_inventory_count",
    "request": InventoryCountSerializer,
    "responses": {200: OpenApiResponse(response=InventoryCountSerializer)},
}

inventory_count_delete_doc = {
    "tags": [INV_TAG],
    "summary": "Eliminar conteo",
    "operation_id": "delete_inventory_count",
    "responses": {204: OpenApiResponse(description="Eliminado")},
}

stock_history_list_doc = {
    "tags": [INV_TAG],
    "summary": "Listar historial de stock",
    "description": "Histórico por producto." + CACHE_NOTE,
    "operation_id": "list_stock_history",
    "parameters": [
        OpenApiParameter("product", location=OpenApiParameter.QUERY, description="ID de producto", type=int),
    ],
    "responses": {200: OpenApiResponse(response=StockHistorySerializer)},
}
