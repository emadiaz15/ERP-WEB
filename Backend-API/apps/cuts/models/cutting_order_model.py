from decimal import Decimal  # ⬅️ para manejar decimales de forma precisa

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction

from apps.products.models.base_model import BaseModel
from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct
from apps.orders.choices import OrderStatus


class CuttingOrder(BaseModel):
    """Orden de corte ligada directamente a un pedido de clientes."""

    WORKFLOW_STATUS_CHOICES = OrderStatus.choices

    order = models.ForeignKey(
        "orders.CustomerOrder",
        on_delete=models.PROTECT,
        related_name="cutting_orders",
        verbose_name="Pedido",
    )

    order_number = models.PositiveIntegerField(
        verbose_name='Número de Pedido',
        help_text='Número de pedido manual, entero único',
        unique=True,                       # Debe ser único
        validators=[MinValueValidator(1)], # No permite 0 ni negativos
        db_index=True                      # Index para búsquedas
    )

    order_line = models.ForeignKey(
        "orders.CustomerOrderLine",
        on_delete=models.PROTECT,
        related_name="cutting_orders",
        null=True,
        blank=True,
        verbose_name="Detalle de pedido",
        help_text="Permite vincular la orden de corte a un ítem específico del pedido",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,          # No se puede borrar el producto si hay ordenes
        related_name='cutting_orders',
        verbose_name='Producto'
    )

    # ✅ DEFAULT para evitar prompt interactivo en migración inicial
    #    Permitimos 0.00 como punto de partida en datos existentes.
    quantity_to_cut = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name='Cantidad a Cortar',
        help_text='Objetivo total a cortar para esta orden (se sincroniza con el pedido)'
    )

    customer = models.CharField(
        max_length=255,
        help_text='Cliente para quien es la orden de corte (snapshot del pedido)',
        verbose_name='Cliente'
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='cutting_orders_assigned',
        on_delete=models.SET_NULL,         # Si el usuario se borra, mantenemos la orden
        null=True, blank=True,
        verbose_name='Asignado A'
    )

    completed_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Fecha de Completado'
    )  # Se setea cuando se marca como completed.

    operator_can_edit_items = models.BooleanField(
        default=False,
        verbose_name='Operario puede editar items',
        help_text='Si está activo, se permite crear la orden sin ítems y que el operario los defina en el Paso 2.'
    )

    class Meta:
        verbose_name = 'Orden de Corte'
        verbose_name_plural = 'Órdenes de Corte'
        permissions = [
            ('can_assign_cutting_order', 'Can assign cutting orders'),
            ('can_process_cutting_order', 'Can process cutting orders'),
        ]

    def __str__(self):
        return f'Orden de corte #{self.pk} para pedido {self.order_number}'

    @property
    def workflow_status(self) -> str | None:
        """Proxy del estado del pedido asociado."""
        return self.order.status if self.order_id else None

    def get_workflow_status_display(self) -> str:
        """Mantiene compatibilidad con templates/admin."""
        if self.order_id:
            return self.order.get_status_display()
        return ""

    def set_workflow_status(self, new_status: str, *, user=None, save: bool = True) -> None:
        """Actualiza el estado del pedido asociado y opcionalmente persiste."""
        if not self.order_id:
            raise ValidationError("No se puede actualizar el estado sin un pedido asociado.")
        if new_status not in dict(self.WORKFLOW_STATUS_CHOICES):
            raise ValidationError({"status": "Estado de pedido inválido."})
        if self.order.status == new_status:
            return
        self.order.status = new_status
        if save:
            update_fields = ["status", "modified_at"]
            if user:
                update_fields.append("modified_by")
            self.order.save(user=user, update_fields=update_fields)

    @property
    def assigned_by(self):
        """Quién creó la orden es quien 'asignó'."""
        return self.created_by

    @property
    def total_selected_quantity(self) -> Decimal:
        """Suma de cantidades de todos los ítems seleccionados."""
        total = Decimal("0")
        for it in self.items.all():
            total += (it.cutting_quantity or Decimal("0"))
        return total

    def clean(self):
        """
        Validaciones:
        - Si NO se permite edición por operario, debe venir al menos 1 ítem.
        - Cada ítem > 0.
        - Subproductos deben pertenecer al 'product' de la orden.
        - La suma de ítems NO puede exceder 'quantity_to_cut'.
        """
        super().clean()

        if not self.operator_can_edit_items and not self.items.exists():
            raise ValidationError('Debe incluir al menos un item de corte.')

        if self.order_line and self.order_line.order_id != self.order_id:
            raise ValidationError({'order_line': 'La línea seleccionada no pertenece al pedido indicado.'})

        if self.order_line and self.order_line.product_id != self.product_id:
            raise ValidationError({'product': 'El producto del detalle debe coincidir con el producto de la orden de corte.'})

        for item in self.items.all():
            if item.cutting_quantity is None or item.cutting_quantity <= 0:
                raise ValidationError({'items': f"Cantidad inválida para {item.subproduct}."})
            if item.subproduct.parent_id != self.product_id:
                raise ValidationError({'items': f"El subproducto {item.subproduct_id} no pertenece al producto seleccionado."})

        total = self.total_selected_quantity
        target = self.quantity_to_cut or Decimal("0")
        if total > target:
            raise ValidationError({
                'items': f"La suma de cantidades ({total}) excede la cantidad a cortar ({target})."
            })

    @transaction.atomic
    def complete_cutting(self, user_completing):
        """Marca la orden como completada (lógica delegada al servicio)."""
        from apps.cuts.services.cuts_services import complete_cutting_logic
        return complete_cutting_logic(self, user_completing)

    def sync_from_order(self):
        """Actualiza campos derivados desde el pedido y su línea asociada."""
        if self.order:
            candidate_number = self.order.legacy_id or self.order.pk
            if candidate_number:
                self.order_number = candidate_number

            customer_name = self.order.customer_snapshot_name
            if not customer_name and self.order.customer:
                customer_name = self.order.customer.name
            if customer_name:
                self.customer = customer_name

        if self.order_line:
            if self.order_line.quantity_ordered is not None:
                self.quantity_to_cut = self.order_line.quantity_ordered
            if self.order_line.product_id and self.product_id != self.order_line.product_id:
                self.product_id = self.order_line.product_id

    def save(self, *args, **kwargs):
        self.sync_from_order()
        super().save(*args, **kwargs)


class CuttingOrderItem(models.Model):
    """
    Ítem de la orden de corte: un subproducto y su cantidad a cortar.
    """
    order = models.ForeignKey(
        CuttingOrder,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name="Orden de Corte"
    )
    subproduct = models.ForeignKey(
        Subproduct,
        on_delete=models.PROTECT,
        verbose_name="Subproducto"
    )
    cutting_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],  # cada ÍTEM sí exige > 0
        help_text="Cantidad a cortar de este subproducto",
        verbose_name="Cantidad a Cortar (ítem)"
    )

    class Meta:
        verbose_name = "Item de Orden de Corte"
        verbose_name_plural = "Items de Orden de Corte"
        constraints = [
            models.UniqueConstraint(
                fields=["order", "subproduct"],
                name="unique_item_per_order_subproduct"
            )
        ]

    def __str__(self):
        return f"{self.subproduct} → {self.cutting_quantity}"
