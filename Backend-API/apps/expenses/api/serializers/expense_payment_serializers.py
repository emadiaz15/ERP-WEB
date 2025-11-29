from rest_framework import serializers

from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.expenses.models import (
    Expense,
    ExpensePayment,
    ExpensePaymentAllocation,
    ExpensePaymentMethod,
    ExpensePaymentDebitLink,
)


class ExpensePaymentAllocationSerializer(BaseSerializer):
    class Meta:
        model = ExpensePaymentAllocation
        fields = [
            "id",
            "payment",
            "expense",
            "amount",
            "is_partial",
            "legacy_id",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["status", "created_at", "modified_at"]


class ExpensePaymentMethodSerializer(BaseSerializer):
    class Meta:
        model = ExpensePaymentMethod
        fields = [
            "id",
            "payment",
            "payment_type_code",
            "bank_code",
            "branch_code",
            "check_number",
            "check_identifier",
            "document_number",
            "document_piece",
            "due_date",
            "amount",
            "taxpayer_number",
            "receipt_payment_legacy_id",
            "legacy_id",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["status", "created_at", "modified_at"]


class ExpensePaymentDebitSerializer(BaseSerializer):
    class Meta:
        model = ExpensePaymentDebitLink
        fields = [
            "id",
            "payment",
            "debit_legacy_id",
            "amount",
            "is_partial",
            "legacy_id",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["status", "created_at", "modified_at"]


class ExpensePaymentSerializer(BaseSerializer):
    allocations = ExpensePaymentAllocationSerializer(many=True, read_only=True)
    payment_methods = ExpensePaymentMethodSerializer(many=True, read_only=True)
    debit_links = ExpensePaymentDebitSerializer(many=True, read_only=True)

    class Meta:
        model = ExpensePayment
        fields = [
            "id",
            "payment_date",
            "person_legacy_id",
            "currency",
            "exchange_rate",
            "total_amount",
            "retention_subject_amount",
            "observations",
            "advance_amount",
            "discount_saf_amount",
            "discount_for_payment_amount",
            "retention_balance_amount",
            "retention_total_amount",
            "status_label",
            "legacy_id",
            "allocations",
            "payment_methods",
            "debit_links",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = [
            "allocations",
            "payment_methods",
            "debit_links",
            "retention_total_amount",
            "status",
            "created_at",
            "modified_at",
        ]

    def validate_total_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("El importe total debe ser mayor a cero.")
        return value

    def validate_exchange_rate(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cotización debe ser mayor a cero.")
        return value

    def validate(self, attrs):
        monetary_fields = [
            "retention_subject_amount",
            "advance_amount",
            "discount_saf_amount",
            "discount_for_payment_amount",
            "retention_balance_amount",
            "retention_total_amount",
        ]
        for field in monetary_fields:
            value = attrs.get(field)
            if value is not None and value < 0:
                raise serializers.ValidationError({field: "El importe no puede ser negativo."})
        return attrs


class ExpensePaymentAllocationInputSerializer(serializers.Serializer):
    expense = serializers.PrimaryKeyRelatedField(queryset=Expense.objects.all())
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    is_partial = serializers.BooleanField(required=False, default=False)
