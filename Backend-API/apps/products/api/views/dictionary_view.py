from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.products.api.serializers.dictionary_serializer import (
    ProductAbbreviationSerializer,
    ProductSynonymSerializer,
    TermDictionarySerializer,
    ProductAliasSerializer,
)
from apps.products.docs.dictionary_doc import (
    abbreviation_list_doc,
    abbreviation_detail_doc,
    synonym_list_doc,
    synonym_detail_doc,
    term_list_doc,
    term_detail_doc,
    alias_list_doc,
    alias_detail_doc,
)
from apps.products.models.dictionary_models import (
    ProductAbbreviation,
    ProductSynonym,
    TermDictionary,
    ProductAlias,
)


def _require_admin(request):
    if not request.user.is_staff:
        return Response({"detail": "Permiso denegado."}, status=status.HTTP_403_FORBIDDEN)
    return None


@extend_schema(**abbreviation_list_doc)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def product_abbreviation_list_view(request):
    qs = ProductAbbreviation.objects.filter(status=True)
    product_id = request.query_params.get("product_id")
    if product_id:
        qs = qs.filter(product_id=product_id)

    if request.method == "GET":
        serializer = ProductAbbreviationSerializer(qs, many=True)
        return Response(serializer.data)

    denied = _require_admin(request)
    if denied:
        return denied

    serializer = ProductAbbreviationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save(user=request.user)
    return Response(ProductAbbreviationSerializer(instance).data, status=status.HTTP_201_CREATED)


@extend_schema(**abbreviation_detail_doc)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def product_abbreviation_detail_view(request, pk: int):
    instance = get_object_or_404(ProductAbbreviation, pk=pk, status=True)

    if request.method == "GET":
        return Response(ProductAbbreviationSerializer(instance).data)

    denied = _require_admin(request)
    if denied:
        return denied

    if request.method == "PUT":
        serializer = ProductAbbreviationSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save(user=request.user)
        return Response(ProductAbbreviationSerializer(updated).data)

    instance.delete(user=request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(**synonym_list_doc)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def product_synonym_list_view(request):
    qs = ProductSynonym.objects.filter(status=True)
    product_id = request.query_params.get("product_id")
    if product_id:
        qs = qs.filter(product_id=product_id)

    if request.method == "GET":
        serializer = ProductSynonymSerializer(qs, many=True)
        return Response(serializer.data)

    denied = _require_admin(request)
    if denied:
        return denied

    serializer = ProductSynonymSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save(user=request.user)
    return Response(ProductSynonymSerializer(instance).data, status=status.HTTP_201_CREATED)


@extend_schema(**synonym_detail_doc)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def product_synonym_detail_view(request, pk: int):
    instance = get_object_or_404(ProductSynonym, pk=pk, status=True)

    if request.method == "GET":
        return Response(ProductSynonymSerializer(instance).data)

    denied = _require_admin(request)
    if denied:
        return denied

    if request.method == "PUT":
        serializer = ProductSynonymSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save(user=request.user)
        return Response(ProductSynonymSerializer(updated).data)

    instance.delete(user=request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(**term_list_doc)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def term_dictionary_list_view(request):
    qs = TermDictionary.objects.filter(status=True)

    if request.method == "GET":
        serializer = TermDictionarySerializer(qs, many=True)
        return Response(serializer.data)

    denied = _require_admin(request)
    if denied:
        return denied

    serializer = TermDictionarySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save(user=request.user)
    return Response(TermDictionarySerializer(instance).data, status=status.HTTP_201_CREATED)


@extend_schema(**term_detail_doc)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def term_dictionary_detail_view(request, pk: int):
    instance = get_object_or_404(TermDictionary, pk=pk, status=True)

    if request.method == "GET":
        return Response(TermDictionarySerializer(instance).data)

    denied = _require_admin(request)
    if denied:
        return denied

    if request.method == "PUT":
        serializer = TermDictionarySerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save(user=request.user)
        return Response(TermDictionarySerializer(updated).data)

    instance.delete(user=request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(**alias_list_doc)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def product_alias_list_view(request):
    qs = ProductAlias.objects.filter(status=True)
    product_id = request.query_params.get("product_id")
    client_id = request.query_params.get("client_legacy_id")
    if product_id:
        qs = qs.filter(product_id=product_id)
    if client_id:
        qs = qs.filter(client_legacy_id=client_id)

    if request.method == "GET":
        serializer = ProductAliasSerializer(qs, many=True)
        return Response(serializer.data)

    denied = _require_admin(request)
    if denied:
        return denied

    serializer = ProductAliasSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save(user=request.user)
    return Response(ProductAliasSerializer(instance).data, status=status.HTTP_201_CREATED)


@extend_schema(**alias_detail_doc)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def product_alias_detail_view(request, pk: int):
    instance = get_object_or_404(ProductAlias, pk=pk, status=True)

    if request.method == "GET":
        return Response(ProductAliasSerializer(instance).data)

    denied = _require_admin(request)
    if denied:
        return denied

    if request.method == "PUT":
        serializer = ProductAliasSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save(user=request.user)
        return Response(ProductAliasSerializer(updated).data)

    instance.delete(user=request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)
