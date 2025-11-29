from django.db.models import (
    Q,
    Exists,
    OuterRef,
    Value,
    IntegerField,
    Case,
    When,
    Count,
)
from django.db.models.functions import Coalesce

from apps.products.models import (
    Product,
    CustomerProduct,
    SupplierProduct,
    ProductAbbreviation,
    ProductSynonym,
    ProductAlias,
)
from apps.products.models.metrics_model import ProductMetrics
from apps.stocks.models import ProductStockHistory


class CatalogRepository:
    """Consultas centralizadas para el catálogo maestro."""

    @staticmethod
    def base_queryset(include_inactive=False):
        qs = Product.objects.select_related("category", "metrics").prefetch_related(
            "abbreviations",
            "synonyms",
            "aliases",
        )
        if not include_inactive:
            qs = qs.filter(status=True)
        return qs

    @staticmethod
    def search_products(keyword=None, filters=None):
        filters = filters or {}
        keyword = (keyword or "").strip()
        qs = CatalogRepository.base_queryset(
            include_inactive=filters.get("include_inactive", False)
        )

        abbr_exists = ProductAbbreviation.objects.filter(
            product_id=OuterRef("pk"),
            abbreviation__icontains=keyword,
            status=True,
        )
        syn_exists = ProductSynonym.objects.filter(
            product_id=OuterRef("pk"),
            synonym__icontains=keyword,
            status=True,
        )
        alias_exists = ProductAlias.objects.filter(
            product_id=OuterRef("pk"),
            alias_text__icontains=keyword,
            status=True,
        )

        if keyword:
            qs = qs.filter(
                Q(code__icontains=keyword)
                | Q(name__icontains=keyword)
                | Q(detail_public__icontains=keyword)
                | Q(detail_internal__icontains=keyword)
                | Q(category__name__icontains=keyword)
                | Exists(abbr_exists)
                | Exists(syn_exists)
                | Exists(alias_exists)
            )

            qs = qs.annotate(
                match_score=Case(
                    When(code__istartswith=keyword, then=Value(100)),
                    When(code__icontains=keyword, then=Value(90)),
                    When(name__istartswith=keyword, then=Value(80)),
                    When(name__icontains=keyword, then=Value(70)),
                    When(detail_public__icontains=keyword, then=Value(60)),
                    When(detail_internal__icontains=keyword, then=Value(50)),
                    default=Value(25),
                    output_field=IntegerField(),
                ),
                synonym_hit=Exists(syn_exists),
                abbreviation_hit=Exists(abbr_exists),
                alias_hit=Exists(alias_exists),
            )
        else:
            qs = qs.annotate(
                match_score=Value(0, output_field=IntegerField()),
                synonym_hit=Value(False),
                abbreviation_hit=Value(False),
                alias_hit=Value(False),
            )

        category_id = filters.get("category_id")
        if category_id:
            qs = qs.filter(category_id=category_id)

        if filters.get("has_metrics"):
            qs = qs.filter(metrics__isnull=False)

        customer_legacy_id = filters.get("customer_legacy_id")
        if customer_legacy_id:
            qs = qs.filter(
                Exists(
                    CustomerProduct.objects.filter(
                        product_id=OuterRef("pk"),
                        customer_legacy_id=customer_legacy_id,
                        status=True,
                    )
                )
            )

        supplier_legacy_id = filters.get("supplier_legacy_id")
        if supplier_legacy_id:
            qs = qs.filter(
                Exists(
                    SupplierProduct.objects.filter(
                        product_id=OuterRef("pk"),
                        supplier_legacy_id=supplier_legacy_id,
                        status=True,
                    )
                )
            )

        qs = qs.annotate(
            customer_match_count=Coalesce(
                Count(
                    "customer_products",
                    filter=Q(customer_products__status=True),
                    distinct=True,
                ),
                Value(0),
            ),
            supplier_match_count=Coalesce(
                Count(
                    "supplier_products",
                    filter=Q(supplier_products__status=True),
                    distinct=True,
                ),
                Value(0),
            ),
        )

        return qs.order_by("-match_score", "-synonym_hit", "name")

    @staticmethod
    def get_product_with_relations(product_id):
        return (
            CatalogRepository.base_queryset(include_inactive=True)
            .prefetch_related(
                "customer_products",
                "supplier_products",
            )
            .get(pk=product_id)
        )

    @staticmethod
    def get_stock_history(product_id, limit=25):
        return ProductStockHistory.objects.filter(product_id=product_id).order_by(
            "-date",
            "-time",
            "-created_at",
        )[:limit]

    @staticmethod
    def metrics_queryset(filters=None):
        filters = filters or {}
        qs = ProductMetrics.objects.select_related("product", "product__category")
        if not filters.get("include_inactive"):
            qs = qs.filter(status=True, product__status=True)

        category_id = filters.get("category_id")
        if category_id:
            qs = qs.filter(product__category_id=category_id)

        rotation_min = filters.get("rotation_min")
        if rotation_min is not None:
            qs = qs.filter(rotation__gte=rotation_min)

        rotation_max = filters.get("rotation_max")
        if rotation_max is not None:
            qs = qs.filter(rotation__lte=rotation_max)

        days_since_last_sale = filters.get("days_since_last_sale")
        if days_since_last_sale is not None:
            qs = qs.filter(days_since_last_sale__gte=days_since_last_sale)

        return qs.order_by("product__name")
