from rest_framework import serializers

from apps.products.api.serializers.base_serializer import BaseSerializer
from apps.products.models.dictionary_models import (
    ProductAbbreviation,
    ProductSynonym,
    TermDictionary,
    ProductAlias,
)
from apps.products.models.product_model import Product


class ProductAbbreviationSerializer(BaseSerializer):
    """Serializer para abreviaciones conocidas de artículos."""

    class Meta:
        model = ProductAbbreviation
        fields = [
            "id",
            "product",
            "abbreviation",
            "full_word",
            "weight",
            "notes",
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
        product = attrs.get("product") or getattr(self.instance, "product", None)
        abbreviation = attrs.get("abbreviation") or getattr(self.instance, "abbreviation", None)
        if product and abbreviation:
            qs = ProductAbbreviation.objects.filter(
                product=product,
                abbreviation__iexact=abbreviation,
                status=True,
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "Ya existe una abreviación igual para este producto.",
                )
        return attrs


class ProductSynonymSerializer(BaseSerializer):
    """Serializer para sinónimos/alias semánticos."""

    class Meta:
        model = ProductSynonym
        fields = [
            "id",
            "product",
            "synonym",
            "type",
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
        product = attrs.get("product") or getattr(self.instance, "product", None)
        synonym = attrs.get("synonym") or getattr(self.instance, "synonym", None)
        syn_type = attrs.get("type") or getattr(self.instance, "type", None)
        if product and synonym and syn_type:
            qs = ProductSynonym.objects.filter(
                product=product,
                synonym__iexact=synonym,
                type=syn_type,
                status=True,
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "Ya existe un sinónimo con ese tipo para este producto.",
                )
        return attrs


class TermDictionarySerializer(BaseSerializer):
    """Serializer para el diccionario global de términos."""

    class Meta:
        model = TermDictionary
        fields = [
            "id",
            "term",
            "type",
            "value",
            "notes",
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

    def validate_term(self, value):
        term = (value or "").strip()
        if not term:
            raise serializers.ValidationError("El término es obligatorio.")
        qs = TermDictionary.objects.filter(term__iexact=term, status=True)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Este término ya existe en el diccionario.")
        return term


class ProductAliasSerializer(BaseSerializer):
    """Serializer para alias gestionados por IA o usuarios."""

    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = ProductAlias
        fields = [
            "id",
            "product",
            "product_name",
            "alias_text",
            "source",
            "client_legacy_id",
            "region",
            "confidence",
            "created_by_source",
            "status",
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]
        read_only_fields = [
            "product_name",
            "created_at",
            "modified_at",
            "deleted_at",
            "created_by_username",
            "modified_by_username",
            "deleted_by_username",
        ]

    def validate(self, attrs):
        product = attrs.get("product") or getattr(self.instance, "product", None)
        alias_text = attrs.get("alias_text") or getattr(self.instance, "alias_text", None)
        source = attrs.get("source") or getattr(self.instance, "source", None)
        if product and alias_text and source:
            qs = ProductAlias.objects.filter(
                product=product,
                alias_text__iexact=alias_text,
                source=source,
                status=True,
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "Ya existe un alias igual para este producto y fuente.",
                )
        return attrs

    def validate_confidence(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("La confianza no puede ser negativa.")
        return value

    def create(self, validated_data, user=None):
        product = validated_data.get("product") or self.context.get("product")
        if not isinstance(product, Product):
            raise serializers.ValidationError("Debe indicar un producto válido.")
        validated_data["product"] = product
        return super().create(validated_data, user=user)

    def update(self, instance, validated_data, user=None):
        validated_data.pop("product", None)
        return super().update(instance, validated_data, user=user)
