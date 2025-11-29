from django.apps import AppConfig


class OrdersConfig(AppConfig):
    name = "apps.orders"
    verbose_name = "Pedidos de clientes"

    def ready(self) -> None:
        # Punto de enganche para señales: reservas de stock, alertas SLA, etc.
        return super().ready()
