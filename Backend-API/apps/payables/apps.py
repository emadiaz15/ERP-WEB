from django.apps import AppConfig


class PayablesConfig(AppConfig):
    name = "apps.payables"
    verbose_name = "Cuentas por pagar"

    def ready(self) -> None:
        # Señales futuras para autoposteo ledger y retenciones.
        return super().ready()
