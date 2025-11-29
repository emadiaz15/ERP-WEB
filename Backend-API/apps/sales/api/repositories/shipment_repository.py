from django.db import models

from apps.sales.models import SalesShipment, SalesShipmentItem


class SalesShipmentRepository:
    """Acceso a datos para remitos."""

    @staticmethod
    def list_shipments(*, search: str | None = None, status: str | None = None) -> models.QuerySet:
        qs = SalesShipment.objects.select_related("order")
        if search:
            qs = qs.filter(reference__icontains=search)
        if status:
            qs = qs.filter(status_label=status)
        return qs.prefetch_related("items__product")

    @staticmethod
    def get_shipment(shipment_id: int) -> SalesShipment | None:
        return (
            SalesShipment.objects
            .select_related("order")
            .prefetch_related("items__product")
            .filter(pk=shipment_id)
            .first()
        )

    @staticmethod
    def create_shipment(**fields) -> SalesShipment:
        shipment = SalesShipment(**fields)
        shipment.save(user=fields.get("user"))
        return shipment

    @staticmethod
    def update_shipment(shipment: SalesShipment, *, user=None, **fields) -> SalesShipment:
        dirty = False
        for attr, value in fields.items():
            if value is not None and hasattr(shipment, attr) and getattr(shipment, attr) != value:
                setattr(shipment, attr, value)
                dirty = True
        if dirty:
            shipment.save(user=user)
        return shipment

    @staticmethod
    def soft_delete(shipment: SalesShipment, *, user=None) -> SalesShipment:
        shipment.delete(user=user)
        return shipment

    @staticmethod
    def add_item(shipment: SalesShipment, *, user=None, **fields) -> SalesShipmentItem:
        item = SalesShipmentItem(shipment=shipment, **fields)
        item.save(user=user)
        return item

    @staticmethod
    def list_items(shipment: SalesShipment) -> models.QuerySet:
        return shipment.items.select_related("product")
