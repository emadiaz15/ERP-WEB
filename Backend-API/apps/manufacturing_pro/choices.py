from django.db import models


class ManufacturingOrderStatus(models.TextChoices):
    PLANNED = "planned", "Planificada"
    IN_PROGRESS = "in_progress", "En proceso"
    ON_HOLD = "on_hold", "En pausa"
    QUALITY = "quality", "Control calidad"
    COMPLETED = "completed", "Completada"
    CANCELLED = "cancelled", "Cancelada"


class ManufacturingPriority(models.TextChoices):
    LOW = "low", "Baja"
    NORMAL = "normal", "Normal"
    HIGH = "high", "Alta"
    CRITICAL = "critical", "Crítica"


class OperationStatus(models.TextChoices):
    PENDING = "pending", "Pendiente"
    RUNNING = "running", "Ejecutando"
    FINISHED = "finished", "Finalizada"
    BLOCKED = "blocked", "Bloqueada"


class ExternalProcessType(models.TextChoices):
    GALVANIZED = "galvanized", "Galvanizado"
    PAINT = "paint", "Pintura"
    ZINC = "zinc", "Zincado"
    OTHER = "other", "Otro"


class ExternalProcessStatus(models.TextChoices):
    PLANNED = "planned", "Planificado"
    SENT = "sent", "Enviado"
    PARTIAL = "partial", "Recepción parcial"
    RECEIVED = "received", "Finalizado"
    CANCELLED = "cancelled", "Cancelado"


class MovementType(models.TextChoices):
    ISSUE = "issue", "Salida"
    RETURN = "return", "Devolución"
    CONSUMPTION = "consumption", "Consumo"
    ADJUSTMENT = "adjustment", "Ajuste"


class SupplyUnit(models.TextChoices):
    UNIT = "un", "Unidad"
    KILO = "kg", "Kilogramo"
    GRAM = "gr", "Gramo"
    LITER = "lt", "Litro"
    METER = "mt", "Metro"
    OTHER = "other", "Otro"
