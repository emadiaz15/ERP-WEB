from rest_framework import serializers

from apps.metrics.models import MetricParameter
from apps.products.api.serializers.base_serializer import BaseSerializer


class MetricParameterSerializer(BaseSerializer):
    class Meta:
        model = MetricParameter
        fields = [
            "id",
            "legacy_code",
            "description",
            "amount_value",
            "date_value",
            "datetime_value",
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

    def validate_legacy_code(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("El codigo legacy debe ser positivo.")
        return value

    def validate_description(self, value):
        if not value:
            raise serializers.ValidationError("La descripcion es obligatoria.")
        return value.strip()
