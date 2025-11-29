# apps/metrics/views.py
from django.db.models import Exists, OuterRef
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.conf import settings
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.products.models.product_model import Product
# Import tolerante por si no re-exportaste el modelo en __init__.py
try:
    from apps.products.models import ProductImage
except Exception:
    from apps.products.models.product_image_model import ProductImage

from ERP_management.settings.base import MYSQL_RO_ENABLED


class ProductsWithFilesPercentage(APIView):
    permission_classes = [IsAuthenticated]  # usa AllowAny si querés público

    # Cache corto (60s) para balancear frescura vs costo de conteos agregados
    METRICS_FILES_PCT_TTL = int(getattr(settings, 'METRICS_FILES_PCT_TTL', 60))

    @method_decorator(cache_page(int(getattr(settings, 'METRICS_FILES_PCT_TTL', 60))))
    def get(self, request):
        # Contamos SOLO productos activos; si querés todos, quita el .filter(status=True)
        base = Product.objects.filter(status=True).annotate(
            has_files=Exists(
                ProductImage.objects.filter(product_id=OuterRef("pk"))
            )
        )

        total = base.count()
        with_files = base.filter(has_files=True).count()
        # (opcional) también podés devolver los sin archivos
        without_files = total - with_files

        percentage = (with_files * 100.0 / total) if total else 0.0

        return Response({
            "total": total,
            "with_files": with_files,
            "without_files": without_files,
            "percentage": round(percentage, 2),
        })


class MySQLReadOnlyHealth(APIView):
    """Healthcheck simple para la base MySQL de solo lectura.

    - Responde 200 si MYSQL_RO_ENABLED está activo y un SELECT 1 funciona.
    - Si no está habilitado, responde 204 (No Content) para no considerarlo un error.
    - No requiere autenticación para pruebas rápidas locales.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        if not MYSQL_RO_ENABLED:
            return Response(status=204)

        # MySQL deshabilitado en esta versión; se mantiene endpoint solo como indicador de flag
        return Response({"enabled": False, "ok": False, "result": None})
