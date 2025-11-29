from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ERP_management.settings.base import MYSQL_RO_ENABLED


@extend_schema(
    operation_id="public_home_view",
    description="Public Home page for unauthenticated users",
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}},
)
@api_view(['GET'])
def public_home_view(request):
    """
    Vista pública para el Home de la aplicación.
    Accesible sin autenticación.
    """
    base_url = request.build_absolute_uri("/").rstrip("/")
    return Response(
        {
            "service": "Inventory Management API",
            "status": "ok",
            "links": {
                "docs": f"{base_url}/api/v1/docs/swagger-ui/",
                "schema": f"{base_url}/api/v1/docs/schema/",
                "health": f"{base_url}/health/",
                "api_root": f"{base_url}/api/v1/",
            },
        }
    )


@extend_schema(
    operation_id="dashboard_view",
    description="Dashboard for authenticated users",
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}},
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    """
    Vista del Dashboard de la aplicación.
    Solo accesible para usuarios autenticados.
    """
    return Response({"message": "Welcome to the Dashboard!"})


@extend_schema(
    operation_id="mysql_readonly_health",
    description="Verifica la conectividad contra la base MySQL de solo lectura.",
    responses={
        200: {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "result": {"type": "integer", "nullable": True},
            },
        },
        503: {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "detail": {"type": "string"},
            },
        },
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mysql_readonly_health_view(request):
    """Endpoint de salud para la integración MySQL readonly."""
    if not MYSQL_RO_ENABLED:
        return Response({"status": "disabled", "result": None}, status=status.HTTP_200_OK)

    # MySQL deshabilitado en esta versión; se mantiene endpoint solo como indicador de flag
    return Response({"status": "disabled", "result": None}, status=status.HTTP_200_OK)
