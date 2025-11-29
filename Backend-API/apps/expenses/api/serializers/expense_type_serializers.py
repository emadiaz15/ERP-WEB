from rest_framework import serializers

from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.expenses.models import ExpenseType


class ExpenseTypeSerializer(BaseSerializer):
    class Meta:
        model = ExpenseType
        fields = [
            "id",
            "code",
            "name",
            "description",
            "legacy_id",
            "category",
            "is_tax_related",
            "requires_approval",
            "retention_percent",
            "retention_minimum_amount",
            "status",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["status", "created_at", "modified_at"]

    def validate_code(self, value):
        value = value.strip().upper()
        if not value:
            raise serializers.ValidationError("El código no puede quedar vacío.")
        qs = ExpenseType.objects.filter(code=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un tipo con ese código.")
        return value
