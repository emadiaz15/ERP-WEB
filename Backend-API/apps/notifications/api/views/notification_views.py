from django.conf import settings
from django.views.decorators.cache import cache_page
from apps.notifications.utils.cache_decorators import cache_decorator_list, cache_decorator_detail
from apps.notifications.utils.cache_invalidation import invalidate_notification_cache
from apps.core.utils import broadcast_crud_event
# apps/notifications/api/views/notification_views.py
from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from apps.core.pagination import Pagination
from apps.notifications.models.notification_model import Notification
from apps.notifications.api.serializers.notification_serializer import NotificationSerializer
from apps.notifications.utils.cache_decorators import get_notification_cache_metrics


@extend_schema(
    summary="List my notifications",
    description=(
        "Returns the authenticated user's notifications ordered by -created_at.\n\n"
        "- Supports **read=true|false** to filter explicitly by read state (takes precedence).\n"
        "- Supports **unread=true** for backward compatibility (only non-read).\n"
        "- Optionally supports **type=<value>** to filter by type."
    ),
    parameters=[
        OpenApiParameter(
            name="read",
            type=OpenApiTypes.BOOL,
            required=False,
            description="Filter by read state (true/false). Takes precedence over `unread`."
        ),
        OpenApiParameter(
            name="unread",
            type=OpenApiTypes.BOOL,
            required=False,
            description="Only unread if true (kept for backward compatibility)."
        ),
        OpenApiParameter(
            name="type",
            type=OpenApiTypes.STR,
            required=False,
            description="Filter by notification type (exact match)."
        ),
    ],
    tags=["Notifications"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
@cache_decorator_list
def my_notifications_list(request):
    qs = Notification.objects.filter(user=request.user, status=True).order_by("-created_at")

    # read tiene prioridad si viene especificado
    read_param = request.query_params.get("read", None)
    if read_param is not None:
        read_bool = str(read_param).lower() in ("1", "true", "yes")
        qs = qs.filter(is_read=read_bool)
    else:
        # compat: unread=true
        unread = request.query_params.get("unread")
        if str(unread).lower() in ("1", "true", "yes"):
            qs = qs.filter(is_read=False)

    # ✅ filtro por tipo (campo real es notif_type)
    # aceptamos ambos: ?type=... (compat) y ?notif_type=... (explícito)
    type_param = request.query_params.get("notif_type") or request.query_params.get("type")
    if type_param:
        qs = qs.filter(notif_type=type_param)

    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    ser = NotificationSerializer(page, many=True, context={"request": request})
    return paginator.get_paginated_response(ser.data)


@extend_schema(
    summary="Notification detail",
    description="Returns a single notification owned by the authenticated user.",
    tags=["Notifications"],
    responses=NotificationSerializer,
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
@cache_decorator_detail
def my_notification_detail(request, notif_pk: int):
    notif = get_object_or_404(
        Notification,
        pk=notif_pk,
        status=True,
        user=request.user,
    )
    ser = NotificationSerializer(notif, context={"request": request})
    return Response(ser.data)


@extend_schema(
    summary="Unread count",
    description="Returns the count of unread notifications for the authenticated user.",
    tags=["Notifications"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_notifications_unread_count(request):
    count = Notification.objects.filter(
        user=request.user, status=True, is_read=False
    ).count()
    # contrato actual del frontend: { unread }
    return Response({"unread": count})


@extend_schema(
    summary="Notifications summary (list + unread count)",
    description=(
        "Combina la lista paginada de notificaciones y el conteo de no leídas en **una sola llamada**.\n\n"
        "Query params soportados: mismos que /notifications/ (read, unread, type).\n"
        "Respuesta: { unread: <int>, count, next, previous, results: [...] }"
    ),
    parameters=[
        OpenApiParameter(
            name="read",
            type=OpenApiTypes.BOOL,
            required=False,
            description="Filtra por estado leído (true/false). Tiene prioridad sobre unread."
        ),
        OpenApiParameter(
            name="unread",
            type=OpenApiTypes.BOOL,
            required=False,
            description="Solo no leídas si true (compat)."
        ),
        OpenApiParameter(
            name="type",
            type=OpenApiTypes.STR,
            required=False,
            description="Filtra por tipo de notificación."
        ),
    ],
    tags=["Notifications"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
@cache_decorator_list
def my_notifications_summary(request):
    """Devuelve lista paginada + conteo unread en un payload."""
    qs = Notification.objects.filter(user=request.user, status=True).order_by("-created_at")

    read_param = request.query_params.get("read", None)
    if read_param is not None:
        read_bool = str(read_param).lower() in ("1", "true", "yes")
        qs = qs.filter(is_read=read_bool)
    else:
        unread = request.query_params.get("unread")
        if str(unread).lower() in ("1", "true", "yes"):
            qs = qs.filter(is_read=False)

    type_param = request.query_params.get("notif_type") or request.query_params.get("type")
    if type_param:
        qs = qs.filter(notif_type=type_param)

    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    ser = NotificationSerializer(page, many=True, context={"request": request})

    # Conteo unread global (independiente de filtros read= / unread= para que el frontend siempre conozca el total pendiente)
    unread_total = Notification.objects.filter(user=request.user, status=True, is_read=False).count()

    paginated = paginator.get_paginated_response(ser.data)
    data = paginated.data
    data["unread"] = unread_total
    return Response(data)


@extend_schema(
    summary="Notification cache metrics",
    description="Métricas simples en memoria de hits/miss/sets del cache de notificaciones.",
    tags=["Notifications"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notification_cache_metrics(request):
    return Response(get_notification_cache_metrics())


@extend_schema(
    summary="Mark one notification as read",
    description="Marks a single notification as read (owner only).",
    tags=["Notifications"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notif_pk: int):
    notif = get_object_or_404(Notification, pk=notif_pk, status=True)
    if notif.user_id != request.user.id:
        return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)


    if not notif.is_read:
        notif.is_read = True
        notif.read_at = timezone.now()
        notif.save(update_fields=["is_read", "read_at", "modified_at", "modified_by"])
        # Invalidar cache de este usuario
        invalidate_notification_cache(user_id=request.user.id)
        # Emitir evento WebSocket para notificar actualización de notificación
        ser = NotificationSerializer(notif, context={"request": request})
        broadcast_crud_event(
            event_type="update",
            app="notifications",
            model="Notification",
            data=ser.data,
        )

    # contrato actual del frontend: { ok: true }
    return Response({"ok": True})


@extend_schema(
    summary="Mark ALL notifications as read",
    description="Marks all notifications of the authenticated user as read.",
    tags=["Notifications"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    qs = Notification.objects.filter(user=request.user, status=True, is_read=False)
    now = timezone.now()
    qs.update(is_read=True, read_at=now)
    # Invalidar cache de este usuario
    invalidate_notification_cache(user_id=request.user.id)
    # Emitir evento WebSocket para notificar actualización masiva
    # (Enviamos solo los IDs marcados como leídos)
    notif_ids = list(qs.values_list('id', flat=True))
    broadcast_crud_event(
        event_type="update",
        app="notifications",
        model="Notification",
        data={"ids": notif_ids, "is_read": True},
    )
    return Response({"ok": True})
