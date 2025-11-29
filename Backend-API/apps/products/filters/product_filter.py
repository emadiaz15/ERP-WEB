import django_filters
from django.core.exceptions import ValidationError
from django.db.models import Exists, OuterRef
from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct


class ProductFilter(django_filters.FilterSet):
    """
    Filtros para Product:
      - code: startswith (sólo dígitos)
      - category: icontains (nombre)
      - type: icontains (nombre)
      - name: icontains
      - has_subproducts: boolean (anotado)
    """
    code = django_filters.CharFilter(
        field_name='code',
        lookup_expr='startswith',
        label='Filtrar por código (prefijo)'
    )
    category = django_filters.CharFilter(
        field_name='category__name',
        lookup_expr='icontains',
        label='Filtrar por categoría (nombre parcial)'
    )
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Filtrar por nombre (parcial)'
    )
    has_subproducts = django_filters.BooleanFilter(method="filter_has_subproducts", label="Solo productos con subproductos")

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        if data and 'code' in data and data['code'] != '':
            if not str(data['code']).isdigit():
                raise ValidationError({"code": f"'{data['code']}' no es un código válido. Debe contener solo números."})
        super().__init__(data, queryset, request=request, prefix=prefix)

    def filter_has_subproducts(self, queryset, name, value):
        if value is None:
            return queryset
        return queryset.annotate(
            _has_sps=Exists(Subproduct.objects.filter(parent_id=OuterRef("pk")))
        ).filter(_has_sps=value)

    class Meta:
        model = Product
        fields = ['status', 'code', 'category', 'name', 'has_subproducts']
