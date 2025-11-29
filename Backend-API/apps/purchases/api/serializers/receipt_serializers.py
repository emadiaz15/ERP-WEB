from rest_framework import serializers

from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.purchases.models import PurchaseReceipt, PurchaseReceiptItem


class PurchaseReceiptItemSerializer(BaseSerializer):
    class Meta:
        model = PurchaseReceiptItem
        fields = [
            "id",
            "receipt",
            "order_item",
            "product",
            "description",
            "quantity",
            "unit_price",
            "tax_rate",
            "legacy_description_id",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = [
            "status",
            "created_at",
            "modified_at",
        ]


class PurchaseReceiptSerializer(BaseSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    items = PurchaseReceiptItemSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseReceipt
        fields = [
            "id",
            "order",
            "supplier",
            "supplier_name",
            "receipt_date",
            "invoice_letter",
            "invoice_pos",
            "invoice_number",
            "total_gross",
            "total_tax",
            "total_amount",
            "currency",
            "exchange_rate",
            "notes",
            "legacy_id",
            "items",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = [
            "status",
            "created_at",
            "modified_at",
        ]

    def validate(self, attrs):
        total_gross = attrs.get("total_gross")
        total_tax = attrs.get("total_tax")
        total_amount = attrs.get("total_amount")
        if total_amount is not None and total_gross is not None and total_tax is not None:
            if total_amount < total_gross + total_tax:
                raise serializers.ValidationError("El total debe ser al menos igual al neto + impuestos.")
        return super().validate(attrs)
