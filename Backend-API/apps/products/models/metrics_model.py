from django.db import models
from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product


class ProductMetrics(BaseModel):
    """Métricas agregadas de comportamiento de un producto.

    Mapea la tabla ``art_metricas`` pero integrándose al modelo
    ``Product`` actual mediante FK. Pensado para procesos batch de
    análisis y scoring de compra.
    """

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="metrics",
        verbose_name="Producto",
    )

    # Ventas en ventanas de tiempo
    vend_6m = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Ventas 6 meses",
    )
    vend_3m = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Ventas 3 meses",
    )
    vend_prev_3m = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Ventas 3 meses previos",
    )
    tendencia_3m = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Tendencia 3 meses",
    )

    # Rotación / clasificación ABC
    rotation = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Rotación (1-5)",
    )
    rotation_pct = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Rotación %",
    )

    monthly_avg = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Promedio mensual 6m",
    )

    days_since_last_sale = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Días desde última venta",
    )

    # Situación de stock y compras
    stock_current = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Stock actual",
    )
    stock_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Stock mínimo",
    )
    position = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Posición proyectada",
    )
    purchased_pending = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Compras pendientes",
    )
    orders_pending = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Pedidos clientes pendientes",
    )
    purchased_3m = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Compras 3 meses",
    )
    purchased_6m = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Compras 6 meses",
    )

    purchase_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Score de compra",
    )

    calculated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de cálculo",
    )

    class Meta:
        verbose_name = "Métricas de Producto"
        verbose_name_plural = "Métricas de Productos"

    def __str__(self) -> str:
        return f"Métricas producto {self.product_id}"
