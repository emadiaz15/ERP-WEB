from apps.cuts.utils.cache_decorators import list_cache, detail_cache
from apps.cuts.utils.cache_invalidation import invalidate_cutting_order_cache
from apps.core.utils import broadcast_crud_event
# apps/cuts/api/views/cutting_view.py
import logging
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema

from apps.core.pagination import Pagination
from apps.cuts.api.serializers.cutting_order_serializer import CuttingOrderSerializer
from apps.cuts.api.repositories.cutting_order_repository import CuttingOrderRepository
from apps.cuts.docs.cutting_order_doc import (
    list_assigned_cutting_orders_doc,
    list_cutting_orders_doc,
    create_cutting_order_doc,
    get_cutting_order_by_id_doc,
    update_cutting_order_by_id_doc,
    delete_cutting_order_by_id_doc
)
from apps.cuts.filters.cutting_order_filter import CuttingOrderFilter

from apps.cuts.services.cuts_services import (
    create_full_cutting_order,
    cancel_cutting_order,
    complete_order_processing,
)

# ⬇️ NUEVO: usar helpers robustos con reintentos
from apps.cuts.services.notification_sender import (
    send_cut_assignment_notification,
    send_cut_status_change_notification,
    send_cutting_order_status_global,
)

logger = logging.getLogger(__name__)


