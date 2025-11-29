from django.apps import AppConfig


class ManufacturingProConfig(AppConfig):
    name = "apps.manufacturing_pro"
    verbose_name = "Manufactura avanzada"

    def ready(self) -> None:
        # Señales futuras: consumos automáticos, alertas de procesos externos, etc.
        return super().ready()
