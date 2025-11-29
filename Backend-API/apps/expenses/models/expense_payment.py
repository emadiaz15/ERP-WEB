from django.db import models

from apps.products.models.base_model import BaseModel


class ExpensePayment(BaseModel):
    """Pagos y aplicaciones contra gastos (legacy: ``pagosgas``)."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        CONFIRMED = "confirmed", "Confirmado"
        APPLIED = "applied", "Aplicado"
        CANCELLED = "cancelled", "Anulado"

    payment_date = models.DateField(verbose_name="Fecha de pago")
    person_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Persona legacy",
        help_text="per_codi",
    )
    currency = models.CharField(max_length=3, default="ARS", verbose_name="Moneda")
    exchange_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=1,
        verbose_name="Cotización",
    )
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Importe total",
        help_text="pagg_impo",
    )
    retention_subject_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Base sujeta a retención",
        help_text="pagg_sujret",
    )
    observations = models.TextField(blank=True, verbose_name="Observaciones")
    advance_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Anticipo",
        help_text="pagg_antic",
    )
    discount_saf_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Descuento SAF",
        help_text="pagg_dtosaf",
    )
    discount_for_payment_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Dto por pago",
        help_text="pagg_dtoxpag",
    )
    retention_balance_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Saldo retenciones",
        help_text="pagg_restsaf",
    )
    retention_total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Total retenciones",
        help_text="pagg_totsaf",
    )
    status_label = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Estado",
    )
    legacy_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID legacy",
        help_text="pagg_codi",
    )

    class Meta:
        verbose_name = "Pago de gasto"
        verbose_name_plural = "Pagos de gastos"
        ordering = ["-payment_date", "-id"]
        indexes = [
            models.Index(fields=["payment_date"]),
            models.Index(fields=["person_legacy_id"]),
        ]

    def __str__(self) -> str:
        return f"Pago gasto {self.id or 'nuevo'}"
