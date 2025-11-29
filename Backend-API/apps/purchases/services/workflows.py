from apps.purchases.models import PurchaseOrder


def approve_purchase_order(order: PurchaseOrder, *, user=None) -> PurchaseOrder:
    """Placeholder para lógica de aprobación de órdenes."""

    if order.status_label == PurchaseOrder.Status.DRAFT:
        order.status_label = PurchaseOrder.Status.APPROVED
        order.save(user=user)
    return order
