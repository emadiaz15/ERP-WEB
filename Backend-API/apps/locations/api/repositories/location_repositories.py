from apps.locations.models import (
    Country,
    Province,
    PostalCode,
    SalesZone,
    Locality,
)


class CountryRepository:
    """Data-access helpers for countries."""

    @staticmethod
    def list_active(search: str | None = None):
        qs = Country.objects.filter(status=True)
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    @staticmethod
    def get_by_id(country_id: int) -> Country | None:
        return Country.objects.filter(pk=country_id, status=True).first()

    @staticmethod
    def update(country: Country, user, **fields) -> Country:
        for attr, value in fields.items():
            setattr(country, attr, value)
        country.save(user=user)
        return country

    @staticmethod
    def soft_delete(country: Country, user) -> Country:
        country.delete(user=user)
        return country


class ProvinceRepository:
    """Data-access helpers for provinces/states."""

    @staticmethod
    def list_active(country_id: int | None = None, search: str | None = None):
        qs = Province.objects.filter(status=True).select_related("country")
        if country_id:
            qs = qs.filter(country_id=country_id)
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    @staticmethod
    def get_by_id(province_id: int) -> Province | None:
        return (
            Province.objects.select_related("country")
            .filter(pk=province_id, status=True)
            .first()
        )

    @staticmethod
    def update(province: Province, user, **fields) -> Province:
        for attr, value in fields.items():
            setattr(province, attr, value)
        province.save(user=user)
        return province

    @staticmethod
    def soft_delete(province: Province, user) -> Province:
        province.delete(user=user)
        return province


class PostalCodeRepository:
    """Data-access helpers for postal codes."""

    @staticmethod
    def list_active(search: str | None = None):
        qs = PostalCode.objects.filter(status=True)
        if search:
            qs = qs.filter(number__icontains=search)
        return qs

    @staticmethod
    def get_by_id(postal_code_id: int) -> PostalCode | None:
        return PostalCode.objects.filter(pk=postal_code_id, status=True).first()

    @staticmethod
    def update(postal_code: PostalCode, user, **fields) -> PostalCode:
        for attr, value in fields.items():
            setattr(postal_code, attr, value)
        postal_code.save(user=user)
        return postal_code

    @staticmethod
    def soft_delete(postal_code: PostalCode, user) -> PostalCode:
        postal_code.delete(user=user)
        return postal_code


class SalesZoneRepository:
    """Data-access helpers for sales zones."""

    @staticmethod
    def list_active(search: str | None = None, salesperson_id: int | None = None):
        qs = SalesZone.objects.filter(status=True)
        if search:
            qs = qs.filter(name__icontains=search)
        if salesperson_id is not None:
            qs = qs.filter(salesperson_legacy_id=salesperson_id)
        return qs

    @staticmethod
    def get_by_id(zone_id: int) -> SalesZone | None:
        return SalesZone.objects.filter(pk=zone_id, status=True).first()

    @staticmethod
    def update(zone: SalesZone, user, **fields) -> SalesZone:
        for attr, value in fields.items():
            setattr(zone, attr, value)
        zone.save(user=user)
        return zone

    @staticmethod
    def soft_delete(zone: SalesZone, user) -> SalesZone:
        zone.delete(user=user)
        return zone


class LocalityRepository:
    """Data-access helpers for localities/cities."""

    @staticmethod
    def list_active(
        province_id: int | None = None,
        country_id: int | None = None,
        zone_id: int | None = None,
        postal_code_id: int | None = None,
        search: str | None = None,
    ):
        qs = (
            Locality.objects.filter(status=True)
            .select_related("province", "province__country", "postal_code", "zone")
        )
        if province_id:
            qs = qs.filter(province_id=province_id)
        if country_id:
            qs = qs.filter(province__country_id=country_id)
        if zone_id:
            qs = qs.filter(zone_id=zone_id)
        if postal_code_id:
            qs = qs.filter(postal_code_id=postal_code_id)
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    @staticmethod
    def get_by_id(locality_id: int) -> Locality | None:
        return (
            Locality.objects.select_related(
                "province",
                "province__country",
                "postal_code",
                "zone",
            )
            .filter(pk=locality_id, status=True)
            .first()
        )

    @staticmethod
    def update(locality: Locality, user, **fields) -> Locality:
        for attr, value in fields.items():
            setattr(locality, attr, value)
        locality.save(user=user)
        return locality

    @staticmethod
    def soft_delete(locality: Locality, user) -> Locality:
        locality.delete(user=user)
        return locality
