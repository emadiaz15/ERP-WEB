from drf_spectacular.utils import OpenApiParameter, OpenApiResponse

catalog_search_doc = {
    "tags": ["Catalog"],
    "summary": "Buscar artículos con sinónimos y alias",
    "operation_id": "catalog_search",
    "description": (
        "Realiza una búsqueda centralizada sobre artículos, rubros, abreviaciones, "
        "sinónimos y alias. Devuelve coincidencias ordenadas por relevancia con sus métricas clave."
    ),
    "parameters": [
        OpenApiParameter(name="query", location=OpenApiParameter.QUERY, description="Texto libre a buscar", required=False, type=str),
        OpenApiParameter(name="category_id", location=OpenApiParameter.QUERY, description="Filtra por categoría/rubro", required=False, type=int),
        OpenApiParameter(name="customer_legacy_id", location=OpenApiParameter.QUERY, description="Limita a coincidencias específicas de un cliente legacy", required=False, type=int),
        OpenApiParameter(name="supplier_legacy_id", location=OpenApiParameter.QUERY, description="Limita a coincidencias para un proveedor legacy", required=False, type=int),
        OpenApiParameter(name="has_metrics", location=OpenApiParameter.QUERY, description="Solo artículos con métricas calculadas", required=False, type=bool),
        OpenApiParameter(name="include_inactive", location=OpenApiParameter.QUERY, description="Incluye artículos dados de baja", required=False, type=bool),
    ],
    "responses": {
        200: OpenApiResponse(description="Resultados paginados del catálogo"),
    },
}

catalog_insight_doc = {
    "tags": ["Catalog"],
    "summary": "Ficha completa del artículo",
    "operation_id": "catalog_product_insight",
    "description": (
        "Devuelve la ficha enriquecida del artículo incluyendo métricas, alias, sinónimos, "
        "configuraciones por cliente/proveedor y los últimos movimientos de stock."
    ),
    "parameters": [
        OpenApiParameter(name="prod_pk", location=OpenApiParameter.PATH, required=True, type=int, description="ID del producto"),
        OpenApiParameter(name="history_limit", location=OpenApiParameter.QUERY, required=False, type=int, description="Cantidad de movimientos de stock a incluir (max 200)"),
    ],
    "responses": {
        200: OpenApiResponse(description="Ficha enriquecida"),
        404: OpenApiResponse(description="Producto no encontrado"),
    },
}

catalog_history_doc = {
    "tags": ["Catalog"],
    "summary": "Histórico de stock (histostock)",
    "operation_id": "catalog_product_history",
    "description": "Expose los movimientos registrados en HISTOSTOCK para un artículo específico.",
    "parameters": [
        OpenApiParameter(name="prod_pk", location=OpenApiParameter.PATH, required=True, type=int, description="ID del producto"),
        OpenApiParameter(name="limit", location=OpenApiParameter.QUERY, required=False, type=int, description="Cantidad máxima de registros (max 500)"),
    ],
    "responses": {
        200: OpenApiResponse(description="Listado ordenado de movimientos"),
        404: OpenApiResponse(description="Producto no encontrado"),
    },
}
