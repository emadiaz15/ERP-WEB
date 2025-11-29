from django.apps import AppConfig


class LogisticsConfig(AppConfig):
    name = "apps.logistics"
    verbose_name = "Logística y transportes"

    def ready(self) -> None:
        # Aquí conectaremos señales para tracking y conciliaciones.
        return super().ready()
