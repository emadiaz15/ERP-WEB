import os
import logging
from pathlib import Path

# Cargar .env si existe (útil en local; inofensivo en prod)
try:
    from dotenv import load_dotenv
    BASE_DIR = Path(__file__).resolve().parent.parent
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except Exception:
    # dotenv es opcional en prod
    pass

# Default a local si no viene seteado desde el entorno (Railway lo setea a production)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ERP_management.settings.local")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()

# Evitá loguear valores sensibles como REDIS_URL completa
logger = logging.getLogger(__name__)
logger.info("WSGI listo. DJANGO_SETTINGS_MODULE=%s | REDIS_URL configurado=%s",
            os.environ.get("DJANGO_SETTINGS_MODULE"),
            "sí" if os.getenv("REDIS_URL") else "no")
