from django.db import models

from apps.logistics.choices import ShipmentMode, ShipmentStatus


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pendiente"
    IN_PROCESS = "in_process", "En proceso"
    COMPLETED = "completed", "Completo"
    CANCELLED = "cancelled", "Cancelado"


class OrderPriority(models.TextChoices):
    LOW = "low", "Baja"
    NORMAL = "normal", "Normal"
    HIGH = "high", "Alta"
    CRITICAL = "critical", "Crítica"


class OrderOrigin(models.TextChoices):
    MANUAL = "manual", "Carga manual"
    IMPORT = "import", "Importado"
    ECOMMERCE = "ecommerce", "E-commerce"
    PORTAL = "portal", "Portal clientes"
    FORECAST = "forecast", "Forecast MRP"


class DiscountApplication(models.TextChoices):
    NONE = "none", "Sin descuento"
    PERCENTAGE = "percentage", "Porcentaje"
    AMOUNT = "amount", "Monto fijo"