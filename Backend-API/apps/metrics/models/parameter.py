from django.conf import settings
from django.db import models
from django.utils import timezone


class MetricParameter(models.Model):
    """Parametro configurable proveniente de la tabla legacy ``parametros``."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    modified_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Modificación")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Eliminación")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_created",
        null=True,
        blank=True,
        verbose_name="Creado por",
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_modified",
        null=True,
        blank=True,
        verbose_name="Modificado por",
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_deleted",
        null=True,
        blank=True,
        verbose_name="Eliminado por",
    )

    status = models.BooleanField(default=True, verbose_name="Activo")

    legacy_code = models.IntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name="Codigo legacy",
        help_text="Valor de param_codi en el sistema legacy.",
    )
    description = models.CharField(
        max_length=255,
        verbose_name="Descripcion",
        help_text="Descripcion del parametro (param_desc).",
    )
    amount_value = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Valor numerico",
        help_text="Importe numerico asociado (param_impo).",
    )
    date_value = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha",
        help_text="Fecha almacenada en param_fec.",
    )
    datetime_value = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha y hora",
        help_text="Fecha y hora almacenadas en param_fechora.",
    )

    class Meta:
        verbose_name = "Parametro de metricas"
        verbose_name_plural = "Parametros de metricas"
        ordering = ["description"]
        indexes = [
            models.Index(fields=["legacy_code"]),
            models.Index(fields=["description"]),
        ]

    def __str__(self) -> str:
        return self.description

    def save(self, *args, **kwargs):
        """Actualiza campos de auditoría y delega el guardado real."""
        user = kwargs.pop("user", None)
        is_new = self.pk is None

        if is_new and user:
            self.created_by = user
        elif not is_new:
            self.modified_at = timezone.now()
            if user:
                self.modified_by = user

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Aplica soft delete preservando auditoría."""
        user = kwargs.pop("user", None)
        self.status = False
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user

        super().save(*args, update_fields=["status", "deleted_at", "deleted_by"], **kwargs)
