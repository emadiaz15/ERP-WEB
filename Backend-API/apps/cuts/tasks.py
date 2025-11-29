# apps/cuts/tasks.py
from celery import shared_task
from django.contrib.auth import get_user_model
from apps.notifications.services.notification_service import create_notification

User = get_user_model()

# Mapeo de estados a español (coherente con tu modelo)
STATUS_ES = {
    "pending": "Pendiente",
    "in_process": "En Proceso",
    "completed": "Completada",
    "cancelled": "Cancelada",
}

def _status_es(s: str) -> str:
    return STATUS_ES.get(s, s)

def _order_url_path(order_id: int) -> str:
    # Ajusta si tu frontend usa otra ruta
    return f"/cuts/orders/{order_id}"

def _order_payload(order, actor):
    product = getattr(order, "product", None)
    assigned = getattr(order, "assigned_to", None)
    creator = getattr(order, "created_by", None)
    return {
        "order_id": order.id,
        "order_number": order.order_number,
        "customer": order.customer,
        "product_id": getattr(product, "id", None),
        "product_name": getattr(product, "name", str(product) if product else None),
        "quantity_to_cut": str(getattr(order, "quantity_to_cut", "")),
        "status": order.workflow_status,
        "status_display": _status_es(order.workflow_status),
        "assigned_to_id": getattr(assigned, "id", None),
        "assigned_to_username": getattr(assigned, "username", None),
        "created_by_id": getattr(creator, "id", None),
        "created_by_username": getattr(creator, "username", None),
        "actor_id": getattr(actor, "id", None) if actor else None,
        "actor_username": getattr(actor, "username", None) if actor else None,
        "url_path": _order_url_path(order.id),
    }

@shared_task
def notify_cut_assignment(user_id: int, order_id: int):
    """
    Notifica SOLO al usuario asignado la nueva asignación.
    """
    try:
        user = User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist:
        return

    from apps.cuts.api.repositories.cutting_order_repository import CuttingOrderRepository
    order = CuttingOrderRepository.get_by_id(order_id)
    if not order:
        return
    if not order.assigned_to_id or order.assigned_to_id != user.id:
        return

    # Formato pedido: "NUEVA ORDEN DE CORTE ASIGNADA {PEDIDO N°} - {CLIENTE}"
    title = f"NUEVA ORDEN DE CORTE ASIGNADA - Pedido N° {order.order_number} - {order.customer}"
    message = (
        f"Te asignaron una order de corte - Pedido N° {order.order_number} del producto "
        f"{getattr(order.product, 'name', str(order.product))} para {order.customer}. "
        f"Objetivo: {order.quantity_to_cut}."
    )
    payload = _order_payload(order, actor=order.created_by)

    create_notification(
        user=user,
        notif_type="cut_assigned",
        title=title,
        message=message,
        payload=payload,
        actor=order.created_by,
    )

@shared_task
def notify_cut_status_change(actor_user_id: int, order_id: int, new_status: str):
    """
    Reglas:
      - Si new_status == 'completed'  → notificar SOLO a admins (is_staff=True).
      - Si new_status == 'cancelled'  → notificar SOLO al usuario asignado.
      - Otros estados                 → no notificar.
    """
    try:
        actor = User.objects.get(pk=actor_user_id, is_active=True)
    except User.DoesNotExist:
        actor = None

    from apps.cuts.api.repositories.cutting_order_repository import CuttingOrderRepository
    order = CuttingOrderRepository.get_by_id(order_id)
    if not order:
        return

    # --- COMPLETED → admins ---
    if new_status == "completed":
        admins = User.objects.filter(is_active=True, is_staff=True)
        if not admins.exists():
            return

        title = f"Order de corte - Pedido N° {order.order_number} completada"
        message = (
            f"La orden de corte del Pedido N° {order.order_number} fue completada. "
            f"Producto: {getattr(order.product, 'name', str(order.product))}. "
            f"Cliente: {order.customer}. "
            f"Objetivo: {order.quantity_to_cut}."
        )
        payload = _order_payload(order, actor=actor)

        for admin in admins:
            create_notification(
                user=admin,
                notif_type="cut_status",
                title=title,
                message=message,
                payload=payload,
                actor=actor,
            )
        return

    # --- CANCELLED → asignado ---
    if new_status == "cancelled":
        if not order.assigned_to_id:
            return

        title = f"Orden de corte - Pedido N° {order.order_number} cancelada"
        message = (
            f"La orden de corte - Pedido N° {order.order_number} fue cancelada. "
            f"Producto: {getattr(order.product, 'name', str(order.product))}. "
            f"Cliente: {order.customer}."
        )
        payload = _order_payload(order, actor=actor)

        create_notification(
            user=order.assigned_to,
            notif_type="cut_status",
            title=title,
            message=message,
            payload=payload,
            actor=actor,
        )
        return

    # Otros estados → no notificar
    return

@shared_task
def notify_cut_admin_edit(actor_user_id: int, order_id: int):
    """
    Notifica al usuario asignado que un admin editó la orden (sin completarla/cancelarla).
    """
    try:
        actor = User.objects.get(pk=actor_user_id, is_active=True)
    except User.DoesNotExist:
        actor = None

    from apps.cuts.api.repositories.cutting_order_repository import CuttingOrderRepository
    order = CuttingOrderRepository.get_by_id(order_id)
    if not order or not order.assigned_to_id:
        return

    title = f"Orden de corte - Pedido N° {order.order_number} actualizada por admin"
    message = (
        f"Un administrador actualizó la orden de corte - Pedido N° {order.order_number} "
        f"del cliente {order.customer}."
    )
    payload = _order_payload(order, actor=actor)

    create_notification(
        user=order.assigned_to,
        notif_type="cut_status",
        title=title,
        message=message,
        payload=payload,
        actor=actor,
    )
