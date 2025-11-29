from django.db import models
from apps.products.models.base_model import BaseModel
from apps.products.models.category_model import Category

class Product(BaseModel):
    """Product catalog model aligned with legacy table ``articulos``.

    This model represents the master data of products (catalog).
    Stock quantities and movements are handled in the separate
    ``stocks`` app (``ProductStock`` and ``StockEvent``), mirroring
    the legacy tables ``histostock`` and related.

    The fields below follow, in order, the legacy columns from the
    ``articulos`` table, but use clear English names and modern
    Django types.
    """

    # ------------------------------------------------------------------
    # Legacy: ``art_codi`` (int, PK lógico del artículo)
    # In the new system we keep ``id`` as the real PK and use
    # ``code`` as the business identifier, unique and indexed.
    # ------------------------------------------------------------------
    code = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Código",
        help_text="Código heredado del sistema legacy (art_codi)."
    )

    # ------------------------------------------------------------------
    # Legacy: ``art_desc`` (varchar) → short/primary description
    # ------------------------------------------------------------------
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Nombre",
        help_text="Descripción corta del producto (art_desc)."
    )

    # ------------------------------------------------------------------
    # Legacy: ``art_precio`` (float) → selling price
    # ------------------------------------------------------------------
    price = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Precio de venta",
        help_text="Precio de venta sugerido (art_precio)."
    )

    # ------------------------------------------------------------------
    # Legacy: ``costo_ultcpra`` (float) → last purchase cost
    # ------------------------------------------------------------------
    last_purchase_cost = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Último costo de compra",
        help_text="Costo de la última compra registrada (costo_ultcpra)."
    )

    # ------------------------------------------------------------------
    # Legacy: ``art_med`` (varchar) → unit of measure
    # ------------------------------------------------------------------
    unit = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Unidad de medida",
        help_text="Unidad de medida principal del producto (art_med)."
    )

    # ------------------------------------------------------------------
    # Legacy: ``art_stmin`` (float) → minimum stock
    # IMPORTANT: current stock lives in ``ProductStock.quantity``.
    # ------------------------------------------------------------------
    min_stock = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Stock mínimo",
        help_text="Stock mínimo recomendado (art_stmin)."
    )

    # ------------------------------------------------------------------
    # Legacy: ``pedidos`` (float) → pending customer orders
    # Legacy: ``pedprov`` (float) → pending supplier orders
    # These are denormalized indicators; they can be recomputed from
    # orders, but are useful for compatibility and fast reporting.
    # ------------------------------------------------------------------
    pending_customer_orders = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Pedidos clientes pendientes",
        help_text="Cantidad pendiente de pedidos de clientes (pedidos)."
    )

    pending_supplier_orders = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Pedidos proveedores pendientes",
        help_text="Cantidad pendiente de pedidos a proveedores (pedprov)."
    )

    # ------------------------------------------------------------------
    # Legacy: ``art_deta`` (text) → internal / technical detail
    # Legacy: ``art_detaofi`` (text) → public / offer description
    # ------------------------------------------------------------------
    detail_internal = models.TextField(
        null=True,
        blank=True,
        verbose_name="Detalle interno",
        help_text="Detalle técnico interno (art_deta)."
    )

    detail_public = models.TextField(
        null=True,
        blank=True,
        verbose_name="Detalle público/oferta",
        help_text="Detalle visible para clientes (art_detaofi)."
    )

    # ------------------------------------------------------------------
    # Legacy: ``art_alicuota`` (int) → VAT condition / rate code
    # For now we store the raw code; later it can be linked to a
    # proper VAT model (e.g. table ``condiva`` / ``iva``).
    # ------------------------------------------------------------------
    vat_condition_code = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Código condición IVA",
        help_text="Código de alícuota IVA heredado (art_alicuota)."
    )

    # ------------------------------------------------------------------
    # Extra catalog fields that do not come directly from ``articulos``
    # but already existed in the new system and are useful for ERP.
    # ------------------------------------------------------------------
    brand = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Marca",
        help_text="Marca comercial del producto."
    )

    location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Ubicación",
        help_text="Ubicación física (depósito, pasillo, etc.)."
    )

    position = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Posición",
        help_text="Posición o referencia interna de ubicación."
    )

    # ------------------------------------------------------------------
    # Legacy: ``rub_codi`` → mapped to Category (rubros)
    # We use a FK to ``Category`` which already knows the legacy code.
    # ------------------------------------------------------------------
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,  # safer than CASCADE for catalog
        related_name='products',
        null=False,
        blank=False,
        verbose_name="Categoría",
        help_text="Categoría / rubro principal del producto."
    )

    # ------------------------------------------------------------------
    # Flag that indicates if stock is handled directly on this product
    # or derived from child ``Subproduct`` items.
    # ------------------------------------------------------------------
    has_subproducts = models.BooleanField(
        default=False,
        verbose_name="Tiene subproductos",
        help_text="Si es True, el stock real se deriva de subproductos."
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        # <— Aquí forzamos el orden descendente por fecha de creación
        ordering = ['-created_at']

    def __str__(self):
        """Human readable representation used in admin and logs."""

        name_display = self.name or "Producto sin nombre"
        code_display = self.code or "Sin código"
        return f"{name_display} ({code_display})"
