from django.db import models
from django.conf import settings
from django.utils import timezone

from apps.products.models.base_model import BaseModel


class Notification(BaseModel):
    """
    Notificación simple dirigida a un usuario.
    Se almacena para históricos y para ‘popup’ en frontend.
    """
    TYPE_CHOICES = (
        ("cut_assigned", "Cutting order assigned"),
        ("cut_status", "Cutting order status update"),
        ("generic", "Generic"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    notif_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default="generic")
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True, default="")
    # Datos extra que el FE puede usar (IDs, rutas, etc.)
    payload = models.JSONField(null=True, blank=True)

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ("-created_at",)

    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at", "modified_at", "modified_by"])

    def __str__(self):
        return f"[{self.notif_type}] {self.title} -> {self.user_id}"
