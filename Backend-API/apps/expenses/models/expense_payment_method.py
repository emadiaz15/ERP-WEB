from django.db import models

from apps.products.models.base_model import BaseModel


class ExpensePaymentMethod(BaseModel):
    """Instrumentos de pago utilizados (legacy: ``pagosgas_pagos``)."""

    payment = models.ForeignKey(
        "expenses.ExpensePayment",
        on_delete=models.CASCADE,
        related_name="payment_methods",
        verbose_name="Pago",
    )
    payment_type_code = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Tipo de pago legacy",
        help_text="tippag_codi",
    )
    bank_code = models.IntegerField(null=True, blank=True, verbose_name="Banco legacy")
    branch_code = models.IntegerField(null=True, blank=True, verbose_name="Sucursal legacy")
    check_number = models.CharField(max_length=50, blank=True, verbose_name="Número de cheque")
    check_identifier = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Identificador cheque",
        help_text="cheqid",
    )
    document_number = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Nro documento",
        help_text="movtippag_nro",
    )
    document_piece = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Pieza",
        help_text="movtippag_pza",
    )
    due_date = models.DateField(null=True, blank=True, verbose_name="Vencimiento")
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Importe",
        help_text="movtippag_imp",
    )
    taxpayer_number = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="CUIT librador",
        help_text="cuit_lib",
    )
    receipt_payment_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID recibo/pago legacy",
        help_text="recpag_codi",
    )
    legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID legacy",
        help_text="pagpag_codi",
    )

    class Meta:
        verbose_name = "Instrumento de pago"
        verbose_name_plural = "Instrumentos de pago"

    def __str__(self) -> str:
        return f"Método {self.id or 'nuevo'}"
