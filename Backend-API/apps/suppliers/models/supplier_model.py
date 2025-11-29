from django.db import models

from apps.products.models.base_model import BaseModel


class Supplier(BaseModel):
    """Supplier master data aligned with legacy table ``proveedores``.

    Legacy mapping (main fields):
    - prov_codi   (PK lógico)       → ``id`` / external business code if needed
    - prov_nomb   (nombre)          → ``name``
    - prov_domi   (domicilio)       → ``address``
    - loca_codi   (FK localidad)    → stored as ``location_legacy_id`` for now
    - prov_cartel (nro cartel)      → ``sign_number`` (legacy billboard/ref)
    - prov_tel1   (teléfono 1)      → ``phone1``
    - prov_tel2   (teléfono 2)      → ``phone2``
    - prov_cel    (celular)         → ``mobile``
    - prov_cuit   (CUIT)            → ``tax_id``
    - prov_email  (email)           → ``email``
    - cond_codi   (cond. IVA)       → ``tax_condition_code`` (link to condiva)
    - percepcion  (percepciones)    → ``perception`` (raw flag/text)
    - dtoxpago    (dto por pago)    → ``discount_for_payment``
    - prov_saldo  (saldo)           → ``balance``
    - prov_afvor  (a favor)         → ``credit_balance``
    - prov_ultiletra (última letra) → ``last_invoice_letter``
    - prov_ultipto   (último pto)   → ``last_invoice_pos``
    - prov_deta   (detalle)         → ``notes``
    """

    name = models.CharField(
        max_length=255,
        verbose_name="Nombre",
        help_text="Nombre del proveedor (prov_nomb).",
    )
    address = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Domicilio",
        help_text="Dirección del proveedor (prov_domi).",
    )
    location_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID localidad legacy",
        help_text="Código de localidad heredado (loca_codi).",
    )
    sign_number = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Número de cartel",
        help_text="Número de cartel / referencia legacy (prov_cartel).",
    )
    phone1 = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Teléfono 1",
    )
    phone2 = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Teléfono 2",
    )
    mobile = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Celular",
    )
    tax_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="CUIT",
        help_text="CUIT del proveedor (prov_cuit).",
    )
    email = models.EmailField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Email",
    )
    tax_condition_code = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Condición IVA (código)",
        help_text="Código de condición de IVA (cond_codi → condiva).",
    )
    perception = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Percepción",
        help_text="Campo legacy de percepción (percepcion).",
    )
    discount_for_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Descuento por pago",
        help_text="Descuento por forma de pago (dtoxpago).",
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Saldo",
        help_text="Saldo actual del proveedor (prov_saldo).",
    )
    credit_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Saldo a favor",
        help_text="Saldo a favor del proveedor (prov_afvor).",
    )
    last_invoice_letter = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name="Última letra comprobante",
        help_text="Última letra de comprobante emitido (prov_ultiletra).",
    )
    last_invoice_pos = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Último punto de venta",
        help_text="Último punto de venta utilizado (prov_ultipto).",
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Notas",
        help_text="Detalle adicional del proveedor (prov_deta).",
    )

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["tax_id"]),
        ]

    def __str__(self) -> str:
        return self.name or f"Proveedor {self.pk}"
