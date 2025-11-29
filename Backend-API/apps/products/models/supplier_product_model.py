from django.db import models

from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product


class SupplierProduct(BaseModel):
    """Supplier-specific product information mapping legacy ``articulos_proveedores``.

    Legacy table columns:

    - artpro_codi  (PK)             → implicit ``id`` from ``BaseModel`` / Django
    - art_codi     (FK articulo)    → ``product`` FK
    - prov_codi    (FK proveedor)   → ``supplier_legacy_id`` (for now)
    - artpro_costo (float)          → ``cost``
    - artpro_ctovta (float)         → ``sale_cost``
    - artpro_desc  (varchar)        → ``description``
    - moneda       (varchar)        → ``currency``
    - lista        (int)            → ``price_list_number``
    - otro         (int)            → ``other_flag``
    - cotiz        (int)            → ``exchange_rate_ref``

    When a full Supplier model exists this class can be extended to use
    a ForeignKey instead of the raw integer ``supplier_legacy_id``.
    """

    # ------------------------------------------------------------------
    # Legacy: ``art_codi``
    # ------------------------------------------------------------------
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="supplier_products",
        verbose_name="Producto",
        help_text="Producto asociado (art_codi).",
    )

    # ------------------------------------------------------------------
    # Legacy: ``prov_codi`` (referencia al proveedor en el sistema viejo)
    # ------------------------------------------------------------------
    supplier_legacy_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID legacy de proveedor",
        help_text="Identificador de proveedor en el sistema legacy (prov_codi).",
    )

    # ------------------------------------------------------------------
    # Legacy: ``artpro_costo`` y ``artpro_ctovta``
    # ------------------------------------------------------------------
    cost = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Costo de proveedor",
        help_text="Costo de compra informado por el proveedor (artpro_costo).",
    )

    sale_cost = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Costo de venta",
        help_text="Costo de referencia para venta (artpro_ctovta).",
    )

    # ------------------------------------------------------------------
    # Legacy: ``artpro_desc``
    # ------------------------------------------------------------------
    description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Descripción de proveedor",
        help_text="Nombre o descripción tal como la maneja el proveedor (artpro_desc).",
    )

    # ------------------------------------------------------------------
    # Legacy: ``moneda``, ``lista``, ``otro``, ``cotiz``
    # ------------------------------------------------------------------
    currency = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        verbose_name="Moneda",
        help_text="Código de moneda (por ejemplo P/D) (moneda).",
    )

    price_list_number = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Número de lista",
        help_text="Número de lista de precios del proveedor (lista).",
    )

    other_flag = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Otro flag",
        help_text="Campo genérico heredado del legacy (otro).",
    )

    exchange_rate_ref = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Referencia cotización",
        help_text="Referencia a una cotización (cotiz).",
    )

    class Meta:
        verbose_name = "Producto por proveedor"
        verbose_name_plural = "Productos por proveedor"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Readable representation including product and supplier legacy id."""

        base = self.product.name if self.product else "Producto"
        return f"{base} @ proveedor {self.supplier_legacy_id or '-'}"
