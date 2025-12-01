# settings/base.py
from pathlib import Path
from datetime import timedelta
import os
import logging

BASE_DIR = Path(__file__).resolve().parent.parent

BASE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
]
THIRD_APPS = [
    'rest_framework',
    'simple_history',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'channels',
    'django_celery_results',
    'django_celery_beat',
    'corsheaders',
    'csp',
    'sslserver',
    'storages',
    'django_filters',
]
LOCAL_APPS = [
    'apps.users',
    'apps.products.apps.ProductsConfig',
    'apps.core',
    'apps.cuts',
    'apps.stocks.apps.StocksConfig',      
    'apps.storages_client',
    'apps.locations.apps.LocationsConfig',
    'apps.metrics',
    'apps.notifications',
    'apps.manufacturing.apps.ManufacturingConfig',
    'apps.suppliers.apps.SuppliersConfig',
    'apps.purchases.apps.PurchasesConfig',
    'apps.expenses.apps.ExpensesConfig',
    'apps.sales.apps.SalesConfig',
    'apps.orders.apps.OrdersConfig',
    'apps.logistics.apps.LogisticsConfig',
    'apps.inventory_adjustments.apps.InventoryAdjustmentsConfig',
    'apps.customers.apps.CustomersConfig',
    'apps.financial.apps.FinancialConfig',
    'apps.payables.apps.PayablesConfig',
    'apps.treasury.apps.TreasuryConfig',
    'apps.manufacturing_pro.apps.ManufacturingProConfig',
    'apps.billing.apps.BillingConfig',
    'apps.accounting.apps.AccountingConfig',
    'apps.delivery_notes.apps.DeliveryNotesConfig',
]
INSTALLED_APPS = BASE_APPS + THIRD_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'csp.middleware.CSPMiddleware',
]

ROOT_URLCONF = 'ERP_management.urls'
WSGI_APPLICATION = 'ERP_management.wsgi.application'
ASGI_APPLICATION = "ERP_management.asgi.application"  # ✅ Channels

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTH_USER_MODEL = 'users.User'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Cordoba'
USE_I18N = True
USE_TZ = True

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}
SPECTACULAR_SETTINGS = {
    'TITLE': 'Inventory Management API',
    'DESCRIPTION': 'Documentación de la API para el Sistema de Gestión de Inventario',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SECURITY': [{'jwtAuth': []}],
    'COMPONENT_SPLIT_REQUEST': True,
    'COMPONENT_NO_READ_ONLY_REQUIRED': True,
    'COMPONENTS': {
        'securitySchemes': {
            'jwtAuth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'Use un token JWT con el prefijo Bearer',
            }
        }
    }
}

CACHE_TTL = 60 * 15  # 15 minutes default cache for API views

# Configuración de DEBUG
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"

# Niveles de log configurables por entorno
DJANGO_LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "INFO")
DJANGO_SQL_LOG_LEVEL = os.getenv("DJANGO_SQL_LOG_LEVEL", "WARNING")
WS_VERBOSE_LOG = os.getenv("WS_VERBOSE_LOG", "False") == "True"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {name} {message}',
            'style': '{'
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{'
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            # Campos claves para búsquedas; se pueden ampliar
            'fmt': '%(levelname)s %(asctime)s %(name)s %(message)s %(pathname)s %(lineno)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            # Permite cambiar a 'json' exportando LOG_FORMAT=json
            'formatter': 'json' if os.getenv('LOG_FORMAT', 'simple') == 'json' else 'simple'
        },
    },
    'root': {'handlers': ['console'], 'level': DJANGO_LOG_LEVEL},
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'ERROR', 'propagate': False},
        'django.db.backends': {
            'handlers': ['console'],
            'level': DJANGO_SQL_LOG_LEVEL,
            'propagate': False,
        },
        'apps': {'handlers': ['console'], 'level': 'DEBUG' if DEBUG else 'INFO', 'propagate': False},
        # ✅ logs dedicados para WS (nivel dinámico por flag)
    # Downgraded WS related loggers to ERROR to avoid noisy reconnect chatter unless WS_VERBOSE_LOG enabled
    'ws.auth': {'handlers': ['console'], 'level': 'DEBUG' if WS_VERBOSE_LOG else 'ERROR', 'propagate': False},
    'ws.consumer': {'handlers': ['console'], 'level': 'DEBUG' if WS_VERBOSE_LOG else 'ERROR', 'propagate': False},
    'channels': {'handlers': ['console'], 'level': 'DEBUG' if WS_VERBOSE_LOG else 'ERROR', 'propagate': False},
    }
}


def env_flag(name: str, default: str = "False") -> bool:
    """Conveniencia para interpretar variables booleanas."""
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


# Feature toggles
ENABLE_INTAKE_S3 = env_flag("ENABLE_INTAKE_S3")

# Helper para advertir si faltan variables de entorno críticas
def warn_if_env_missing(var_name):
    if not os.getenv(var_name):
        logging.warning(f"[settings] La variable de entorno '{var_name}' no está definida.")

# Warning condicional: solo si activamos funcionalidad intake S3
if ENABLE_INTAKE_S3 and not os.getenv('AWS_INTAKE_BUCKET_NAME'):
    logging.warning("[settings] ENABLE_INTAKE_S3=True pero falta AWS_INTAKE_BUCKET_NAME — se deshabilitará subida intake.")

# ✅ CSP para permitir WebSocket en dev
CSP_STYLE_SRC = ("'self'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net", "'unsafe-inline'")
CSP_SCRIPT_SRC = ("'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "https://cdn.jsdelivr.net", "data:")
CSP_CONNECT_SRC = (
    "'self'",
    "http://localhost:8000", "ws://localhost:8000",
    "http://127.0.0.1:8000", "ws://127.0.0.1:8000",
)

# Celery base (overridable)
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ALWAYS_EAGER = os.getenv("CELERY_TASK_ALWAYS_EAGER", "False") == "True"

# ✅ Channels base (hosts se setean en local/production)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": []},
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
APPEND_SLASH = False

DATABASE_ROUTERS: list[str] = []
MYSQL_RO_ENABLED: bool = False
