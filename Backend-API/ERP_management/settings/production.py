# settings/production.py
from .base import *  # noqa
import logging
import os
from pathlib import Path
from datetime import timedelta
import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from urllib.parse import urlparse

# ── BASE_DIR ───────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

ASGI_APPLICATION = "ERP_management.asgi.application"

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured("La variable SECRET_KEY no está definida en producción")

# Verifica y advierte si faltan variables de entorno críticas realmente usadas
critical_env_vars = [
    'SECRET_KEY',
    'DATABASE_URL',
    'REDIS_URL',
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_PRODUCT_BUCKET_NAME',
    'AWS_PROFILE_BUCKET_NAME',
    'AWS_INTAKE_BUCKET_NAME',
    'AWS_S3_ENDPOINT_URL',
]
for var in critical_env_vars:
    if not os.getenv(var):
        logging.warning(f"[settings] La variable de entorno '{var}' no está definida.")

DEBUG = False
ALLOWED_HOSTS = [h for h in os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',') if h]

# ── ESTÁTICOS (mínimos para evitar ImproperlyConfigured) ─────────────
# Aun si no servimos estáticos desde Django en prod, STATIC_URL debe existir
# Ubicación de collectstatic si decidieras ejecutarlo en tu pipeline
STATIC_ROOT = BASE_DIR.parent / 'staticfiles'

# ── CSP (Content Security Policy) ─────────────────────────────────────
# Permitimos conexiones al API/WS propios y al dominio del frontend
from urllib.parse import urlparse

def _to_origin(host: str) -> str:
    host = host.strip()
    if not host:
        return ''
    if host.startswith(('http://', 'https://')):
        return host
    return f"https://{host}"

def _to_ws(origin: str) -> str:
    try:
        p = urlparse(origin)
        scheme = 'wss' if p.scheme == 'https' else 'ws'
        return f"{scheme}://{p.netloc}"
    except Exception:
        return origin.replace('https://', 'wss://').replace('http://', 'ws://')
cors_origins = [o for o in os.getenv('DJANGO_CORS_ALLOWED_ORIGINS', '').split(',') if o]
csrf_origins = [o for o in os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if o]

origins_set = set()
for h in ALLOWED_HOSTS:
    o = _to_origin(h)
    if o:
        origins_set.add(o)
for o in cors_origins + csrf_origins:
    origins_set.add(o.strip())

ws_set = {_to_ws(o) for o in origins_set}

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC  = ("'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'")
CSP_STYLE_SRC   = ("'self'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net", "'unsafe-inline'")
CSP_IMG_SRC     = ("'self'", "data:", "https://cdn.jsdelivr.net")
CSP_CONNECT_SRC = tuple(["'self'"] + sorted(list(origins_set | ws_set)))

# ── BASE DE DATOS ──────────────────────────────────────────────
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ImproperlyConfigured("La variable DATABASE_URL no está definida en producción")
DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)}

# ── HTTPS Y SEGURIDAD ──────────────────────────────────────────
SECURE_PROXY_SSL_HEADER        = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT            = True
SESSION_COOKIE_SECURE          = True
CSRF_COOKIE_SECURE             = True
SESSION_COOKIE_HTTPONLY        = True
SECURE_HSTS_SECONDS            = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD            = True
# (opcional) detrás de proxy
USE_X_FORWARDED_HOST           = True

# ── CSRF Y CORS ────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = [o for o in os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if o]
CORS_ALLOWED_ORIGINS = [o for o in os.getenv('DJANGO_CORS_ALLOWED_ORIGINS', '').split(',') if o]
CORS_ALLOW_HEADERS    = [
    'authorization', 'content-type', 'accept', 'origin',
    'x-csrftoken', 'x-requested-with', 'x-api-key'
]
CORS_ALLOW_METHODS    = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
CORS_ALLOW_CREDENTIALS = True

    raise ImproperlyConfigured("La variable REDIS_URL no está definida en producción")

def _with_db(url: str, db: str) -> str:
    """
    Devuelve la misma URL de Redis con el path reemplazado por /{db}.
    Útil cuando Railway da un único REDIS_URL y queremos separar servicios por DB.
    """
    parsed = urlparse(url)
    netloc = parsed.netloc
    scheme = parsed.scheme
    return f"{scheme}://{netloc}/{db}"

# Separa URLs (por defecto en DBs distintas para aislar tráficos)
BROKER_URL  = os.getenv('CELERY_BROKER_URL',     _with_db(REDIS_URL, '0'))
RESULT_URL  = os.getenv('CELERY_RESULT_BACKEND', _with_db(REDIS_URL, '1'))
CHANNEL_URL = os.getenv('CHANNEL_REDIS_URL',     _with_db(REDIS_URL, '2'))
CACHE_URL   = os.getenv('CACHE_REDIS_URL',       _with_db(REDIS_URL, '3'))

# ✅ Channels (sin SSL/TLS): usar redis:// y NO pasar kwargs de SSL
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            # dict con address recomendado por channels_redis
            "hosts": [{"address": CHANNEL_URL}],
        },
    },
}

