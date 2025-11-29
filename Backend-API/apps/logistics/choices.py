from django.db import models


class ShipmentMode(models.TextChoices):
    PICKUP = "pickup", "Retira cliente"
    OWN_FLEET = "own_fleet", "Flota propia"
    THIRD_PARTY = "third_party", "Transporte tercerizado"
    DROPSHIP = "dropship", "Dropshipping"
    COURIER = "courier", "Courier"


class ShipmentStatus(models.TextChoices):
    PENDING = "pending", "Pendiente"
    SCHEDULED = "scheduled", "Programado"
    PICKING = "picking", "En picking"
    PACKING = "packing", "En packing"
    IN_ROUTE = "in_route", "En ruta"
    DELIVERED = "delivered", "Entregado"
    RETURNED = "returned", "Devuelto"
    CANCELLED = "cancelled", "Cancelado"


class ShipmentDirection(models.TextChoices):
    INBOUND = "inbound", "Ingreso (compras)"
    OUTBOUND = "outbound", "Salida (ventas)"
    TRANSFER = "transfer", "Transferencia interna"
    THIRD_PARTY = "third_party", "Servicio externo"


class ServiceLevel(models.TextChoices):
    STANDARD = "standard", "Estándar"
    EXPRESS = "express", "Exprés"
    SAME_DAY = "same_day", "Mismo día"
    SCHEDULED = "scheduled", "Programado"


class CarrierAccountEntryType(models.TextChoices):
    DEBIT = "debit", "Débito"
    CREDIT = "credit", "Crédito"
    ADJUSTMENT = "adjustment", "Ajuste"


class ShipmentCostType(models.TextChoices):
    FREIGHT = "freight", "Flete"
    INSURANCE = "insurance", "Seguro"
    HANDLING = "handling", "Maniobras"
    TAX = "tax", "Impuestos"
    OTHER = "other", "Otros"
