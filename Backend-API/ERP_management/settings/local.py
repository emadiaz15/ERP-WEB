# settings/local.py
from .base import *  # noqa

import os
from dotenv import load_dotenv
from datetime import timedelta
from pathlib import Path
import dj_database_url

# Verifica y advierte si faltan variables de entorno críticas realmente usadas
critical_env_vars = [
    'SECRET_KEY',
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_PRODUCT_BUCKET_NAME',
    'AWS_PROFILE_BUCKET_NAME',
    'AWS_S3_ENDPOINT_URL',
    'MINIO_PUBLIC_URL',
    'REDIS_HOST',
    'REDIS_PORT',
]
for var in critical_env_vars:
    warn_if_env_missing(var)


BASE_DIR = Path(__file__).resolve().parent.parent

# ── VARIABLES DE ENTORNO LOCAL ────────────────────────────────
load_dotenv(BASE_DIR.parent / '.env.local')

# ── SEGURIDAD ─────────────────────────────────────────────────
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-for-local-dev-only')
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = ['*']

# DB sqlite
DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL', 'postgres://inventory_user:inventory_pass@db:5432/inventory_db'))
}

MYSQL_RO_ENABLED = False

# ── ESTÁTICOS Y MEDIA ──────────────────────────────────────────
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.parent / 'media'

# S3 / MinIO local
DEFAULT_FILE_STORAGE    = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID       = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY   = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_PRODUCT_BUCKET_NAME = os.getenv('AWS_PRODUCT_BUCKET_NAME')
AWS_PROFILE_BUCKET_NAME = os.getenv('AWS_PROFILE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL     = os.getenv('AWS_S3_ENDPOINT_URL')
AWS_S3_REGION_NAME      = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_FILE_OVERWRITE   = False
AWS_DEFAULT_ACL         = None
AWS_QUERYSTRING_AUTH    = False

# Forzar HTTP y dominio en dev
AWS_S3_SECURE_URLS    = False
AWS_S3_URL_PROTOCOL   = 'http:'
minio_public = os.getenv('MINIO_PUBLIC_URL', AWS_S3_ENDPOINT_URL)
if minio_public and not minio_public.startswith(('http://', 'https://')):
    minio_public = f'http://{minio_public}'

AWS_S3_CUSTOM_DOMAIN = minio_public
MINIO_PUBLIC_URL     = AWS_S3_CUSTOM_DOMAIN

# Validación de dominio S3 solo después de definir AWS_S3_CUSTOM_DOMAIN
if AWS_S3_CUSTOM_DOMAIN and not AWS_S3_CUSTOM_DOMAIN.startswith(('http://', 'https://')):
    import logging
    logging.warning("[settings] AWS_S3_CUSTOM_DOMAIN no tiene un esquema http/https: %s", AWS_S3_CUSTOM_DOMAIN)

# ── Añadido para forzar path-style, firma v4 y desactivar SSL ─────────
AWS_S3_ADDRESSING_STYLE   = 'path'
AWS_S3_SIGNATURE_VERSION  = 's3v4'
AWS_S3_USE_SSL            = False
AWS_S3_VERIFY             = False

# CORS
CORS_ALLOWED_ORIGINS  = [o for o in os.getenv("DJANGO_CORS_ALLOWED_ORIGINS", "").split(",") if o]
CORS_ALLOW_HEADERS     = ['authorization','content-type','accept','origin','x-csrftoken','x-requested-with','x-api-key']
CORS_ALLOW_METHODS     = ['GET','POST','PUT','PATCH','DELETE','OPTIONS']
CORS_ALLOW_CREDENTIALS = True

# ── EMAIL LOCAL ───────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# JWT
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

# Redis & Celery
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')

# Separar DBs por servicio
REDIS_BROKER_DB   = os.getenv('REDIS_BROKER_DB',   '0')
REDIS_RESULT_DB   = os.getenv('REDIS_RESULT_DB',   '1')
REDIS_CHANNEL_DB  = os.getenv('REDIS_CHANNEL_DB',  '2')
REDIS_CACHE_DB    = os.getenv('REDIS_CACHE_DB',    '3')

REDIS_BROKER_URL  = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BROKER_DB}'
REDIS_RESULT_URL  = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULT_DB}'
REDIS_CHANNEL_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CHANNEL_DB}'
REDIS_CACHE_URL   = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}'

# ✅ Channels (Redis local)
_is_tls = REDIS_CHANNEL_URL.startswith("rediss://")
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [{"address": REDIS_CHANNEL_URL, "ssl": True}] if _is_tls else [REDIS_CHANNEL_URL],
        },
    }
}

# Celery
CELERY_BROKER_URL        = REDIS_BROKER_URL
CELERY_RESULT_BACKEND    = REDIS_RESULT_URL
CELERY_TASK_ALWAYS_EAGER = os.getenv("CELERY_TASK_ALWAYS_EAGER", "False") == "True"

# Cache (django-redis)
from .base import CACHE_TTL  # noqa
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_CACHE_URL,
        "TIMEOUT": CACHE_TTL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        },
        "KEY_PREFIX": "inventory_local",
    }
}

CSP_CONNECT_SRC = (
    "'self'",
    "http://localhost:8000", "ws://localhost:8000",
    "http://127.0.0.1:8000", "ws://127.0.0.1:8000",
    "ws://localhost:5173",   # HMR de Vite (opcional pero útil)
)