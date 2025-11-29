from django.apps import AppConfig


class FinancialConfig(AppConfig):
    name = "apps.financial"
    verbose_name = "Financiero"

    def ready(self) -> None:
        # Señales se conectarán en futuros incrementos (ledger postings, etc.).
        return super().ready()
