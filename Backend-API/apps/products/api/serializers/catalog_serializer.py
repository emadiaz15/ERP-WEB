from rest_framework import serializers

from apps.products.models.product_model import Product
from apps.products.api.serializers.metrics_serializer import ProductMetricsSerializer
from apps.products.api.serializers.customer_product_serializer import CustomerProductSerializer
from apps.suppliers.api.serializers import SupplierProductSerializer
from apps.products.api.serializers.dictionary_serializer import (
    ProductAbbreviationSerializer,
    ProductSynonymSerializer,
    ProductAliasSerializer,
)
from apps.products.api.serializers.stock_history_serializer import ProductStockHistorySerializer


class CatalogSearchParamsSerializer(serializers.Serializer):
    """Valida filtros de búsqueda de catálogo."""

    query = serializers.CharField(required=False, allow_blank=True)
    category_id = serializers.IntegerField(required=False, min_value=1)
    has_metrics = serializers.BooleanField(required=False)
    customer_legacy_id = serializers.IntegerField(required=False, min_value=1)
    supplier_legacy_id = serializers.IntegerField(required=False, min_value=1)
    include_inactive = serializers.BooleanField(required=False)


class CatalogProductSerializer(serializers.ModelSerializer):
    """Vista resumida del artículo con señales de búsqueda."""

    category_name = serializers.CharField(source="category.name", read_only=True)
    metrics = ProductMetricsSerializer(read_only=True)
    synonym_samples = serializers.SerializerMethodField()
    abbreviation_samples = serializers.SerializerMethodField()
    alias_samples = serializers.SerializerMethodField()
    match_score = serializers.IntegerField(read_only=True, default=0)
    synonym_hit = serializers.BooleanField(read_only=True, default=False)
    abbreviation_hit = serializers.BooleanField(read_only=True, default=False)
    alias_hit = serializers.BooleanField(read_only=True, default=False)
    customer_match_count = serializers.IntegerField(read_only=True, default=0)
    supplier_match_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Product
        fields = [
            "id",
            "code",
            "name",
            "price",
            "last_purchase_cost",
            "unit",
            "brand",
            "location",
            "position",
            "category",
            "category_name",
            "has_subproducts",
            "status",
            "match_score",
            "synonym_hit",
            "abbreviation_hit",
            "alias_hit",
            "customer_match_count",
            "supplier_match_count",
            "synonym_samples",
            "abbreviation_samples",
            "alias_samples",
            "metrics",
        ]
        read_only_fields = fields

    def _get_sample(self, obj, relation_name, attr_name, limit=5):
        relation = getattr(obj, relation_name, None)
        if relation is None:
            return []
        values = getattr(relation, "all", lambda: relation)()
        sample = []
        for item in values[:limit]:  # type: ignore[index]
            sample.append(getattr(item, attr_name, ""))
        return sample

    def get_synonym_samples(self, obj):
        return self._get_sample(obj, "synonyms", "synonym")

    def get_abbreviation_samples(self, obj):
        return self._get_sample(obj, "abbreviations", "abbreviation")

    def get_alias_samples(self, obj):
        return self._get_sample(obj, "aliases", "alias_text")


class ProductInsightSerializer(CatalogProductSerializer):
    """Vista completa del artículo con relaciones detalladas."""

    detail_internal = serializers.CharField(read_only=True)
    detail_public = serializers.CharField(read_only=True)
    customer_overrides = CustomerProductSerializer(many=True, read_only=True, source="customer_products")
    supplier_overrides = SupplierProductSerializer(many=True, read_only=True, source="supplier_products")
    abbreviations = ProductAbbreviationSerializer(many=True, read_only=True, source="abbreviations")
    synonyms = ProductSynonymSerializer(many=True, read_only=True, source="synonyms")
    aliases = ProductAliasSerializer(many=True, read_only=True, source="aliases")
    stock_history = serializers.SerializerMethodField()

    class Meta(CatalogProductSerializer.Meta):
        fields = CatalogProductSerializer.Meta.fields + [
            "detail_internal",
            "detail_public",
            "customer_overrides",
            "supplier_overrides",
            "abbreviations",
            "synonyms",
            "aliases",
            "stock_history",
        ]
        read_only_fields = fields

    def get_stock_history(self, obj):
        history = self.context.get("history", [])
        if not history:
            return []
        serializer = ProductStockHistorySerializer(history, many=True)
        return serializer.data
