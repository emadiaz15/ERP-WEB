from django.contrib import admin

from .models import MetricParameter


@admin.register(MetricParameter)
class MetricParameterAdmin(admin.ModelAdmin):
	list_display = ("description", "legacy_code", "amount_value", "date_value", "datetime_value", "status")
	search_fields = ("description", "legacy_code")
	list_filter = ("status",)
