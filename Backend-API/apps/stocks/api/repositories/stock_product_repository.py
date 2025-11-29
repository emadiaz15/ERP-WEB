from __future__ import annotations

from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from apps.products.models.product_model import Product
from apps.stocks.models.stock_product_model import ProductStock
import logging

logger = logging.getLogger(__name__)


class StockProductRepository:
    """
    Repositorio para ProductStock (stock de productos sin subproductos).
    Delega auditoría a BaseModel.save(user=...).
    La lógica de negocio (ajustes + StockEvent) debe vivir en los servicios.
    """

    # --- Lectura ---
    @staticmethod
    def get_by_stock_id(stock_id: int) -> ProductStock | None:
        try:
            return (
                ProductStock.objects
                .select_related('product', 'created_by', 'modified_by', 'deleted_by')
                .get(id=stock_id, status=True)
            )
        except ProductStock.DoesNotExist:
            return None

    @staticmethod
    def get_stock_for_product(product: Product) -> ProductStock | None:
        if not isinstance(product, Product) or not product.pk:
            return None
        try:
            # OneToOne + status
            return (
                ProductStock.objects
                .select_related('product', 'created_by', 'modified_by', 'deleted_by')
                .get(product=product, status=True)
            )
        except ProductStock.DoesNotExist:
            return None
        except ProductStock.MultipleObjectsReturned:
            logger.warning(
                "ALERTA: Múltiples ProductStock activos para Producto ID %s", product.pk
            )
            return (
                ProductStock.objects
                .filter(product=product, status=True)
                .select_related('product')
                .first()
            )

    @staticmethod
    def get_all_active():
        return (
            ProductStock.objects
            .filter(status=True)
            .select_related('product', 'created_by')
        )

    # --- Creación (sin evento) ---
    @staticmethod
    @transaction.atomic
    def create_stock(product: Product, quantity: Decimal | float, user) -> ProductStock:
        """
        Crea ProductStock básico. El evento inicial (si corresponde) lo debe crear un servicio.
        """
        if not isinstance(product, Product) or product.pk is None:
            raise ValidationError("Se requiere una instancia de Producto válida.")

        # Regla de negocio: NO crear stock si el producto tiene subproductos
        if getattr(product, "has_subproducts", False):
            raise ValidationError("No se puede crear ProductStock para un producto con subproductos.")

        try:
            qty = Decimal(quantity)
            if qty < 0:
                raise ValidationError("La cantidad inicial no puede ser negativa.")
        except (InvalidOperation, TypeError):
            raise ValidationError("La cantidad inicial debe ser un número válido.")

        # Chequeo amistoso antes de caer en la OneToOne
        if ProductStock.objects.filter(product=product).exists():
            raise ValidationError(f"Ya existe un registro de stock para el producto '{product.name}'.")

        try:
            stock = ProductStock(product=product, quantity=qty)
            stock.save(user=user)  # BaseModel: audita created_by/created_at
            return stock
        except IntegrityError:
            # Carrera con otra transacción creando el mismo registro
            raise ValidationError(f"Ya existe un registro de stock para el producto '{product.name}'.")

    # --- Soft delete ---
    @staticmethod
    def soft_delete_stock(stock_instance: ProductStock, user) -> ProductStock:
        if not isinstance(stock_instance, ProductStock):
            raise ValidationError("Se requiere una instancia de ProductStock válida.")
        stock_instance.delete(user=user)
        return stock_instance
