"""Service for managing supplier product price history.

This service handles the creation and management of historical price records
for supplier products. It automatically tracks price changes and maintains
a complete audit trail of all price modifications over time.
"""

import logging
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.contrib.auth import get_user_model

from apps.products.models.supplier_product_model import SupplierProduct
from apps.products.models.supplier_product_price_history_model import SupplierProductPriceHistory

logger = logging.getLogger(__name__)
User = get_user_model()


class SupplierPriceHistoryService:
    """Service for handling supplier product price history operations."""

    @staticmethod
    @transaction.atomic
    def create_price_history_record(
        supplier_product: SupplierProduct,
        cost: Optional[Decimal] = None,
        sale_cost: Optional[Decimal] = None,
        currency: Optional[str] = None,
        exchange_rate_ref: Optional[Decimal] = None,
        changed_by: Optional[User] = None,
        notes: Optional[str] = None,
        valid_from: Optional[datetime] = None,
    ) -> SupplierProductPriceHistory:
        """Create a new price history record for a supplier product.

        Args:
            supplier_product: The SupplierProduct instance
            cost: Purchase cost (if None, uses current supplier_product.cost)
            sale_cost: Sale cost (if None, uses current supplier_product.sale_cost)
            currency: Currency code (if None, uses current supplier_product.currency)
            exchange_rate_ref: Exchange rate reference
            changed_by: User who made the change
            notes: Optional notes about the price change
            valid_from: Start date (if None, uses current timestamp)

        Returns:
            The created SupplierProductPriceHistory instance
        """
        # Cerrar el registro anterior (marcar valid_to)
        previous_records = SupplierProductPriceHistory.objects.filter(
            supplier_product=supplier_product,
            valid_to__isnull=True,
        )

        valid_from_date = valid_from or timezone.now()

        if previous_records.exists():
            previous_records.update(valid_to=valid_from_date)
            logger.info(
                f"Closed {previous_records.count()} previous price records for "
                f"SupplierProduct #{supplier_product.id}"
            )

        # Crear nuevo registro de histórico
        history_record = SupplierProductPriceHistory.objects.create(
            supplier_product=supplier_product,
            cost=cost if cost is not None else supplier_product.cost,
            sale_cost=sale_cost if sale_cost is not None else supplier_product.sale_cost,
            currency=currency if currency is not None else supplier_product.currency,
            exchange_rate_ref=exchange_rate_ref if exchange_rate_ref is not None else supplier_product.exchange_rate_ref,
            valid_from=valid_from_date,
            valid_to=None,  # Precio actual
            changed_by=changed_by,
            notes=notes,
        )

        logger.info(
            f"Created price history record #{history_record.id} for "
            f"SupplierProduct #{supplier_product.id} (cost: {history_record.cost})"
        )

        return history_record

    @staticmethod
    def get_current_price(supplier_product: SupplierProduct) -> Optional[SupplierProductPriceHistory]:
        """Get the current active price record for a supplier product.

        Args:
            supplier_product: The SupplierProduct instance

        Returns:
            The current active SupplierProductPriceHistory or None
        """
        return SupplierProductPriceHistory.objects.filter(
            supplier_product=supplier_product,
            valid_to__isnull=True,
        ).first()

    @staticmethod
    def get_price_history(
        supplier_product: SupplierProduct,
        limit: Optional[int] = None
    ) -> List[SupplierProductPriceHistory]:
        """Get all price history records for a supplier product.

        Args:
            supplier_product: The SupplierProduct instance
            limit: Optional limit on number of records to return

        Returns:
            List of SupplierProductPriceHistory ordered by valid_from descending
        """
        queryset = SupplierProductPriceHistory.objects.filter(
            supplier_product=supplier_product
        ).order_by("-valid_from")

        if limit:
            queryset = queryset[:limit]

        return list(queryset)

    @staticmethod
    def get_price_at_date(
        supplier_product: SupplierProduct,
        date: datetime
    ) -> Optional[SupplierProductPriceHistory]:
        """Get the price that was valid at a specific date.

        Args:
            supplier_product: The SupplierProduct instance
            date: The date to query

        Returns:
            The SupplierProductPriceHistory valid at that date or None
        """
        return SupplierProductPriceHistory.objects.filter(
            supplier_product=supplier_product,
            valid_from__lte=date,
        ).filter(
            Q(valid_to__gte=date) | Q(valid_to__isnull=True)
        ).first()

    @staticmethod
    def has_price_changed(
        supplier_product: SupplierProduct,
        new_cost: Optional[Decimal],
        new_sale_cost: Optional[Decimal]
    ) -> bool:
        """Check if the price has actually changed.

        Args:
            supplier_product: The SupplierProduct instance
            new_cost: New cost value
            new_sale_cost: New sale cost value

        Returns:
            True if either cost or sale_cost has changed
        """
        cost_changed = False
        sale_cost_changed = False

        if new_cost is not None:
            current_cost = supplier_product.cost or Decimal("0")
            cost_changed = current_cost != new_cost

        if new_sale_cost is not None:
            current_sale_cost = supplier_product.sale_cost or Decimal("0")
            sale_cost_changed = current_sale_cost != new_sale_cost

        return cost_changed or sale_cost_changed

    @staticmethod
    def calculate_price_change_percentage(
        old_price: Optional[Decimal],
        new_price: Optional[Decimal]
    ) -> Optional[Decimal]:
        """Calculate the percentage change between two prices.

        Args:
            old_price: Previous price
            new_price: New price

        Returns:
            Percentage change as Decimal, or None if calculation not possible
        """
        if old_price is None or new_price is None or old_price == 0:
            return None

        change = ((new_price - old_price) / old_price) * 100
        return change.quantize(Decimal("0.01"))
