from rest_framework import serializers

from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.sales.models import SalesInvoice, SalesInvoiceItem


class SalesInvoiceItemSerializer(BaseSerializer):
    class Meta:
        model = SalesInvoiceItem
        fields = [
            "id",
            "invoice",
            "order_item",
            "shipment_item",
            "product",
            "description",
            "quantity",
            "unit_price",
            "discount_amount",
            "vat_rate_code",
            "legacy_detail_id",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["status", "created_at", "modified_at"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser positiva.")
        return value


class SalesInvoiceSerializer(BaseSerializer):
    items = SalesInvoiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = SalesInvoice
        fields = [
            "id",
            "order",
            "shipment",
            "customer_legacy_id",
            "invoice_type",
            "point_of_sale",
            "invoice_number",
            "issue_date",
            "due_date",
            "currency",
            "exchange_rate",
            "subtotal_amount",
            "discount_amount",
            "tax_amount",
            "total_amount",
            "notes",
            "legacy_id",
            "status_label",
            "items",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["status", "created_at", "modified_at"]

    def validate(self, attrs):
        subtotal = attrs.get("subtotal_amount", 0)
        discounts = attrs.get("discount_amount", 0)
        taxes = attrs.get("tax_amount", 0)
        total = attrs.get("total_amount", 0)
        if total < subtotal - discounts + taxes:
            raise serializers.ValidationError(
                "El total debe ser mayor o igual a subtotal - descuentos + impuestos."
            )
        return super().validate(attrs)
