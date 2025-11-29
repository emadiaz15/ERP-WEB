from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.products.models.base_model import BaseModel
from apps.suppliers.models import Supplier
from apps.payables.choices import RetentionType


class RetentionCertificate(BaseModel):
    """Certificados de retención aplicados a pagos o facturas."""

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="retention_certificates",
        verbose_name="Proveedor",
    )
    retention_type = models.CharField(
        max_length=20,
        choices=RetentionType.choices,
        default=RetentionType.VAT,
    )
    certificate_number = models.CharField(max_length=60, blank=True)
    retention_date = models.DateField(null=True, blank=True)
    base_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    retention_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    jurisdiction = models.CharField(max_length=120, blank=True)
    tax_id = models.CharField(max_length=20, blank=True)

    document_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    document_object_id = models.PositiveIntegerField(null=True, blank=True)
    document = GenericForeignKey("document_content_type", "document_object_id")

    payment_order = models.ForeignKey(
        "payables.PaymentOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="retentions",
    )
    observations = models.TextField(blank=True)
    legacy_id = models.IntegerField(null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = "Retención"
        verbose_name_plural = "Retenciones"
        indexes = [models.Index(fields=["retention_type", "retention_date"])]
