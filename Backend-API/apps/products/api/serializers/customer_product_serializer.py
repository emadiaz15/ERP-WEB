from rest_framework import serializers

from apps.products.models.customer_product_model import CustomerProduct
from .base_serializer import BaseSerializer


class CustomerProductSerializer(BaseSerializer):
    """Serializer for customer-specific product descriptions.

    This maps the legacy table ``articulos_clientes`` where each row
    customizes how a product is shown for a given client.
    """

    class Meta:
        model = CustomerProduct
        fields = [
            "id",
            "product",
            "customer_legacy_id",
            "description",
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

    def validate(self, attrs):
        """Ensure there is no duplicated (product, customer_legacy_id) pair.

        This prevents having multiple rows for the same product/customer
        combination, which would complicate pricing/description logic.
        """

        product = attrs.get("product") or getattr(self.instance, "product", None)
        customer_legacy_id = attrs.get("customer_legacy_id") or getattr(
            self.instance, "customer_legacy_id", None
        )

        if product and customer_legacy_id is not None:
            qs = CustomerProduct.objects.filter(
                product=product,
                customer_legacy_id=customer_legacy_id,
                status=True,
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "Ya existe una configuración para este producto y cliente legacy."
                )
        return attrs
