from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.customers.models import (
    Customer,
    CustomerZone,
    CustomerLocation,
    PostalCode,
    TaxCondition,
)


class CustomerZoneSerializer(BaseSerializer):
    class Meta:
        model = CustomerZone
        fields = [
            "id",
            "legacy_id",
            "name",
            "vendor_legacy_id",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["status", "created_at", "modified_at"]


class PostalCodeSerializer(BaseSerializer):
    class Meta:
        model = PostalCode
        fields = [
            "id",
            "legacy_id",
            "code",
            "number",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["status", "created_at", "modified_at"]


class CustomerLocationSerializer(BaseSerializer):
    postal_code_detail = PostalCodeSerializer(source="postal_code", read_only=True)

    class Meta:
        model = CustomerLocation
        fields = [
            "id",
            "legacy_id",
            "name",
            "province_name",
            "postal_code",
            "postal_code_detail",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["postal_code_detail", "status", "created_at", "modified_at"]


class TaxConditionSerializer(BaseSerializer):
    class Meta:
        model = TaxCondition
        fields = [
            "id",
            "legacy_id",
            "name",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["status", "created_at", "modified_at"]


class CustomerSerializer(BaseSerializer):
    zone_detail = CustomerZoneSerializer(source="zone", read_only=True)
    city_detail = CustomerLocationSerializer(source="city", read_only=True)
    tax_condition_detail = TaxConditionSerializer(source="tax_condition", read_only=True)

    class Meta:
        model = Customer
        fields = [
            "id",
            "legacy_id",
            "code",
            "name",
            "address",
            "email",
            "phone_primary",
            "phone_secondary",
            "mobile_phone",
            "cuit",
            "legacy_balance",
            "legacy_credit",
            "notes",
            "city",
            "city_detail",
            "zone",
            "zone_detail",
            "tax_condition",
            "tax_condition_detail",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = [
            "city_detail",
            "zone_detail",
            "tax_condition_detail",
            "status",
            "created_at",
            "modified_at",
        ]
