from drf_spectacular.utils import OpenApiParameter, OpenApiResponse

from apps.expenses.api.serializers import (
    ExpenseSerializer,
    ExpensePaymentSerializer,
    ExpenseTypeSerializer,
    ExpensePaymentAllocationSerializer,
)

EXPENSES_TAG = "Expenses"
CACHE_NOTE = "⚠️ Respuesta cacheada por 5 minutos en ambientes productivos."

expense_type_list_doc = {
    "tags": [EXPENSES_TAG],
    "summary": "Listar tipos de gasto",
    "description": "Catálogo administrable de categorías de gasto. " + CACHE_NOTE,
    "operation_id": "list_expense_types",
    "responses": {200: OpenApiResponse(response=ExpenseTypeSerializer)},
}

expense_type_create_doc = {
    "tags": [EXPENSES_TAG],
    "summary": "Crear tipo de gasto",
    "operation_id": "create_expense_type",
    "request": ExpenseTypeSerializer,
    "responses": {
        201: OpenApiResponse(response=ExpenseTypeSerializer, description="Tipo creado"),
        400: OpenApiResponse(description="Datos inválidos"),
    },
}

expense_type_detail_doc = {
    "tags": [EXPENSES_TAG],
    "summary": "Detalle tipo de gasto",
    "operation_id": "retrieve_expense_type",
    "responses": {200: OpenApiResponse(response=ExpenseTypeSerializer)},
}

expense_type_update_doc = {
    "tags": [EXPENSES_TAG],
    "summary": "Actualizar tipo de gasto",
    "operation_id": "update_expense_type",
    "request": ExpenseTypeSerializer,
    "responses": {200: OpenApiResponse(response=ExpenseTypeSerializer)},
}

expense_type_delete_doc = {
    "tags": [EXPENSES_TAG],
    "summary": "Eliminar tipo de gasto",
    "operation_id": "delete_expense_type",
    "responses": {204: OpenApiResponse(description="Eliminado")},
}

expense_list_doc = {
    "tags": [EXPENSES_TAG],
    "summary": "Listar gastos",
    "description": "Listado paginado con filtros por tipo, persona, estado y rango de fechas. " + CACHE_NOTE,
    "operation_id": "list_expenses",
    "parameters": [
        OpenApiParameter("type", location=OpenApiParameter.QUERY, description="ID del tipo de gasto", type=int),
        OpenApiParameter("status", location=OpenApiParameter.QUERY, description="Estado lógico", type=str),
        OpenApiParameter("person", location=OpenApiParameter.QUERY, description="ID legacy de persona", type=int),
        OpenApiParameter("date_from", location=OpenApiParameter.QUERY, description="Fecha desde (YYYY-MM-DD)", type=str),
        OpenApiParameter("date_to", location=OpenApiParameter.QUERY, description="Fecha hasta (YYYY-MM-DD)", type=str),
        OpenApiParameter("search", location=OpenApiParameter.QUERY, description="Texto en concepto/observaciones", type=str),
    ],
    "responses": {200: OpenApiResponse(response=ExpenseSerializer)},
}

expense_create_doc = {
    "tags": [EXPENSES_TAG],
    "summary": "Crear gasto",
    "operation_id": "create_expense",
    "request": ExpenseSerializer,
    "responses": {
        201: OpenApiResponse(response=ExpenseSerializer, description="Gasto creado"),
        400: OpenApiResponse(description="Datos inválidos"),
    },
}

expense_detail_doc = {
    "tags": [EXPENSES_TAG],
    "summary": "Detalle de gasto",
    "operation_id": "retrieve_expense",
    "responses": {200: OpenApiResponse(response=ExpenseSerializer)},
}

expense_update_doc = {
    "tags": [EXPENSES_TAG],
    "summary": "Actualizar gasto",
    "operation_id": "update_expense",
    "request": ExpenseSerializer,
    "responses": {200: OpenApiResponse(response=ExpenseSerializer)},
}

expense_delete_doc = {
    "tags": [EXPENSES_TAG],
    "summary": "Eliminar gasto",
    "operation_id": "delete_expense",
    "responses": {204: OpenApiResponse(description="Eliminado")},
}

expense_approve_doc = {
    "tags": [EXPENSES_TAG],
    "summary": "Aprobar gasto",
    "operation_id": "approve_expense",
    "request": None,
    "responses": {200: OpenApiResponse(response=ExpenseSerializer)},
    "description": "Transición del gasto a estado aprobado con control de workflow.",
}

expense_payment_list_doc = {
    "tags": [EXPENSES_TAG],
    "summary": "Listar pagos de gastos",
    "description": "Pagos y aplicaciones contra gastos. " + CACHE_NOTE,
    "operation_id": "list_expense_payments",
    "parameters": [
        OpenApiParameter("person", location=OpenApiParameter.QUERY, description="ID legacy de persona", type=int),
        OpenApiParameter("status", location=OpenApiParameter.QUERY, description="Estado del pago", type=str),
        OpenApiParameter("date_from", location=OpenApiParameter.QUERY, description="Fecha desde", type=str),
        OpenApiParameter("date_to", location=OpenApiParameter.QUERY, description="Fecha hasta", type=str),
    ],
    "responses": {200: OpenApiResponse(response=ExpensePaymentSerializer)},
}

expense_payment_create_doc = {
    "tags": [EXPENSES_TAG],
    "summary": "Registrar pago de gasto",
    "operation_id": "create_expense_payment",
    "request": ExpensePaymentSerializer,
    "responses": {
        201: OpenApiResponse(response=ExpensePaymentSerializer, description="Pago registrado"),
        400: OpenApiResponse(description="Datos inválidos"),
    },
}

expense_payment_detail_doc = {
    "tags": [EXPENSES_TAG],
    "summary": "Detalle de pago",
    "operation_id": "retrieve_expense_payment",
    "responses": {200: OpenApiResponse(response=ExpensePaymentSerializer)},
}

expense_payment_delete_doc = {
    "tags": [EXPENSES_TAG],
    "summary": "Eliminar pago",
    "operation_id": "delete_expense_payment",
    "responses": {204: OpenApiResponse(description="Eliminado")},
}

expense_payment_allocation_doc = {
    "tags": [EXPENSES_TAG],
    "summary": "Imputar pago a gasto",
    "operation_id": "allocate_expense_payment",
    "request": ExpensePaymentAllocationSerializer,
    "responses": {200: OpenApiResponse(response=ExpensePaymentSerializer)},
    "description": "Registra imputaciones parciales/total y recalcula retenciones automáticas.",
}
