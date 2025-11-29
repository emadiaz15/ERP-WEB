from django.db import models

from apps.orders.choices import OrderStatus
from apps.products.models.base_model import BaseModel


class OrderStatusLog(BaseModel):
    """Audita cambios de estado y observaciones Operativas."""

    order = models.ForeignKey(
        "orders.CustomerOrder",
        on_delete=models.CASCADE,
        related_name="status_logs",
        verbose_name="Pedido",
    )
    previous_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        blank=True,
        verbose_name="Estado anterior",
    )
    new_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        verbose_name="Estado nuevo",
    )
    comment = models.CharField(max_length=255, blank=True, verbose_name="Comentario")
    actor = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Actor",
        help_text="Origen del cambio: usuario, integrador, servicio",
    )
    source = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Fuente",
        help_text="Microservicio o módulo que originó el cambio",
    )

    class Meta:
        verbose_name = "Log de estado de pedido"
        verbose_name_plural = "Logs de estados de pedido"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.order_id}: {self.previous_status}→{self.new_status}"
