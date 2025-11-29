# apps/cuts/filters/cutting_order_filter.py
import django_filters
from django.core.exceptions import ValidationError
from apps.cuts.models.cutting_order_model import CuttingOrder  # ajusta import si difiere

class CuttingOrderFilter(django_filters.FilterSet):
    """
    Filtros comunes:
      - order_number: exacto (numérico) o prefix si preferís (cambia lookup)
      - customer: icontains
      - product_id: exacto
      - product_code: startswith
      - product_name: icontains
      - assigned_to: por id
      - assigned_username: icontains
      - workflow_status: exacto (pending|in_process|completed|cancelled)
      - created_from / created_to: por created_at (ISO)
      - assigned_to_me: boolean (usa request.user)
      - has_items: boolean (True => con items; False => sin items)
    """
    order_number = django_filters.NumberFilter(field_name="order_number", lookup_expr="exact")
    customer = django_filters.CharFilter(field_name="customer", lookup_expr="icontains")

    product_id = django_filters.NumberFilter(field_name="product_id", lookup_expr="exact")
    product_code = django_filters.CharFilter(field_name="product__code", lookup_expr="startswith")
    product_name = django_filters.CharFilter(field_name="product__name", lookup_expr="icontains")

    assigned_to = django_filters.NumberFilter(field_name="assigned_to_id", lookup_expr="exact")
    assigned_username = django_filters.CharFilter(field_name="assigned_to__username", lookup_expr="icontains")

    workflow_status = django_filters.CharFilter(field_name="workflow_status", lookup_expr="exact")

    created_from = django_filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_to   = django_filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="lte")

    assigned_to_me = django_filters.BooleanFilter(method="filter_assigned_to_me")
    has_items      = django_filters.BooleanFilter(method="filter_has_items")

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        # Validación amistosa para order_number si llega como string
        if data and "order_number" in data and data["order_number"] not in (None, "", []):
            s = str(data["order_number"])
            if not s.isdigit():
                raise ValidationError({"order_number": "Debe ser numérico."})
        super().__init__(data, queryset, request=request, prefix=prefix)

    def filter_assigned_to_me(self, queryset, name, value):
        if value is None:
            return queryset
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return queryset.none() if value else queryset
        return queryset.filter(assigned_to_id=user.id) if value else queryset.exclude(assigned_to_id=user.id)

    def filter_has_items(self, queryset, name, value):
        if value is None:
            return queryset
        # True: con items | False: sin items
        if value:
            return queryset.filter(items__isnull=False).distinct()
        return queryset.filter(items__isnull=True)

    class Meta:
        model = CuttingOrder
        fields = [
            "order_number",
            "customer",
            "product_id",
            "product_code",
            "product_name",
            "assigned_to",
            "assigned_username",
            "workflow_status",
            "created_from",
            "created_to",
            "assigned_to_me",
            "has_items",
            "status",  # si tu modelo lo tuviera
        ]
