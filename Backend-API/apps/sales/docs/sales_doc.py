from drf_spectacular.utils import OpenApiParameter, OpenApiResponse

from apps.sales.api.serializers import (
    SalesOrderSerializer,
    SalesShipmentSerializer,
    SalesInvoiceSerializer,
)

SALES_TAG = "Sales"
CACHE_NOTE = "⚠️ Cache de 5 minutos para listados."

sales_order_list_doc = {
    "tags": [SALES_TAG],
    "summary": "Listar pedidos de venta",
    "description": "Listado paginado filtrable por cliente o estado. " + CACHE_NOTE,
    "operation_id": "list_sales_orders",
    "parameters": [
        OpenApiParameter("search", location=OpenApiParameter.QUERY, description="Nombre cliente", type=str),
        OpenApiParameter("status", location=OpenApiParameter.QUERY, description="Estado", type=str),
    ],
    "responses": {200: OpenApiResponse(response=SalesOrderSerializer)},
}

sales_order_create_doc = {
    "tags": [SALES_TAG],
    "summary": "Crear pedido de venta",
    "operation_id": "create_sales_order",
    "request": SalesOrderSerializer,
    "responses": {
        201: OpenApiResponse(response=SalesOrderSerializer, description="Pedido creado"),
        400: OpenApiResponse(description="Datos inválidos"),
    },
}

sales_order_detail_doc = {
    "tags": [SALES_TAG],
    "summary": "Detalle pedido de venta",
    "operation_id": "retrieve_sales_order",
    "responses": {200: OpenApiResponse(response=SalesOrderSerializer)},
}

sales_order_update_doc = {
    "tags": [SALES_TAG],
    "summary": "Actualizar pedido",
    "operation_id": "update_sales_order",
    "request": SalesOrderSerializer,
    "responses": {200: OpenApiResponse(response=SalesOrderSerializer)},
}

sales_order_delete_doc = {
    "tags": [SALES_TAG],
    "summary": "Eliminar pedido",
    "operation_id": "delete_sales_order",
    "responses": {204: OpenApiResponse(description="Eliminado")},
}

sales_shipment_list_doc = {
    "tags": [SALES_TAG],
    "summary": "Listar remitos",
    "description": "Listado paginado filtrable por referencia o estado. " + CACHE_NOTE,
    "operation_id": "list_sales_shipments",
    "parameters": [
        OpenApiParameter("search", location=OpenApiParameter.QUERY, description="Referencia", type=str),
        OpenApiParameter("status", location=OpenApiParameter.QUERY, description="Estado", type=str),
    ],
    "responses": {200: OpenApiResponse(response=SalesShipmentSerializer)},
}

sales_shipment_create_doc = {
    "tags": [SALES_TAG],
    "summary": "Crear remito",
    "operation_id": "create_sales_shipment",
    "request": SalesShipmentSerializer,
    "responses": {
        201: OpenApiResponse(response=SalesShipmentSerializer, description="Remito creado"),
        400: OpenApiResponse(description="Datos inválidos"),
    },
}

sales_shipment_detail_doc = {
    "tags": [SALES_TAG],
    "summary": "Detalle remito",
    "operation_id": "retrieve_sales_shipment",
    "responses": {200: OpenApiResponse(response=SalesShipmentSerializer)},
}

sales_shipment_update_doc = {
    "tags": [SALES_TAG],
    "summary": "Actualizar remito",
    "operation_id": "update_sales_shipment",
    "request": SalesShipmentSerializer,
    "responses": {200: OpenApiResponse(response=SalesShipmentSerializer)},
}

sales_shipment_delete_doc = {
    "tags": [SALES_TAG],
    "summary": "Eliminar remito",
    "operation_id": "delete_sales_shipment",
    "responses": {204: OpenApiResponse(description="Eliminado")},
}

sales_invoice_list_doc = {
    "tags": [SALES_TAG],
    "summary": "Listar facturas",
    "description": "Listado paginado filtrable por número o estado. " + CACHE_NOTE,
    "operation_id": "list_sales_invoices",
    "parameters": [
        OpenApiParameter("search", location=OpenApiParameter.QUERY, description="Número factura", type=str),
        OpenApiParameter("status", location=OpenApiParameter.QUERY, description="Estado", type=str),
    ],
    "responses": {200: OpenApiResponse(response=SalesInvoiceSerializer)},
}

sales_invoice_create_doc = {
    "tags": [SALES_TAG],
    "summary": "Crear factura",
    "operation_id": "create_sales_invoice",
    "request": SalesInvoiceSerializer,
    "responses": {
        201: OpenApiResponse(response=SalesInvoiceSerializer, description="Factura creada"),
        400: OpenApiResponse(description="Datos inválidos"),
    },
}

sales_invoice_detail_doc = {
    "tags": [SALES_TAG],
    "summary": "Detalle factura",
    "operation_id": "retrieve_sales_invoice",
    "responses": {200: OpenApiResponse(response=SalesInvoiceSerializer)},
}

sales_invoice_update_doc = {
    "tags": [SALES_TAG],
    "summary": "Actualizar factura",
    "operation_id": "update_sales_invoice",
    "request": SalesInvoiceSerializer,
    "responses": {200: OpenApiResponse(response=SalesInvoiceSerializer)},
}

sales_invoice_delete_doc = {
    "tags": [SALES_TAG],
    "summary": "Eliminar factura",
    "operation_id": "delete_sales_invoice",
    "responses": {204: OpenApiResponse(description="Eliminada")},
}
