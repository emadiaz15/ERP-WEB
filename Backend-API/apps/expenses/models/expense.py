from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.products.models.base_model import BaseModel


class Expense(BaseModel):
    """Cabecera de un gasto registrado en el ERP (legacy: ``gastos``)."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        APPROVED = "approved", "Aprobado"
        PAID = "paid", "Pagado"
        CANCELLED = "cancelled", "Anulado"

    expense_type = models.ForeignKey(
        "expenses.ExpenseType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
        verbose_name="Tipo de gasto",
    )
    person_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Persona legacy",
        help_text="Referencia a personas.per_codi.",
    )
    expense_date = models.DateField(verbose_name="Fecha del gasto")
    concept = models.CharField(max_length=255, blank=True, verbose_name="Concepto")
    notes = models.TextField(blank=True, verbose_name="Observaciones")
    currency = models.CharField(max_length=3, default="ARS", verbose_name="Moneda")
    exchange_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=1,
        verbose_name="Cotización",
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Descuento %",
    )
    due_date = models.DateField(null=True, blank=True, verbose_name="Fecha de vencimiento")
    point_of_sale = models.IntegerField(null=True, blank=True, verbose_name="Punto de venta")
    receipt_number = models.BigIntegerField(null=True, blank=True, verbose_name="Nro comprobante")
    receipt_type_code = models.CharField(
        max_length=5,
        blank=True,
        verbose_name="Tipo comprobante",
        help_text="Equivalente a gas_tipcbte / AFIP.",
    )
    receipt_reference = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Referencia externa",
        help_text="Combina gas_pto + gas_cbte si se requiere.",
    )
    withholding_number = models.IntegerField(null=True, blank=True, verbose_name="Nro de retención")
    iva_condition_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Condición IVA legacy",
        help_text="Referencia a condiva.cond_codi",
    )
    vat_perception_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Percepción IVA",
    )
    gross_income_perception_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Percepción IIBB",
    )
    amount_paid = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Importe pagado",
    )
    paid_flag = models.BooleanField(default=False, verbose_name="Pagado legacy")
    net_amount_primary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Neto 1",
        help_text="gas_impo",
    )
    net_amount_secondary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Neto 2",
        help_text="gas_impo2",
    )
    net_amount_third = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Neto 3",
        help_text="gas_impo3",
    )
    non_taxed_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Importe no gravado",
        help_text="gas_impng",
    )
    vat_amount_primary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="IVA 1",
        help_text="gas_iva",
    )
    vat_amount_secondary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="IVA 2",
        help_text="gas_iva2",
    )
    vat_amount_third = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="IVA 3",
        help_text="gas_iva3",
    )
    vat_debit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="IVA débito",
        help_text="ivand",
    )
    vat_credit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="IVA crédito",
        help_text="ivanc",
    )
    alternate_vat_rate_primary = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Alicuota alternativa 1",
        help_text="altiva_1",
    )
    alternate_vat_rate_secondary = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Alicuota alternativa 2",
        help_text="altiva_2",
    )
    discount_to_pay_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Descuento por pago",
        help_text="gas_dtopag",
    )
    cost_center_code = models.IntegerField(null=True, blank=True, verbose_name="Centro de costo")
    credit_note_reference = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Nota de crédito",
        help_text="gas_nc",
    )
    approval_notes = models.TextField(blank=True, verbose_name="Notas de aprobación")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Aprobado el")
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses_approved",
        verbose_name="Aprobado por",
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
        help_text="gas_codi",
    )

    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"
        ordering = ["-expense_date", "-id"]
        indexes = [
            models.Index(fields=["expense_date"]),
            models.Index(fields=["person_legacy_id"]),
            models.Index(fields=["legacy_id"]),
        ]

    def __str__(self) -> str:
        return f"Gasto {self.id or 'nuevo'}"

    def compute_total_amount(self) -> Decimal:
        components = [
            self.net_amount_primary or Decimal("0"),
            self.net_amount_secondary or Decimal("0"),
            self.net_amount_third or Decimal("0"),
            self.non_taxed_amount or Decimal("0"),
            self.vat_amount_primary or Decimal("0"),
            self.vat_amount_secondary or Decimal("0"),
            self.vat_amount_third or Decimal("0"),
            self.vat_perception_amount or Decimal("0"),
            self.gross_income_perception_amount or Decimal("0"),
        ]
        total = sum(components, Decimal("0")) - (self.discount_to_pay_amount or Decimal("0"))
        return total.quantize(Decimal("0.01"))

    def outstanding_amount(self) -> Decimal:
        total = self.compute_total_amount()
        paid = self.amount_paid or Decimal("0")
        remaining = total - paid
        return remaining if remaining > Decimal("0") else Decimal("0")

    def mark_as_paid_if_needed(self, *, user=None):
        if self.outstanding_amount() <= Decimal("0") and self.status_label != self.Status.PAID:
            self.status_label = self.Status.PAID
            self.save(user=user)
        elif self.status_label == self.Status.DRAFT:
            self.status_label = self.Status.APPROVED
            self.save(user=user)
