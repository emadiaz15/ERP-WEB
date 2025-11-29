from rest_framework import serializers

from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.locations.models import (
    Country,
    Province,
    PostalCode,
    SalesZone,
    Locality,
)


class CountrySerializer(BaseSerializer):
    """Serializer for country catalog entries."""

    class Meta:
        model = Country
        fields = [
            "id",
            "name",
            "iso_code",
            "legacy_code",
            "status",
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]
        read_only_fields = [
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]

    def validate_name(self, value: str) -> str:
        return self._get_normalized_name(value)

    def validate_iso_code(self, value: str) -> str:
        value = (value or "").strip().upper()
        if len(value) != 3:
            raise serializers.ValidationError("El código ISO debe tener 3 caracteres.")
        return value


class ProvinceSerializer(BaseSerializer):
    """Serializer for provinces/states."""

    country_name = serializers.CharField(source="country.name", read_only=True)

    class Meta:
        model = Province
        fields = [
            "id",
            "country",
            "country_name",
            "name",
            "legacy_code",
            "status",
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]
        read_only_fields = [
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
            "country_name",
        ]


class PostalCodeSerializer(BaseSerializer):
    """Serializer for postal code catalog."""

    class Meta:
        model = PostalCode
        fields = [
            "id",
            "number",
            "legacy_code",
            "status",
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]
        read_only_fields = [
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]


class SalesZoneSerializer(BaseSerializer):
    """Serializer for traveling salesperson zones."""

    class Meta:
        model = SalesZone
        fields = [
            "id",
            "name",
            "legacy_code",
            "salesperson_legacy_id",
            "status",
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]
        read_only_fields = [
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]

    def validate_name(self, value: str) -> str:
        return self._get_normalized_name(value)


class LocalitySerializer(BaseSerializer):
    """Serializer for localities/cities."""

    province_name = serializers.CharField(source="province.name", read_only=True)
    country_id = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    postal_code_number = serializers.SerializerMethodField()
    zone_name = serializers.SerializerMethodField()

    class Meta:
        model = Locality
        fields = [
            "id",
            "province",
            "province_name",
            "country_id",
            "country_name",
            "postal_code",
            "postal_code_number",
            "zone",
            "zone_name",
            "name",
            "legacy_code",
            "status",
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]
        read_only_fields = [
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
            "province_name",
            "country_id",
            "country_name",
            "postal_code_number",
            "zone_name",
        ]

    def get_country_id(self, obj):  # noqa: D401 - simple delegation
        province = getattr(obj, "province", None)
        return province.country_id if province else None

    def get_country_name(self, obj):
        province = getattr(obj, "province", None)
        return province.country.name if province and province.country else None

    def get_postal_code_number(self, obj):
        return obj.postal_code.number if obj.postal_code else None

    def get_zone_name(self, obj):
        return obj.zone.name if obj.zone else None
