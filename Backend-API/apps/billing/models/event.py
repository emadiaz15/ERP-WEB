from django.db import models

from apps.products.models.base_model import BaseModel


class BillingEvent(BaseModel):
    billing_document = models.ForeignKey(
        "billing.BillingDocument",
        on_delete=models.CASCADE,
        related_name="events",
    )
    previous_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20)
    actor = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billing_events",
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Evento de facturación"
        verbose_name_plural = "Eventos de facturación"