# Celery
CELERY_BROKER_URL        = BROKER_URL
CELERY_RESULT_BACKEND    = RESULT_URL
CELERY_ACCEPT_CONTENT    = ['json']
CELERY_TASK_SERIALIZER   = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE          = 'America/Argentina/Buenos_Aires'
CELERY_ENABLE_UTC        = False
CELERY_TASK_ALWAYS_EAGER = os.getenv("CELERY_TASK_ALWAYS_EAGER", "False") == "True"

# Cache (django-redis) — sin TLS
from .base import CACHE_TTL
_cache_options = {
    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
    'IGNORE_EXCEPTIONS': True,
}
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': CACHE_URL,          # asegurate que sea redis://...
        'TIMEOUT': CACHE_TTL,
        'OPTIONS': _cache_options,      # sin CONNECTION_POOL_KWARGS de SSL
        'KEY_PREFIX': 'inventory_prod',
    }
}

# ── S3 / MinIO ────────────────────────────────────────────────
AWS_ACCESS_KEY_ID       = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY   = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_ENDPOINT_URL     = os.getenv('AWS_S3_ENDPOINT_URL')  # p.ej. http://<privado>:9000
AWS_S3_REGION_NAME      = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
AWS_PRODUCT_BUCKET_NAME = os.getenv('AWS_PRODUCT_BUCKET_NAME')
AWS_PROFILE_BUCKET_NAME = os.getenv('AWS_PROFILE_BUCKET_NAME')
AWS_INTAKE_BUCKET_NAME  = os.getenv('AWS_INTAKE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN    = os.getenv('AWS_S3_CUSTOM_DOMAIN', None)

AWS_S3_ADDRESSING_STYLE  = 'path'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_SECURE_URLS       = True
AWS_S3_FILE_OVERWRITE    = False
AWS_DEFAULT_ACL          = None
AWS_QUERYSTRING_AUTH     = True

# URL pública (si usás MinIO/CloudFront)
# Preferimos MINIO_PUBLIC_ENDPOINT; si viene como placeholder (${...}) o vacío, caemos a AWS_S3_CUSTOM_DOMAIN o AWS_S3_ENDPOINT_URL.
minio_public = os.getenv('MINIO_PUBLIC_ENDPOINT')

# Normaliza (quita comillas envolventes) y detecta placeholders no resueltos
def _normalize_env(val: str | None) -> str | None:
    if val is None:
        return None
    s = str(val).strip().strip('"').strip("'")
    # Trata ${...} como no establecido
    if s.startswith('${') and s.endswith('}'):
        return None
    return s

minio_public = _normalize_env(minio_public)
if not minio_public:
    minio_public = _normalize_env(AWS_S3_CUSTOM_DOMAIN) or _normalize_env(AWS_S3_ENDPOINT_URL)

# Si no tiene esquema, prefijamos silenciosamente con https:// para evitar warnings ruidosos
if minio_public and not str(minio_public).startswith(('http://', 'https://')):
    minio_public = f'https://{minio_public}'

MINIO_PUBLIC_URL = minio_public

# ── JWT Simple ─────────────────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# ── LOGGING PRODUCCIÓN ─────────────────────────────────────────
from .base import WS_VERBOSE_LOG, ENABLE_INTAKE_S3
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '{levelname} {asctime} {name} {message}', 'style': '{'},
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'fmt': '%(levelname)s %(asctime)s %(name)s %(message)s'
        },
    },
    'handlers': {
        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'django-error.log',
            'formatter': 'json' if os.getenv('LOG_FORMAT', 'verbose') == 'json' else 'verbose',
        },
        'console_prod': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'json' if os.getenv('LOG_FORMAT', 'verbose') == 'json' else 'verbose',
        },
    },
    'loggers': {
        'django':      {'handlers': ['file_errors', 'console_prod'], 'level': 'INFO', 'propagate': False},
        'apps':        {'handlers': ['file_errors', 'console_prod'], 'level': 'INFO', 'propagate': False},
        'ws.auth':     {'handlers': ['console_prod'], 'level': 'DEBUG' if WS_VERBOSE_LOG else 'INFO', 'propagate': False},
        'ws.consumer': {'handlers': ['console_prod'], 'level': 'DEBUG' if WS_VERBOSE_LOG else 'WARNING', 'propagate': False},
        'ws.crud':     {'handlers': ['console_prod'], 'level': 'DEBUG' if WS_VERBOSE_LOG else 'WARNING', 'propagate': False},
        'ws.jwt':      {'handlers': ['console_prod'], 'level': 'DEBUG' if WS_VERBOSE_LOG else 'WARNING', 'propagate': False},
        'channels':    {'handlers': ['console_prod'], 'level': 'DEBUG' if WS_VERBOSE_LOG else 'WARNING', 'propagate': False},
    },
    'root': {'handlers': ['console_prod'], 'level': 'WARNING'},
}

# Warning tardío (production) si activado y sin bucket
if ENABLE_INTAKE_S3 and not AWS_INTAKE_BUCKET_NAME:
    import logging as _logging
    _logging.warning("[settings][prod] ENABLE_INTAKE_S3=True pero AWS_INTAKE_BUCKET_NAME no definido — uploads intake NO disponibles.")
