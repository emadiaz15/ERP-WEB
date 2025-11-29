from __future__ import annotations

from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from django.db import models, IntegrityError, transaction
from typing import Optional

from apps.products.models.subproduct_model import Subproduct
from apps.products.models.product_model import Product
from apps.stocks.models.stock_subproduct_model import SubproductStock


class StockSubproductRepository:
    """
    Repositorio para SubproductStock.
    La creación/ajuste que generen eventos deben hacerse en servicios.
    """

    # --- Lectura ---
    @staticmethod
    def get_by_stock_id(stock_id: int) -> Optional[SubproductStock]:
        try:
            return (
                SubproductStock.objects
                .select_related('subproduct', 'created_by', 'modified_by', 'deleted_by')
                .get(id=stock_id, status=True)
            )
        except SubproductStock.DoesNotExist:
            return None

    @staticmethod
    def get_all_active_stocks_for_subproduct(subproduct: Subproduct) -> models.QuerySet[SubproductStock]:
        if not isinstance(subproduct, Subproduct) or not subproduct.pk:
            return SubproductStock.objects.none()
        return (
            SubproductStock.objects
            .filter(subproduct=subproduct, status=True)
            .select_related('subproduct', 'created_by')
        )

    @staticmethod
    def get_all_active_stocks_for_product(parent_product: Product) -> models.QuerySet[SubproductStock]:
        if not isinstance(parent_product, Product) or not parent_product.pk:
            return SubproductStock.objects.none()
        return (
            SubproductStock.objects
            .filter(subproduct__parent=parent_product, status=True)
            .select_related('subproduct', 'created_by')
        )

    # --- Creación (sin evento) ---
    @staticmethod
    @transaction.atomic
    def create_stock(subproduct: Subproduct, quantity: Decimal | float, user) -> SubproductStock:
        """
        Crea SubproductStock básico. El evento inicial lo debe crear un servicio (initialize_subproduct_stock).
        """
        if not isinstance(subproduct, Subproduct) or subproduct.pk is None:
            raise ValidationError("Se requiere una instancia de Subproducto válida.")

        try:
            qty = Decimal(quantity)
            if qty < 0:
                raise ValidationError("La cantidad inicial no puede ser negativa.")
        except (InvalidOperation, TypeError):
            raise ValidationError("La cantidad inicial debe ser un número válido.")

        # Unique(subproduct): evita duplicados antes de la constraint
        if SubproductStock.objects.filter(subproduct=subproduct).exists():
            raise ValidationError(f"Ya existe stock para el subproducto '{subproduct.name}'. Use ajuste de stock.")

        try:
            stock = SubproductStock(subproduct=subproduct, quantity=qty)
            stock.save(user=user)
            return stock
        except IntegrityError:
            # Carrera con otra transacción creando el mismo registro
            raise ValidationError(f"Ya existe stock para el subproducto '{subproduct.name}'. Use ajuste de stock.")

    # --- Soft delete ---
    @staticmethod
    def soft_delete_stock(stock_instance: SubproductStock, user) -> SubproductStock:
        if not isinstance(stock_instance, SubproductStock):
            raise ValidationError("Se requiere una instancia de SubproductStock válida.")
        stock_instance.delete(user=user)
        return stock_instance
