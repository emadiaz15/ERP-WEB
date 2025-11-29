from django.db import models

from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product


class CustomerProduct(BaseModel):
    """Customer-specific product description mapping legacy table ``articulos_clientes``.

    This model stores per-customer overrides for the product description or
    label. In the legacy system, this is the table ``articulos_clientes``:

    - artcli_codi  (PK)             → implicit ``id`` from ``BaseModel`` / Django
    - art_codi     (FK to articulo) → ``product`` FK
    - cli_codi     (FK to cliente)  → ``customer_legacy_id`` for now
    - artcli_desc  (varchar)        → ``description``

    At this stage we only keep a reference to the legacy customer integer
    (``customer_legacy_id``). When a proper ``Customer`` model exists we
    can migrate this field to a real ForeignKey.
    """

    # ------------------------------------------------------------------
    # Legacy: ``art_codi``
    # ------------------------------------------------------------------
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="customer_products",
        verbose_name="Producto",
        help_text="Producto asociado (art_codi).",
    )

    # ------------------------------------------------------------------
    # Legacy: ``cli_codi`` (referencia al cliente en el sistema viejo)
    # ------------------------------------------------------------------
    customer_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID legacy de cliente",
        help_text="Identificador de cliente en el sistema legacy (cli_codi).",
    )

    # ------------------------------------------------------------------
    # Legacy: ``artcli_desc``
    # ------------------------------------------------------------------
    description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Descripción para cliente",
        help_text="Descripción o etiqueta específica para el cliente (artcli_desc).",
    )

    class Meta:
        verbose_name = "Producto por cliente"
        verbose_name_plural = "Productos por cliente"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Readable representation including product and legacy customer id."""

        base = self.product.name if self.product else "Producto"
        return f"{base} @ cliente {self.customer_legacy_id or '-'}"
