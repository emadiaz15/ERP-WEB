# apps/stocks/apps.py
from django.apps import AppConfig

class StocksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.stocks"

    def ready(self):
        import apps.stocks.signals  # noqa: F401
