"""OpenAPI documentation for supplier product price history endpoints."""

from drf_spectacular.utils import OpenApiResponse, OpenApiParameter
from apps.products.api.serializers import (
    SupplierProductPriceHistorySerializer,
    SupplierProductPriceHistoryCreateSerializer,
)


list_supplier_price_history_doc = {
    "tags": ["Products - Supplier Price History"],
    "summary": "Listar histórico de precios",
    "operation_id": "list_supplier_price_history",
    "description": """
    Obtiene todo el histórico de precios de un producto de proveedor.

    **Retorna**:
    - Lista completa de registros de precios ordenados por fecha descendente
    - El primer registro es el precio actual (valid_to=NULL)
    - Incluye información del usuario que realizó cada cambio
    - Muestra duración de vigencia de cada precio

    **Permisos**: ADMIN, MANAGER, WAREHOUSE, SALES, BILLING, READONLY

    **Ejemplo de uso**:
    - Analizar tendencias de precios de un proveedor
    - Auditar cambios históricos de costos
    - Generar reportes de variación de precios
    """,
    "parameters": [
        OpenApiParameter(
            name="supplier_product_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=int,
            description="ID del producto de proveedor"
        )
    ],
    "responses": {
        200: OpenApiResponse(
            description="Histórico de precios obtenido exitosamente",
            response={
                "type": "object",
                "properties": {
                    "supplier_product_id": {"type": "integer"},
                    "product_name": {"type": "string"},
                    "supplier_id": {"type": "integer"},
                    "total_records": {"type": "integer"},
                    "history": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/SupplierProductPriceHistory"}
                    }
                }
            }
        ),
        404: OpenApiResponse(description="Producto de proveedor no encontrado"),
        403: OpenApiResponse(description="Sin permisos para ver histórico de precios"),
        401: OpenApiResponse(description="No autenticado"),
    }
}


create_supplier_price_history_doc = {
    "tags": ["Products - Supplier Price History"],
    "summary": "Crear registro de precio manual",
    "operation_id": "create_supplier_price_history",
    "description": """
    Crea manualmente un registro en el histórico de precios.

    **Uso principal**:
    - Importar datos históricos de precios
    - Registrar cambios especiales de precio con notas
    - Corregir registros históricos

    **Nota importante**: Los cambios de precio realizados mediante la actualización
    del modelo SupplierProduct se registran automáticamente vía signal.
    Este endpoint es para casos especiales donde se necesita crear registros manualmente.

    **Comportamiento**:
    - Cierra automáticamente el registro de precio anterior (marca valid_to)
    - El nuevo registro se convierte en el precio actual (valid_to=NULL)
    - Registra el usuario que realizó el cambio

    **Permisos**: ADMIN, MANAGER, WAREHOUSE
    """,
    "parameters": [
        OpenApiParameter(
            name="supplier_product_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=int,
            description="ID del producto de proveedor"
        )
    ],
    "request": SupplierProductPriceHistoryCreateSerializer,
    "responses": {
        201: OpenApiResponse(
            response=SupplierProductPriceHistorySerializer,
            description="Registro de precio creado exitosamente"
        ),
        400: OpenApiResponse(description="Datos inválidos"),
        404: OpenApiResponse(description="Producto de proveedor no encontrado"),
        403: OpenApiResponse(description="Sin permisos para crear registros de precio"),
        401: OpenApiResponse(description="No autenticado"),
    }
}


get_supplier_price_history_detail_doc = {
    "tags": ["Products - Supplier Price History"],
    "summary": "Obtener detalle de registro de precio",
    "operation_id": "get_supplier_price_history_detail",
    "description": """
    Obtiene los detalles de un registro específico del histórico de precios.

    **Retorna**:
    - Información completa del registro de precio
    - Usuario que realizó el cambio
    - Periodo de vigencia (valid_from - valid_to)
    - Notas asociadas al cambio

    **Permisos**: ADMIN, MANAGER, WAREHOUSE, SALES, BILLING, READONLY
    """,
    "parameters": [
        OpenApiParameter(
            name="supplier_product_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=int,
            description="ID del producto de proveedor"
        ),
        OpenApiParameter(
            name="history_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=int,
            description="ID del registro de histórico de precio"
        )
    ],
    "responses": {
        200: OpenApiResponse(
            response=SupplierProductPriceHistorySerializer,
            description="Detalle del registro obtenido exitosamente"
        ),
        404: OpenApiResponse(description="Registro de precio no encontrado"),
        403: OpenApiResponse(description="Sin permisos para ver histórico de precios"),
        401: OpenApiResponse(description="No autenticado"),
    }
}


get_current_supplier_price_doc = {
    "tags": ["Products - Supplier Price History"],
    "summary": "Obtener precio actual",
    "operation_id": "get_current_supplier_price",
    "description": """
    Obtiene el precio actualmente vigente para un producto de proveedor.

    **Retorna**: El registro de precio con valid_to=NULL (precio actual)

    **Uso**:
    - Consultar precio vigente antes de crear una orden de compra
    - Verificar última actualización de precio
    - Validar costos actuales para cálculos

    **Permisos**: ADMIN, MANAGER, WAREHOUSE, SALES, BILLING, READONLY
    """,
    "parameters": [
        OpenApiParameter(
            name="supplier_product_id",
            location=OpenApiParameter.PATH,
            required=True,
            type=int,
            description="ID del producto de proveedor"
        )
    ],
    "responses": {
        200: OpenApiResponse(
            response=SupplierProductPriceHistorySerializer,
            description="Precio actual obtenido exitosamente"
        ),
        404: OpenApiResponse(description="No se encontró precio actual para este producto"),
        403: OpenApiResponse(description="Sin permisos para ver precios"),
        401: OpenApiResponse(description="No autenticado"),
    }
}
