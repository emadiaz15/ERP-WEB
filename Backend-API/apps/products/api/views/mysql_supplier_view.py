"""Vistas que exponen datos de MySQL readonly para proveedores."""
from __future__ import annotations

from typing import Any, Dict

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ERP_management.settings.base import MYSQL_RO_ENABLED as is_mysql_enabled
from inventory_management.database import mysql_queries


def _build_payload(supplier_id: int, data: Any) -> Dict[str, Any]:
    return {"supplier_id": supplier_id, "count": len(data), "results": data}


@extend_schema(
    operation_id="supplier_products_mysql",
    summary="Productos y costos del proveedor (MySQL readonly)",
    parameters=[],
    responses={200: {"type": "object"}},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def supplier_products_view(request, supplier_id: int):
    """Lista artículos asociados a un proveedor desde la DB externa."""
    if not is_mysql_enabled():
        return Response(
            {"detail": "Integración MySQL deshabilitada."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    products = mysql_queries.fetch_supplier_products(supplier_id)
    return Response(_build_payload(supplier_id, products))


@extend_schema(
    operation_id="supplier_purchases_mysql",
    summary="Órdenes de compra del proveedor (MySQL readonly)",
    parameters=[],
    responses={200: {"type": "object"}},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def supplier_purchases_view(request, supplier_id: int):
    """Lista órdenes de compra e items asociados de la DB externa."""
    if not is_mysql_enabled():
        return Response(
            {"detail": "Integración MySQL deshabilitada."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    purchases = mysql_queries.fetch_supplier_purchases(supplier_id)
    return Response(_build_payload(supplier_id, purchases))
