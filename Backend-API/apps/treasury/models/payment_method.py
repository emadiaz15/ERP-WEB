from django.db import models

from apps.products.models.base_model import BaseModel


class PaymentMethod(BaseModel):
    """Catálogo de medios de pago (``tipospago``)."""

    legacy_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID legacy",
        help_text="Identificador legado (tippag_codi).",
    )
    name = models.CharField(
        max_length=120,
        verbose_name="Descripción",
        help_text="Nombre del medio de pago (tippag_desc).",
    )
    requires_bank = models.BooleanField(
        default=False,
        verbose_name="Requiere banco",
    )
    requires_reference = models.BooleanField(
        default=False,
        verbose_name="Requiere referencia",
    )
    is_cash = models.BooleanField(
        default=False,
        verbose_name="Es efectivo",
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Notas",
    )

    class Meta:
        verbose_name = "Medio de pago"
        verbose_name_plural = "Medios de pago"
        ordering = ["name"]
        indexes = [models.Index(fields=["legacy_id"]), models.Index(fields=["name"])]

    def __str__(self) -> str:
        return self.name
