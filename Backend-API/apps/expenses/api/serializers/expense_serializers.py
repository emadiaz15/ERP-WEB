from decimal import Decimal

from rest_framework import serializers

from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.expenses.models import Expense, ExpenseItem, ExpenseDisbursement


class ExpenseItemSerializer(BaseSerializer):
    class Meta:
        model = ExpenseItem
        fields = [
            "id",
            "expense",
            "description",
            "quantity",
            "unit_amount",
            "total_amount",
            "vat_rate_code",
            "vat_rate_percent",
            "legacy_description_id",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["status", "created_at", "modified_at"]


class ExpenseDisbursementSerializer(BaseSerializer):
    class Meta:
        model = ExpenseDisbursement
        fields = [
            "id",
            "expense",
            "expense_type_code",
            "transaction_number",
            "bank_code",
            "document_piece",
            "due_date",
            "amount",
            "taxpayer_number",
            "legacy_id",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["status", "created_at", "modified_at"]


class ExpenseSerializer(BaseSerializer):
    expense_type_name = serializers.CharField(source="expense_type.name", read_only=True)
    approved_by_username = serializers.CharField(source="approved_by.username", read_only=True)
    total_amount = serializers.SerializerMethodField()
    items = ExpenseItemSerializer(many=True, read_only=True)
    disbursements = ExpenseDisbursementSerializer(many=True, read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id",
            "expense_type",
            "expense_type_name",
            "person_legacy_id",
            "expense_date",
            "concept",
            "notes",
            "currency",
            "exchange_rate",
            "discount_percent",
            "due_date",
            "point_of_sale",
            "receipt_number",
            "receipt_type_code",
            "receipt_reference",
            "withholding_number",
            "iva_condition_id",
            "vat_perception_amount",
            "gross_income_perception_amount",
            "amount_paid",
            "paid_flag",
            "net_amount_primary",
            "net_amount_secondary",
            "net_amount_third",
            "non_taxed_amount",
            "vat_amount_primary",
            "vat_amount_secondary",
            "vat_amount_third",
            "vat_debit_amount",
            "vat_credit_amount",
            "alternate_vat_rate_primary",
            "alternate_vat_rate_secondary",
            "discount_to_pay_amount",
            "cost_center_code",
            "credit_note_reference",
            "approval_notes",
            "approved_at",
            "approved_by",
            "approved_by_username",
            "status_label",
            "legacy_id",
            "total_amount",
            "items",
            "disbursements",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = [
            "status",
            "created_at",
            "modified_at",
            "total_amount",
            "items",
            "disbursements",
            "approved_at",
            "approved_by",
            "approved_by_username",
        ]

    def validate_discount_percent(self, value):
        if value < 0:
            raise serializers.ValidationError("El descuento no puede ser negativo.")
        if value > 100:
            raise serializers.ValidationError("El descuento no puede superar el 100%.")
        return value

    def validate_exchange_rate(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cotización debe ser mayor a cero.")
        return value

    def validate(self, attrs):
        monetary_fields = [
            "vat_perception_amount",
            "gross_income_perception_amount",
            "amount_paid",
            "net_amount_primary",
            "net_amount_secondary",
            "net_amount_third",
            "non_taxed_amount",
            "vat_amount_primary",
            "vat_amount_secondary",
            "vat_amount_third",
            "vat_debit_amount",
            "vat_credit_amount",
            "discount_to_pay_amount",
        ]
        for field in monetary_fields:
            value = attrs.get(field)
            if value is not None and value < 0:
                raise serializers.ValidationError({field: "El importe no puede ser negativo."})
        return attrs

    def get_total_amount(self, obj: Expense) -> Decimal:
        return obj.compute_total_amount()
