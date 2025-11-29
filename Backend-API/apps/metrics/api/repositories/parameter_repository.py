from typing import Optional

from django.db import models

from apps.metrics.models import MetricParameter


class ParameterRepository:
    """Operaciones de acceso a datos para parametros de metricas."""

    @staticmethod
    def list_parameters(*, search: str | None = None) -> models.QuerySet:
        qs = MetricParameter.objects.filter(status=True)
        if search:
            qs = qs.filter(description__icontains=search)
        return qs.order_by("description")

    @staticmethod
    def get_parameter(parameter_id: int) -> Optional[MetricParameter]:
        return MetricParameter.objects.filter(pk=parameter_id, status=True).first()

    @staticmethod
    def create_parameter(**fields) -> MetricParameter:
        user = fields.pop("user", None)
        parameter = MetricParameter(**fields)
        parameter.save(user=user)
        return parameter

    @staticmethod
    def update_parameter(instance: MetricParameter, *, user=None, **fields) -> MetricParameter:
        changed = False
        for attr, value in fields.items():
            if hasattr(instance, attr) and getattr(instance, attr) != value:
                setattr(instance, attr, value)
                changed = True
        if changed:
            instance.save(user=user)
        return instance

    @staticmethod
    def soft_delete(instance: MetricParameter, *, user=None) -> MetricParameter:
        instance.delete(user=user)
        return instance
