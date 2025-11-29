from django.db import models

from apps.products.models.base_model import BaseModel


class PostalCode(BaseModel):
    """Postal code catalog mapping legacy table ``codipostales``.

    Legacy columns:
    - cp_codi (PK) → ``legacy_code``
    - cp_nro       → ``number``
    """

    number = models.CharField(
        max_length=10,
        verbose_name="Código postal",
        help_text="Número de código postal (cp_nro).",
    )
    legacy_code = models.IntegerField(
        unique=True,
        verbose_name="Código legacy",
        help_text="Identificador legacy del código postal (cp_codi).",
    )

    class Meta:
        verbose_name = "Código Postal"
        verbose_name_plural = "Códigos Postales"
        ordering = ["number"]
        indexes = [models.Index(fields=["legacy_code"])]

    def __str__(self) -> str:
        return self.number
