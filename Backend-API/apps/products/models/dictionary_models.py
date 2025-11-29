from django.db import models
from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product


class ProductAbbreviation(BaseModel):
    """Abreviaciones conocidas para un artículo específico.

    Mapea la tabla legacy ``articulo_abreviaciones``.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="abbreviations",
        verbose_name="Producto",
    )
    abbreviation = models.CharField(
        max_length=50,
        verbose_name="Abreviación",
    )
    full_word = models.CharField(
        max_length=255,
        verbose_name="Palabra completa",
    )
    weight = models.IntegerField(
        default=1,
        verbose_name="Peso",
        help_text="Peso relativo de la abreviación (mayor = más relevante).",
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Notas",
    )

    class Meta:
        verbose_name = "Abreviación de Producto"
        verbose_name_plural = "Abreviaciones de Producto"
        indexes = [
            models.Index(fields=["abbreviation"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self) -> str:
        return f"{self.abbreviation} -> {self.full_word} (prod {self.product_id})"


class ProductSynonym(BaseModel):
    """Sinónimos o alias de un artículo.

    Mapea la tabla legacy ``articulo_sinonimos``.
    """

    class SynonymType(models.TextChoices):
        CUSTOMER = "cliente", "Cliente"
        INTERNAL = "interno", "Interno"
        TECHNICAL = "tecnico", "Técnico"

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="synonyms",
        verbose_name="Producto",
    )
    synonym = models.CharField(
        max_length=255,
        verbose_name="Sinónimo",
    )
    type = models.CharField(
        max_length=50,
        choices=SynonymType.choices,
        default=SynonymType.CUSTOMER,
        verbose_name="Tipo",
    )

    class Meta:
        verbose_name = "Sinónimo de Producto"
        verbose_name_plural = "Sinónimos de Producto"
        indexes = [
            models.Index(fields=["synonym"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self) -> str:
        return f"{self.synonym} ({self.type}) - prod {self.product_id}"


class TermDictionary(BaseModel):
    """Diccionario global de términos relacionados con artículos.

    Mapea la tabla legacy ``diccionario_terminos``.
    """

    term = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Término",
    )
    type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Tipo",
        help_text="material / medida / unidad / accion, etc.",
    )
    value = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Valor",
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Notas",
    )

    class Meta:
        verbose_name = "Término de Diccionario"
        verbose_name_plural = "Términos de Diccionario"

    def __str__(self) -> str:
        return self.term


class ProductAlias(BaseModel):
    """Alias de artículos utilizados por IA o usuarios.

    Mapea la tabla ``ia_alias_articulos``.
    """

    class SourceType(models.TextChoices):
        IA = "IA", "IA"
        CUSTOMER = "CLIENTE", "Cliente"
        SYSTEM = "SISTEMA", "Sistema"

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="aliases",
        verbose_name="Producto",
    )
    alias_text = models.CharField(
        max_length=255,
        verbose_name="Alias",
    )
    source = models.CharField(
        max_length=20,
        choices=SourceType.choices,
        default=SourceType.IA,
        verbose_name="Fuente",
    )
    client_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="ID cliente legacy",
    )
    region = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Región",
    )
    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100,
        verbose_name="Confianza",
    )
    created_by_source = models.CharField(
        max_length=50,
        default="IA",
        verbose_name="Creado por",
    )

    class Meta:
        verbose_name = "Alias de Producto"
        verbose_name_plural = "Alias de Productos"
        indexes = [
            models.Index(fields=["alias_text"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self) -> str:
        return f"{self.alias_text} -> prod {self.product_id} ({self.source})"
