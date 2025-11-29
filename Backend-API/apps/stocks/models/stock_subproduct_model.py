# apps/stocks/models/stock_subproduct_model.py
from decimal import Decimal
from django.db import models
from django.db.models import Q
from apps.products.models.base_model import BaseModel
from apps.products.models.subproduct_model import Subproduct

class SubproductStock(BaseModel):
    """Stock para un Subproducto específico (1 registro por subproducto)."""
    # Si quieres hacerlo literalmente 1‑a‑1, puedes usar OneToOneField; dejo FK+constraint porque ya lo tenías.
    subproduct = models.ForeignKey(
        Subproduct,
        on_delete=models.CASCADE,
        related_name='stock_records',
        verbose_name="Subproducto",
    )
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Cantidad Actual",
    )

    class Meta:
        verbose_name = "Stock de Subproducto"
        verbose_name_plural = "Stocks de Subproductos"
        constraints = [
            models.UniqueConstraint(
                fields=['subproduct'],
                name='uniq_subproduct_stock_only_one_record',
            ),
            models.CheckConstraint(
                check=Q(quantity__gte=0),
                name='subproductstock_quantity_non_negative',
            ),
        ]
        indexes = [
            models.Index(fields=['subproduct', 'status']),
        ]

    def __str__(self):
        subproduct_name = getattr(self.subproduct, 'name', f'ID:{self.subproduct_id}')
        return f"Stock de {subproduct_name}: {self.quantity}"

    # Helper para saber si está disponible
    @property
    def is_available(self) -> bool:
        try:
            return self.quantity > 0
        except Exception:
            return False
