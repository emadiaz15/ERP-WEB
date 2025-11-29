"""Integración básica con contabilidad/tesorería.

Por ahora despachamos un evento WebSocket para que los consumidores de
contabilidad puedan sincronizar los pagos. En el futuro se puede reemplazar
por una tarea Celery que llame a un ERP externo.
"""

import logging
from decimal import Decimal

from apps.core.utils import broadcast_crud_event

logger = logging.getLogger(__name__)


def sync_payment_with_accounting(payment, *, event="sync", source="expenses"):
    payload = {
        "id": payment.id,
        "person_legacy_id": payment.person_legacy_id,
        "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
        "currency": payment.currency,
        "total_amount": float(payment.total_amount or Decimal("0")),
        "retention_total_amount": float(payment.retention_total_amount or Decimal("0")),
    }
    broadcast_crud_event(event, source, "ExpensePaymentLedger", payload)
    logger.debug("[expenses][accounting] Evento de sync enviado para pago %s", payment.id)
