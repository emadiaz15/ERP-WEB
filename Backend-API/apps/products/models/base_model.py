from django.conf import settings
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
	"""Modelo base con auditoría y soft delete reutilizable."""

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

	class Meta:
		abstract = True
		ordering = ["-created_at"]

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


__all__ = ["BaseModel"]
