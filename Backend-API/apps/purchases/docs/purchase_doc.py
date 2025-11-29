from drf_spectacular.utils import OpenApiParameter, OpenApiResponse

from apps.purchases.api.serializers import (
    PurchaseOrderSerializer,
    PurchaseReceiptSerializer,
    PurchasePaymentSerializer,
)

PURCHASE_TAG = "Purchases"
CACHE_NOTE = "⚠️ Cache de 5 minutos para listados."  # breve aviso

purchase_order_list_doc = {
    "tags": [PURCHASE_TAG],
    "summary": "Listar órdenes de compra",
    "description": "Listado paginado filtrable por proveedor o estado. " + CACHE_NOTE,
    "operation_id": "list_purchase_orders",
    "parameters": [
        OpenApiParameter("search", location=OpenApiParameter.QUERY, description="Nombre proveedor", type=str),
        OpenApiParameter("status", location=OpenApiParameter.QUERY, description="Estado", type=str),
    ],
    "responses": {200: OpenApiResponse(response=PurchaseOrderSerializer)},
}

purchase_order_create_doc = {
    "tags": [PURCHASE_TAG],
    "summary": "Crear orden de compra",
    "operation_id": "create_purchase_order",
    "request": PurchaseOrderSerializer,
    "responses": {
        201: OpenApiResponse(response=PurchaseOrderSerializer, description="Orden creada"),
        400: OpenApiResponse(description="Datos inválidos"),
    },
}

purchase_order_detail_doc = {
    "tags": [PURCHASE_TAG],
    "summary": "Detalle orden de compra",
    "operation_id": "retrieve_purchase_order",
    "responses": {200: OpenApiResponse(response=PurchaseOrderSerializer)},
}

purchase_order_update_doc = {
    "tags": [PURCHASE_TAG],
    "summary": "Actualizar orden",
    "operation_id": "update_purchase_order",
    "request": PurchaseOrderSerializer,
    "responses": {200: OpenApiResponse(response=PurchaseOrderSerializer)},
}

purchase_order_delete_doc = {
    "tags": [PURCHASE_TAG],
    "summary": "Eliminar orden",
    "operation_id": "delete_purchase_order",
    "responses": {204: OpenApiResponse(description="Eliminada")},
}

purchase_receipt_list_doc = {
    "tags": [PURCHASE_TAG],
    "summary": "Listar recepciones",
    "description": "Recepciones/facturas de proveedor. " + CACHE_NOTE,
    "operation_id": "list_purchase_receipts",
    "parameters": [
        OpenApiParameter("search", location=OpenApiParameter.QUERY, description="Nombre proveedor", type=str),
    ],
    "responses": {200: OpenApiResponse(response=PurchaseReceiptSerializer)},
}

purchase_receipt_create_doc = {
    "tags": [PURCHASE_TAG],
    "summary": "Crear recepción",
    "operation_id": "create_purchase_receipt",
    "request": PurchaseReceiptSerializer,
    "responses": {
        201: OpenApiResponse(response=PurchaseReceiptSerializer, description="Recepción creada"),
        400: OpenApiResponse(description="Datos inválidos"),
    },
}

purchase_receipt_detail_doc = {
    "tags": [PURCHASE_TAG],
    "summary": "Detalle recepción",
    "operation_id": "retrieve_purchase_receipt",
    "responses": {200: OpenApiResponse(response=PurchaseReceiptSerializer)},
}

purchase_receipt_update_doc = {
    "tags": [PURCHASE_TAG],
    "summary": "Actualizar recepción",
    "operation_id": "update_purchase_receipt",
    "request": PurchaseReceiptSerializer,
    "responses": {200: OpenApiResponse(response=PurchaseReceiptSerializer)},
}

purchase_receipt_delete_doc = {
    "tags": [PURCHASE_TAG],
    "summary": "Eliminar recepción",
    "operation_id": "delete_purchase_receipt",
    "responses": {204: OpenApiResponse(description="Eliminada")},
}

purchase_payment_list_doc = {
    "tags": [PURCHASE_TAG],
    "summary": "Listar pagos a proveedores",
    "description": "Pagos registrados. " + CACHE_NOTE,
    "operation_id": "list_purchase_payments",
    "parameters": [
        OpenApiParameter("supplier", location=OpenApiParameter.QUERY, description="ID proveedor", type=int),
    ],
    "responses": {200: OpenApiResponse(response=PurchasePaymentSerializer)},
}

purchase_payment_create_doc = {
    "tags": [PURCHASE_TAG],
    "summary": "Registrar pago",
    "operation_id": "create_purchase_payment",
    "request": PurchasePaymentSerializer,
    "responses": {
        201: OpenApiResponse(response=PurchasePaymentSerializer, description="Pago creado"),
        400: OpenApiResponse(description="Datos inválidos"),
    },
}

purchase_payment_detail_doc = {
    "tags": [PURCHASE_TAG],
    "summary": "Detalle pago",
    "operation_id": "retrieve_purchase_payment",
    "responses": {200: OpenApiResponse(response=PurchasePaymentSerializer)},
}

purchase_payment_delete_doc = {
    "tags": [PURCHASE_TAG],
    "summary": "Eliminar pago",
    "operation_id": "delete_purchase_payment",
    "responses": {204: OpenApiResponse(description="Eliminado")},
}
