from django.db import models

from apps.products.models.base_model import BaseModel


class BillingAttachment(BaseModel):
    billing_document = models.ForeignKey(
        "billing.BillingDocument",
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    filename = models.CharField(max_length=255)
    file_url = models.URLField()
    content_type = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Adjunto de facturación"
        verbose_name_plural = "Adjuntos de facturación"
