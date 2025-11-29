from drf_spectacular.utils import OpenApiParameter, OpenApiResponse

abbreviation_list_doc = {
    "tags": ["Catalog", "Dictionary"],
    "summary": "Listar / crear abreviaciones",
    "operation_id": "catalog_abbreviation_list",
    "description": "Gestiona las abreviaciones conocidas por artículo (tabla articulo_abreviaciones).",
    "parameters": [
        OpenApiParameter(name="product_id", location=OpenApiParameter.QUERY, required=False, type=int, description="Filtra por producto"),
    ],
    "responses": {200: OpenApiResponse(description="Listado de abreviaciones activas")},
}

abbreviation_detail_doc = {
    "tags": ["Catalog", "Dictionary"],
    "summary": "Detalle de abreviación",
    "operation_id": "catalog_abbreviation_detail",
    "parameters": [
        OpenApiParameter(name="pk", location=OpenApiParameter.PATH, required=True, type=int, description="ID de la abreviación"),
    ],
    "responses": {
        200: OpenApiResponse(description="Detalle"),
        404: OpenApiResponse(description="No encontrado"),
    },
}

synonym_list_doc = {
    "tags": ["Catalog", "Dictionary"],
    "summary": "Listar / crear sinónimos",
    "operation_id": "catalog_synonym_list",
    "parameters": [
        OpenApiParameter(name="product_id", location=OpenApiParameter.QUERY, required=False, type=int, description="Filtra por producto"),
    ],
    "responses": {200: OpenApiResponse(description="Listado de sinónimos activos")},
}

synonym_detail_doc = {
    "tags": ["Catalog", "Dictionary"],
    "summary": "Detalle de sinónimo",
    "operation_id": "catalog_synonym_detail",
    "parameters": [
        OpenApiParameter(name="pk", location=OpenApiParameter.PATH, required=True, type=int, description="ID del sinónimo"),
    ],
    "responses": {
        200: OpenApiResponse(description="Detalle"),
        404: OpenApiResponse(description="No encontrado"),
    },
}

term_list_doc = {
    "tags": ["Catalog", "Dictionary"],
    "summary": "Listar / crear términos globales",
    "operation_id": "catalog_term_list",
    "responses": {200: OpenApiResponse(description="Listado de términos")},
}

term_detail_doc = {
    "tags": ["Catalog", "Dictionary"],
    "summary": "Detalle de término",
    "operation_id": "catalog_term_detail",
    "parameters": [
        OpenApiParameter(name="pk", location=OpenApiParameter.PATH, required=True, type=int, description="ID del término"),
    ],
    "responses": {
        200: OpenApiResponse(description="Detalle"),
        404: OpenApiResponse(description="No encontrado"),
    },
}

alias_list_doc = {
    "tags": ["Catalog", "Dictionary"],
    "summary": "Listar / crear alias IA",
    "operation_id": "catalog_alias_list",
    "parameters": [
        OpenApiParameter(name="product_id", location=OpenApiParameter.QUERY, required=False, type=int, description="Filtra por producto"),
        OpenApiParameter(name="client_legacy_id", location=OpenApiParameter.QUERY, required=False, type=int, description="Filtra por cliente legacy"),
    ],
    "responses": {200: OpenApiResponse(description="Listado de alias")},
}

alias_detail_doc = {
    "tags": ["Catalog", "Dictionary"],
    "summary": "Detalle de alias",
    "operation_id": "catalog_alias_detail",
    "parameters": [
        OpenApiParameter(name="pk", location=OpenApiParameter.PATH, required=True, type=int, description="ID del alias"),
    ],
    "responses": {
        200: OpenApiResponse(description="Detalle"),
        404: OpenApiResponse(description="No encontrado"),
    },
}
