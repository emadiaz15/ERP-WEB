import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.pagination import Pagination
from apps.locations.api.serializers import (
    CountrySerializer,
    ProvinceSerializer,
    PostalCodeSerializer,
    SalesZoneSerializer,
    LocalitySerializer,
)
from apps.locations.api.repositories import (
    CountryRepository,
    ProvinceRepository,
    PostalCodeRepository,
    SalesZoneRepository,
    LocalityRepository,
)

logger = logging.getLogger(__name__)


def _parse_int(value: str | None) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _paginate_queryset(queryset, request, serializer_class):
    paginator = Pagination()
    page = paginator.paginate_queryset(queryset, request)
    data = serializer_class(page, many=True, context={"request": request}).data
    return paginator.get_paginated_response(data)


# ───────────────────────────────
# Countries
# ───────────────────────────────
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def country_list_create(request):
    if request.method == "GET":
        search = request.query_params.get("search")
        qs = CountryRepository.list_active(search=search)
        return _paginate_queryset(qs, request, CountrySerializer)

    if not request.user.is_staff:
        return Response({"detail": "Solo administradores."}, status=status.HTTP_403_FORBIDDEN)

    serializer = CountrySerializer(data=request.data, context={"request": request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    country = serializer.save(user=request.user)
    logger.info("Country %s created by %s", country.id, request.user)
    return Response(
        CountrySerializer(country, context={"request": request}).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def country_detail(request, country_id: int):
    country = CountryRepository.get_by_id(country_id)
    if not country:
        return Response({"detail": "País no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(CountrySerializer(country, context={"request": request}).data)

    if request.method == "PUT":
        if not request.user.is_staff:
            return Response({"detail": "Solo administradores."}, status=status.HTTP_403_FORBIDDEN)
        serializer = CountrySerializer(
            country,
            data=request.data,
            context={"request": request},
            partial=True,
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        updated = CountryRepository.update(country, user=request.user, **serializer.validated_data)
        return Response(CountrySerializer(updated, context={"request": request}).data)

    if not request.user.is_staff:
        return Response({"detail": "Solo administradores."}, status=status.HTTP_403_FORBIDDEN)

    CountryRepository.soft_delete(country, user=request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)


# ───────────────────────────────
# Provinces
# ───────────────────────────────
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def province_list_create(request):
    if request.method == "GET":
        search = request.query_params.get("search")
        country_id = _parse_int(request.query_params.get("country_id"))
        qs = ProvinceRepository.list_active(country_id=country_id, search=search)
        return _paginate_queryset(qs, request, ProvinceSerializer)

    if not request.user.is_staff:
        return Response({"detail": "Solo administradores."}, status=status.HTTP_403_FORBIDDEN)

    serializer = ProvinceSerializer(data=request.data, context={"request": request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    province = serializer.save(user=request.user)
    logger.info("Province %s created by %s", province.id, request.user)
    return Response(
        ProvinceSerializer(province, context={"request": request}).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def province_detail(request, province_id: int):
    province = ProvinceRepository.get_by_id(province_id)
    if not province:
        return Response({"detail": "Provincia no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(ProvinceSerializer(province, context={"request": request}).data)

    if request.method == "PUT":
        if not request.user.is_staff:
            return Response({"detail": "Solo administradores."}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProvinceSerializer(
            province,
            data=request.data,
            context={"request": request},
            partial=True,
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        updated = ProvinceRepository.update(province, user=request.user, **serializer.validated_data)
        return Response(ProvinceSerializer(updated, context={"request": request}).data)

    if not request.user.is_staff:
        return Response({"detail": "Solo administradores."}, status=status.HTTP_403_FORBIDDEN)

    ProvinceRepository.soft_delete(province, user=request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)


# ───────────────────────────────
# Postal Codes
# ───────────────────────────────
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def postal_code_list_create(request):
    if request.method == "GET":
        search = request.query_params.get("search")
        qs = PostalCodeRepository.list_active(search=search)
        return _paginate_queryset(qs, request, PostalCodeSerializer)

    if not request.user.is_staff:
        return Response({"detail": "Solo administradores."}, status=status.HTTP_403_FORBIDDEN)

    serializer = PostalCodeSerializer(data=request.data, context={"request": request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    postal_code = serializer.save(user=request.user)
    logger.info("PostalCode %s created by %s", postal_code.id, request.user)
    return Response(
        PostalCodeSerializer(postal_code, context={"request": request}).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def postal_code_detail(request, postal_code_id: int):
    postal_code = PostalCodeRepository.get_by_id(postal_code_id)
    if not postal_code:
        return Response({"detail": "Código postal no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(PostalCodeSerializer(postal_code, context={"request": request}).data)

    if request.method == "PUT":
        if not request.user.is_staff:
            return Response({"detail": "Solo administradores."}, status=status.HTTP_403_FORBIDDEN)
        serializer = PostalCodeSerializer(
            postal_code,
            data=request.data,
            context={"request": request},
            partial=True,
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        updated = PostalCodeRepository.update(
            postal_code,
            user=request.user,
            **serializer.validated_data,
        )
        return Response(PostalCodeSerializer(updated, context={"request": request}).data)

    if not request.user.is_staff:
        return Response({"detail": "Solo administradores."}, status=status.HTTP_403_FORBIDDEN)

    PostalCodeRepository.soft_delete(postal_code, user=request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)


# ───────────────────────────────
# Sales Zones
# ───────────────────────────────
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def sales_zone_list_create(request):
    if request.method == "GET":
        search = request.query_params.get("search")
        salesperson_id = _parse_int(request.query_params.get("salesperson_id"))
        qs = SalesZoneRepository.list_active(search=search, salesperson_id=salesperson_id)
        return _paginate_queryset(qs, request, SalesZoneSerializer)

    if not request.user.is_staff:
        return Response({"detail": "Solo administradores."}, status=status.HTTP_403_FORBIDDEN)

    serializer = SalesZoneSerializer(data=request.data, context={"request": request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    zone = serializer.save(user=request.user)
    logger.info("SalesZone %s created by %s", zone.id, request.user)
    return Response(
        SalesZoneSerializer(zone, context={"request": request}).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def sales_zone_detail(request, zone_id: int):
    zone = SalesZoneRepository.get_by_id(zone_id)
    if not zone:
        return Response({"detail": "Zona no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(SalesZoneSerializer(zone, context={"request": request}).data)

    if request.method == "PUT":
        if not request.user.is_staff:
            return Response({"detail": "Solo administradores."}, status=status.HTTP_403_FORBIDDEN)
        serializer = SalesZoneSerializer(
            zone,
            data=request.data,
            context={"request": request},
            partial=True,
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        updated = SalesZoneRepository.update(zone, user=request.user, **serializer.validated_data)
        return Response(SalesZoneSerializer(updated, context={"request": request}).data)

    if not request.user.is_staff:
        return Response({"detail": "Solo administradores."}, status=status.HTTP_403_FORBIDDEN)

    SalesZoneRepository.soft_delete(zone, user=request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)


# ───────────────────────────────
# Localities
# ───────────────────────────────
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def locality_list_create(request):
    if request.method == "GET":
        search = request.query_params.get("search")
        province_id = _parse_int(request.query_params.get("province_id"))
        country_id = _parse_int(request.query_params.get("country_id"))
        zone_id = _parse_int(request.query_params.get("zone_id"))
        postal_code_id = _parse_int(request.query_params.get("postal_code_id"))
        qs = LocalityRepository.list_active(
            province_id=province_id,
            country_id=country_id,
            zone_id=zone_id,
            postal_code_id=postal_code_id,
            search=search,
        )
        return _paginate_queryset(qs, request, LocalitySerializer)

    if not request.user.is_staff:
        return Response({"detail": "Solo administradores."}, status=status.HTTP_403_FORBIDDEN)

    serializer = LocalitySerializer(data=request.data, context={"request": request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    locality = serializer.save(user=request.user)
    logger.info("Locality %s created by %s", locality.id, request.user)
    return Response(
        LocalitySerializer(locality, context={"request": request}).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def locality_detail(request, locality_id: int):
    locality = LocalityRepository.get_by_id(locality_id)
    if not locality:
        return Response({"detail": "Localidad no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(LocalitySerializer(locality, context={"request": request}).data)

    if request.method == "PUT":
        if not request.user.is_staff:
            return Response({"detail": "Solo administradores."}, status=status.HTTP_403_FORBIDDEN)
        serializer = LocalitySerializer(
            locality,
            data=request.data,
            context={"request": request},
            partial=True,
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        updated = LocalityRepository.update(locality, user=request.user, **serializer.validated_data)
        return Response(LocalitySerializer(updated, context={"request": request}).data)

    if not request.user.is_staff:
        return Response({"detail": "Solo administradores."}, status=status.HTTP_403_FORBIDDEN)

    LocalityRepository.soft_delete(locality, user=request.user)
    return Response(status=status.HTTP_204_NO_CONTENT)
