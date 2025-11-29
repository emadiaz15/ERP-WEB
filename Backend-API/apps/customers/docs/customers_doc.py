from drf_spectacular.utils import OpenApiParameter, OpenApiResponse

from apps.customers.api.serializers import (
    CustomerSerializer,
    CustomerProductDetailSerializer,
)

CUSTOMER_TAG = "Customers"
CACHE_NOTE = "⚠️ Listado cacheado 5 minutos."

customer_list_doc = {
    "tags": [CUSTOMER_TAG],
    "summary": "Listar clientes",
    "description": "Permite filtrar por nombre o zona. " + CACHE_NOTE,
    "operation_id": "list_customers",
    "parameters": [
        OpenApiParameter("search", location=OpenApiParameter.QUERY, description="Nombre", type=str),
        OpenApiParameter("zone", location=OpenApiParameter.QUERY, description="ID zona", type=int),
    ],
    "responses": {200: OpenApiResponse(response=CustomerSerializer)},
}

customer_create_doc = {
    "tags": [CUSTOMER_TAG],
    "summary": "Crear cliente",
    "operation_id": "create_customer",
    "request": CustomerSerializer,
    "responses": {
        201: OpenApiResponse(response=CustomerSerializer, description="Cliente creado"),
        400: OpenApiResponse(description="Datos inválidos"),
    },
}

customer_detail_doc = {
    "tags": [CUSTOMER_TAG],
    "summary": "Detalle cliente",
    "operation_id": "retrieve_customer",
    "responses": {200: OpenApiResponse(response=CustomerSerializer)},
}

customer_update_doc = {
    "tags": [CUSTOMER_TAG],
    "summary": "Actualizar cliente",
    "operation_id": "update_customer",
    "request": CustomerSerializer,
    "responses": {200: OpenApiResponse(response=CustomerSerializer)},
}

customer_delete_doc = {
    "tags": [CUSTOMER_TAG],
    "summary": "Eliminar cliente",
    "operation_id": "delete_customer",
    "responses": {204: OpenApiResponse(description="Eliminado")},
}

customer_product_list_doc = {
    "tags": [CUSTOMER_TAG],
    "summary": "Listar descripciones de producto por cliente",
    "description": CACHE_NOTE,
    "operation_id": "list_customer_product_details",
    "parameters": [
        OpenApiParameter("customer", location=OpenApiParameter.QUERY, description="ID cliente", type=int),
        OpenApiParameter("product", location=OpenApiParameter.QUERY, description="ID producto", type=int),
    ],
    "responses": {200: OpenApiResponse(response=CustomerProductDetailSerializer)},
}

customer_product_create_doc = {
    "tags": [CUSTOMER_TAG],
    "summary": "Crear descripción personalizada",
    "operation_id": "create_customer_product_detail",
    "request": CustomerProductDetailSerializer,
    "responses": {
        201: OpenApiResponse(response=CustomerProductDetailSerializer, description="Detalle creado"),
        400: OpenApiResponse(description="Datos inválidos"),
    },
}

customer_product_detail_doc = {
    "tags": [CUSTOMER_TAG],
    "summary": "Detalle descripción personalizada",
    "operation_id": "retrieve_customer_product_detail",
    "responses": {200: OpenApiResponse(response=CustomerProductDetailSerializer)},
}

customer_product_update_doc = {
    "tags": [CUSTOMER_TAG],
    "summary": "Actualizar descripción personalizada",
    "operation_id": "update_customer_product_detail",
    "request": CustomerProductDetailSerializer,
    "responses": {200: OpenApiResponse(response=CustomerProductDetailSerializer)},
}

customer_product_delete_doc = {
    "tags": [CUSTOMER_TAG],
    "summary": "Eliminar descripción personalizada",
    "operation_id": "delete_customer_product_detail",
    "responses": {204: OpenApiResponse(description="Eliminado")},
}
