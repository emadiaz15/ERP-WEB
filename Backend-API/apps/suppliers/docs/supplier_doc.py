from drf_spectacular.utils import OpenApiParameter, OpenApiResponse

from apps.suppliers.api.serializers import (
    SupplierProductDescriptionSerializer,
    SupplierProductDiscountSerializer,
    SupplierCostHistorySerializer,
)

SUPPLIER_TAG = "Suppliers"
CACHE_NOTE = "⚠️ Este recurso utiliza cache de 5 minutos para acelerar lecturas."


supplier_description_list_doc = {
    "tags": [SUPPLIER_TAG],
    "summary": "Listar descripciones por proveedor",
    "operation_id": "list_supplier_product_descriptions",
    "description": (
        "Devuelve las descripciones alternativas asociadas a una relación producto-proveedor específica. "
        + CACHE_NOTE
    ),
    "parameters": [
        OpenApiParameter(
            name="search",
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filtro contains sobre la descripción",
            type=str,
        ),
    ],
    "responses": {
        200: OpenApiResponse(
            response=SupplierProductDescriptionSerializer,
            description="Listado paginado de descripciones",
        )
    },
}

supplier_description_create_doc = {
    "tags": [SUPPLIER_TAG],
    "summary": "Crear descripción por proveedor",
    "operation_id": "create_supplier_product_description",
    "description": "Alta de una descripción alternativa. Invalida cache inmediatamente al completar.",
    "request": SupplierProductDescriptionSerializer,
    "responses": {
        201: OpenApiResponse(response=SupplierProductDescriptionSerializer, description="Descripción creada"),
        400: OpenApiResponse(description="Datos inválidos"),
    },
}

supplier_description_detail_doc = {
    "tags": [SUPPLIER_TAG],
    "summary": "Obtener descripción por proveedor",
    "operation_id": "retrieve_supplier_product_description",
    "description": "Detalle completo de la descripción solicitada.",
    "responses": {
        200: OpenApiResponse(response=SupplierProductDescriptionSerializer, description="Detalle consultado"),
        404: OpenApiResponse(description="No encontrada"),
    },
}

supplier_description_update_doc = {
    "tags": [SUPPLIER_TAG],
    "summary": "Actualizar descripción por proveedor",
    "operation_id": "update_supplier_product_description",
    "description": "Actualiza la descripción y limpia la cache vinculada.",
    "request": SupplierProductDescriptionSerializer,
    "responses": {
        200: OpenApiResponse(response=SupplierProductDescriptionSerializer, description="Descripción actualizada"),
        400: OpenApiResponse(description="Datos inválidos"),
    },
}

supplier_description_delete_doc = {
    "tags": [SUPPLIER_TAG],
    "summary": "Eliminar descripción por proveedor",
    "operation_id": "delete_supplier_product_description",
    "description": "Soft delete de la descripción. Invalida cache y eventos en tiempo real.",
    "responses": {
        204: OpenApiResponse(description="Eliminado"),
        404: OpenApiResponse(description="No encontrada"),
    },
}

supplier_discount_list_doc = {
    "tags": [SUPPLIER_TAG],
    "summary": "Listar descuentos por proveedor",
    "operation_id": "list_supplier_product_discounts",
    "description": (
        "Devuelve los descuentos aplicables configurados en la relación proveedor-producto. "
        + CACHE_NOTE
    ),
    "parameters": [
        OpenApiParameter(
            name="search",
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filtra por dto_codi",
            type=str,
        ),
        OpenApiParameter(
            name="negative_only",
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filtra solo negativos (true/false)",
            type=bool,
        ),
    ],
    "responses": {
        200: OpenApiResponse(response=SupplierProductDiscountSerializer, description="Listado paginado"),
    },
}

supplier_discount_create_doc = {
    "tags": [SUPPLIER_TAG],
    "summary": "Crear descuento por proveedor",
    "operation_id": "create_supplier_product_discount",
    "description": "Registra un nuevo descuento legacy asociado al proveedor.",
    "request": SupplierProductDiscountSerializer,
    "responses": {
        201: OpenApiResponse(response=SupplierProductDiscountSerializer, description="Descuento creado"),
        400: OpenApiResponse(description="Datos inválidos"),
    },
}

supplier_discount_detail_doc = {
    "tags": [SUPPLIER_TAG],
    "summary": "Obtener descuento por proveedor",
    "operation_id": "retrieve_supplier_product_discount",
    "description": "Detalle del descuento configurado.",
    "responses": {
        200: OpenApiResponse(response=SupplierProductDiscountSerializer, description="Detalle consultado"),
        404: OpenApiResponse(description="No encontrado"),
    },
}

supplier_discount_update_doc = {
    "tags": [SUPPLIER_TAG],
    "summary": "Actualizar descuento por proveedor",
    "operation_id": "update_supplier_product_discount",
    "description": "Modifica porcentaje legacy / signo del descuento.",
    "request": SupplierProductDiscountSerializer,
    "responses": {
        200: OpenApiResponse(response=SupplierProductDiscountSerializer, description="Actualizado"),
        400: OpenApiResponse(description="Datos inválidos"),
    },
}

supplier_discount_delete_doc = {
    "tags": [SUPPLIER_TAG],
    "summary": "Eliminar descuento por proveedor",
    "operation_id": "delete_supplier_product_discount",
    "description": "Soft delete e invalidación de cache.",
    "responses": {
        204: OpenApiResponse(description="Eliminado"),
        404: OpenApiResponse(description="No encontrado"),
    },
}

supplier_cost_history_list_doc = {
    "tags": [SUPPLIER_TAG],
    "summary": "Histórico de costos por proveedor",
    "operation_id": "list_supplier_cost_history",
    "description": (
        "Devuelve la trazabilidad de costos y cotizaciones asociadas al proveedor. "
        "Cache 10 minutos para mantener estabilidad."
    ),
    "parameters": [
        OpenApiParameter(
            name="date_from",
            location=OpenApiParameter.QUERY,
            required=False,
            description="Fecha desde (YYYY-MM-DD)",
            type=str,
        ),
        OpenApiParameter(
            name="date_to",
            location=OpenApiParameter.QUERY,
            required=False,
            description="Fecha hasta (YYYY-MM-DD)",
            type=str,
        ),
        OpenApiParameter(
            name="currency",
            location=OpenApiParameter.QUERY,
            required=False,
            description="Código de moneda",
            type=str,
        ),
    ],
    "responses": {
        200: OpenApiResponse(response=SupplierCostHistorySerializer, description="Histórico paginado"),
    },
}
