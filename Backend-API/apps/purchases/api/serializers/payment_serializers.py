from rest_framework import serializers

from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.purchases.models import PurchasePayment, PurchasePaymentAllocation


class PurchasePaymentAllocationSerializer(BaseSerializer):
    receipt_number = serializers.CharField(source="receipt.id", read_only=True)

    class Meta:
        model = PurchasePaymentAllocation
        fields = [
            "id",
            "payment",
            "receipt",
            "receipt_number",
            "allocated_amount",
            "is_partial",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = [
            "status",
            "created_at",
            "modified_at",
        ]


class PurchasePaymentSerializer(BaseSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    allocations = PurchasePaymentAllocationSerializer(many=True, read_only=True)

    class Meta:
        model = PurchasePayment
        fields = [
            "id",
            "supplier",
            "supplier_name",
            "payment_date",
            "amount",
            "currency",
            "exchange_rate",
            "reference",
            "notes",
            "legacy_id",
            "allocations",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = [
            "status",
            "created_at",
            "modified_at",
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("El importe debe ser positivo.")
        return value
