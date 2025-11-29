from rest_framework import serializers

from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.customers.models import (
    CustomerProductDetail,
    CustomerProductDescription,
)


class CustomerProductDescriptionSerializer(BaseSerializer):
    class Meta:
        model = CustomerProductDescription
        fields = [
            "id",
            "detail",
            "description",
            "legacy_id",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["status", "created_at", "modified_at"]


class CustomerProductDetailSerializer(BaseSerializer):
    descriptions = CustomerProductDescriptionSerializer(many=True, read_only=True)

    class Meta:
        model = CustomerProductDetail
        fields = [
            "id",
            "customer",
            "product",
            "custom_description",
            "legacy_id",
            "descriptions",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["descriptions", "status", "created_at", "modified_at"]

    def validate(self, attrs):
        customer = attrs.get("customer", getattr(self.instance, "customer", None))
        product = attrs.get("product", getattr(self.instance, "product", None))
        if not customer or not product:
            raise serializers.ValidationError("Debe especificar cliente y producto.")
        return super().validate(attrs)
