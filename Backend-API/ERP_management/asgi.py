import os
from pathlib import Path
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
# from channels.auth import AuthMiddlewareStack  # ← quitado: pisaba scope["user"]

# Cargar .env local si existe (opcional)
try:
    from dotenv import load_dotenv
    BASE_DIR = Path(__file__).resolve().parent.parent
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except Exception:
    pass

# Respetar DJANGO_SETTINGS_MODULE del entorno; manage.py ya pone local por defecto

django_asgi_app = get_asgi_application()


# Rutas WS unificadas
from apps.notifications.routing import websocket_urlpatterns as notifications_ws  # noqa: E402
from apps.core.routing import websocket_urlpatterns as core_ws  # noqa: E402
from ERP_management.channels_jwt import JWTAuthMiddlewareStack  # noqa: E402

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddlewareStack(
            URLRouter(notifications_ws + core_ws)
        )
    ),
})
