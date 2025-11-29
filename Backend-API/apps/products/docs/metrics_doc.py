from drf_spectacular.utils import OpenApiParameter, OpenApiResponse

metrics_list_doc = {
    "tags": ["Catalog", "Metrics"],
    "summary": "Listar métricas agregadas",
    "operation_id": "catalog_metrics_list",
    "description": "Permite explorar la tabla art_metricas filtrando por rubro, rotación o antigüedad de ventas.",
    "parameters": [
        OpenApiParameter(name="category_id", location=OpenApiParameter.QUERY, required=False, type=int, description="Filtra por categoría"),
        OpenApiParameter(name="rotation_min", location=OpenApiParameter.QUERY, required=False, type=int, description="Rotación mínima"),
        OpenApiParameter(name="rotation_max", location=OpenApiParameter.QUERY, required=False, type=int, description="Rotación máxima"),
        OpenApiParameter(name="days_since_last_sale", location=OpenApiParameter.QUERY, required=False, type=int, description="Días desde la última venta"),
        OpenApiParameter(name="include_inactive", location=OpenApiParameter.QUERY, required=False, type=bool, description="Incluye métricas de artículos inactivos"),
    ],
    "responses": {200: OpenApiResponse(description="Listado paginado")},
}

metrics_detail_doc = {
    "tags": ["Catalog", "Metrics"],
    "summary": "Consultar / actualizar métricas",
    "operation_id": "catalog_metrics_detail",
    "parameters": [
        OpenApiParameter(name="prod_pk", location=OpenApiParameter.PATH, required=True, type=int, description="ID del producto"),
    ],
    "responses": {
        200: OpenApiResponse(description="Métricas encontradas"),
        201: OpenApiResponse(description="Métricas creadas"),
        404: OpenApiResponse(description="Producto o métricas no encontradas"),
    },
}