@extend_schema(
    summary=list_assigned_cutting_orders_doc["summary"],
    description=list_assigned_cutting_orders_doc["description"],
    tags=list_assigned_cutting_orders_doc["tags"],
    operation_id=list_assigned_cutting_orders_doc["operation_id"],
    parameters=list_assigned_cutting_orders_doc["parameters"],
    responses=list_assigned_cutting_orders_doc["responses"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@list_cache
def cutting_order_assigned_list(request):
    qs = CuttingOrderRepository.get_cutting_orders_assigned_to(request.user)
    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = CuttingOrderSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@extend_schema(
    summary=list_cutting_orders_doc["summary"],
    description=list_cutting_orders_doc["description"],
    tags=list_cutting_orders_doc["tags"],
    operation_id=list_cutting_orders_doc["operation_id"],
    parameters=list_cutting_orders_doc["parameters"],
    responses=list_cutting_orders_doc["responses"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # cualquier usuario autenticado puede ver el historial
@list_cache
def cutting_order_list(request):
    qs = CuttingOrderRepository.get_all_active()

    f = CuttingOrderFilter(request.GET, queryset=qs, request=request)
    if not f.is_valid():
        return Response(f.errors, status=status.HTTP_400_BAD_REQUEST)
    qs = f.qs

    paginator = Pagination()
    page = paginator.paginate_queryset(qs, request)
    serializer = CuttingOrderSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@extend_schema(
    summary=create_cutting_order_doc["summary"],
    description=create_cutting_order_doc["description"],
    tags=create_cutting_order_doc["tags"],
    operation_id=create_cutting_order_doc["operation_id"],
    request=create_cutting_order_doc["requestBody"],
    responses=create_cutting_order_doc["responses"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def cutting_order_create(request):
    serializer = CuttingOrderSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        data = serializer.validated_data

        items = []
        if 'items' in data:
            items = [
                {
                    'subproduct': item['subproduct'].id,
                    'cutting_quantity': str(item['cutting_quantity'])
                }
                for item in data['items']
            ]

        order = create_full_cutting_order(
            product_id=data['product'].id,
            quantity_to_cut=str(data['quantity_to_cut']),
            items=items,
            customer=data['customer'],
            user_creator=request.user,
            assigned_to_id=data.get('assigned_to').id if data.get('assigned_to') else None,
            order_number=data['order_number'],
            operator_can_edit_items=data.get('operator_can_edit_items', False)
        )

        if order.assigned_to:
            send_cut_assignment_notification(
                user_id=order.assigned_to.id,
                order_id=order.id,
                queue="notifications"  # opcional, si ruteás por cola
            )

        # Invalidar caché tras crear
        invalidate_cutting_order_cache()

        # Emitir evento global para refresco de dashboards
        send_cutting_order_status_global(order_id=order.id, workflow_status=order.workflow_status)

        resp = CuttingOrderSerializer(order, context={'request': request})
        # Emitir evento WebSocket para notificar creación
        broadcast_crud_event(
            event_type="create",
            app="cuts",
            model="CuttingOrder",
            data=resp.data,
        )
        return Response(resp.data, status=status.HTTP_201_CREATED)

    except IntegrityError:
        return Response(
            {"order_number": "Ya existe una orden con ese número."},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.exception("Error al crear orden de corte")
        detail = getattr(e, 'detail', str(e))
        code = (
            status.HTTP_400_BAD_REQUEST
            if isinstance(e, (serializers.ValidationError, ValidationError))
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        return Response({"detail": detail}, status=code)


@extend_schema(
    summary=get_cutting_order_by_id_doc["summary"],
    description=get_cutting_order_by_id_doc["description"],
    tags=get_cutting_order_by_id_doc["tags"],
    operation_id=get_cutting_order_by_id_doc["operation_id"],
    parameters=get_cutting_order_by_id_doc["parameters"],
    responses=get_cutting_order_by_id_doc["responses"]
)
@extend_schema(
    summary=update_cutting_order_by_id_doc["summary"],
    description=update_cutting_order_by_id_doc["description"],
    tags=update_cutting_order_by_id_doc["tags"],
    operation_id=update_cutting_order_by_id_doc["operation_id"],
    parameters=update_cutting_order_by_id_doc["parameters"],
    request=update_cutting_order_by_id_doc["requestBody"],
    responses=update_cutting_order_by_id_doc["responses"]
)
@extend_schema(
    summary=delete_cutting_order_by_id_doc["summary"],
    description=delete_cutting_order_by_id_doc["description"],
    tags=delete_cutting_order_by_id_doc["tags"],
    operation_id=delete_cutting_order_by_id_doc["operation_id"],
    parameters=delete_cutting_order_by_id_doc["parameters"],
    responses=delete_cutting_order_by_id_doc["responses"]
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@detail_cache
def cutting_order_detail(request, cuts_pk):
    order = CuttingOrderRepository.get_by_id(cuts_pk)
    if not order:
        return Response({"detail": "Orden de corte no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        ser = CuttingOrderSerializer(order, context={'request': request})
        return Response(ser.data)

    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response({"detail": "Solo staff puede eliminar órdenes."}, status=status.HTTP_403_FORBIDDEN)
        try:
            CuttingOrderRepository.soft_delete(order, request.user)
            # Invalidar caché tras borrar
            invalidate_cutting_order_cache()
            # Emitir evento WebSocket para notificar borrado
            broadcast_crud_event(
                event_type="delete",
                app="cuts",
                model="CuttingOrder",
                data={"id": order.id},
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.exception("Error eliminando orden %s", cuts_pk)
            return Response({"detail": "Error interno al eliminar la orden."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    partial = (request.method == 'PATCH')
    payload = request.data

    is_staff = request.user.is_staff
    is_assigned = (order.assigned_to_id == request.user.id)

    allowed_fields = {"workflow_status"}
    if order.operator_can_edit_items:
        allowed_fields.add("items")

    only_workflow_or_items = set(payload.keys()).issubset(allowed_fields)

    if not (is_staff or (is_assigned and only_workflow_or_items)):
        return Response({"detail": "No tienes permiso para modificar esta orden."}, status=status.HTTP_403_FORBIDDEN)

    serializer = CuttingOrderSerializer(order, data=payload, partial=partial, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            data = serializer.validated_data
            target_status = data.get('workflow_status')

            if target_status == 'completed':
                updated = complete_order_processing(order.id, request.user)
            elif target_status == 'cancelled':
                updated = cancel_cutting_order(order.id, request.user)
            else:
                items = data.pop('items', None)
                updated = CuttingOrderRepository.update(
                    order_instance=order,
                    user_modifier=request.user,
                    data=data,
                    items=items
                )

            # Notificación de cambio de estado (decide destinatarios según new_status)
            send_cut_status_change_notification(
                actor_user_id=request.user.id,
                order_id=updated.id,
                new_status=updated.workflow_status,
                queue="notifications"
            )

            # Si es staff y NO fue ni completed ni cancelled → notificar al asignado "editada por admin"
            if request.user.is_staff and target_status not in ('completed', 'cancelled'):
                from apps.cuts.tasks import notify_cut_admin_edit
                notify_cut_admin_edit.apply_async(
                    kwargs={"actor_user_id": request.user.id, "order_id": updated.id},
                    queue="notifications"
                )

            # Invalidar caché tras update
            invalidate_cutting_order_cache()

            # Emitir evento global para refresco de dashboards
            send_cutting_order_status_global(order_id=updated.id, workflow_status=updated.workflow_status)

        resp = CuttingOrderSerializer(updated, context={'request': request})
        # Emitir evento WebSocket para notificar actualización
        broadcast_crud_event(
            event_type="update",
            app="cuts",
            model="CuttingOrder",
            data=resp.data,
        )
        return Response(resp.data)

    except Exception as e:
        logger.exception("Error actualizando orden %s", cuts_pk)
        detail = getattr(e, 'detail', str(e))
        code = (
            status.HTTP_400_BAD_REQUEST
            if isinstance(e, (serializers.ValidationError, ValidationError))
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        return Response({"detail": detail}, status=code)


@extend_schema(
    summary="Cancelar orden de corte",
    description="Cancela una orden (pending o in_process).",
    tags=["Cutting Orders"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def cutting_order_cancel(request, cuts_pk):
    try:
        order = cancel_cutting_order(cuts_pk, request.user)
        ser = CuttingOrderSerializer(order, context={'request': request})

        send_cut_status_change_notification(
            actor_user_id=request.user.id,
            order_id=order.id,
            new_status="cancelled",
            queue="notifications"
        )

        # Emitir evento global para refresco de dashboards
        send_cutting_order_status_global(order_id=order.id, workflow_status=order.workflow_status)

        # Emitir evento WebSocket para notificar cancelación (update)
        broadcast_crud_event(
            event_type="update",
            app="cuts",
            model="CuttingOrder",
            data=ser.data,
        )
        return Response(ser.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception("Error al cancelar orden %s", cuts_pk)
        detail = getattr(e, 'detail', str(e))
        code = (
            status.HTTP_400_BAD_REQUEST
            if isinstance(e, (serializers.ValidationError, ValidationError))
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        return Response({"detail": detail}, status=code)
