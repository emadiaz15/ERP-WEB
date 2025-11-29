from django.db import models

from apps.delivery_notes.models.delivery_note import DeliveryNote
from apps.products.models.base_model import BaseModel


class DeliveryNoteTransport(BaseModel):
    """Información de transporte asociada a un remito."""

    delivery_note = models.ForeignKey(
        DeliveryNote,
        on_delete=models.CASCADE,
        related_name="transports",
        verbose_name="Remito",
    )
    carrier = models.ForeignKey(
        "logistics.Carrier",
        on_delete=models.SET_NULL,
        related_name="delivery_note_transports",
        null=True,
        blank=True,
        verbose_name="Transportista",
    )
    carrier_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Transporte legacy",
        help_text="Código legacy del transportista (tran_codi).",
    )
    freight_charge = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Cargo de flete",
        help_text="Responsable del flete (flete_cargo).",
    )
    delivery_place = models.TextField(
        blank=True,
        verbose_name="Lugar de entrega",
        help_text="Lugar detallado para la entrega (flete_lugent).",
    )

    class Meta:
        verbose_name = "Transporte de remito"
        verbose_name_plural = "Transportes de remito"

    def __str__(self) -> str:
        return f"Transporte remito {self.delivery_note_id}"
