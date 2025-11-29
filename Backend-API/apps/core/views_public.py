from django.db import connection
from django.db.utils import OperationalError
from django.http import HttpResponse, JsonResponse
from django.utils import timezone


def service_health_view(_request):
    """Minimal JSON health check used by containers and external monitors."""
    payload = {
        "status": "ok",
        "timestamp": timezone.now().isoformat(),
        "database": "ok",
    }

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            cursor.fetchone()
    except OperationalError as exc:  # pragma: no cover - only hit on infra issues
        payload["status"] = "error"
        payload["database"] = "error"
        payload["detail"] = str(exc)
        return JsonResponse(payload, status=503)

    return JsonResponse(payload)


def robots_txt(request):
    """Return a minimal robots.txt allowing all crawlers.

    Added to satisfy import in inventory_management/urls.py. Includes a Cache-Control
    header so that crawlers/CDNs can cache it for 1 hour.
    """
    content = "User-agent: *\nDisallow:\n"
    response = HttpResponse(content, content_type="text/plain")
    response["Cache-Control"] = "public, max-age=3600"
    return response
