#!/bin/sh
set -e

APP_ENV=${APP_ENV:-prod}
if [ -z "${DJANGO_SETTINGS_MODULE:-}" ]; then
  if [ "$APP_ENV" = "prod" ]; then
    export DJANGO_SETTINGS_MODULE=ERP_management.settings.production
  else
    export DJANGO_SETTINGS_MODULE=ERP_management.settings.local
  fi
fi

echo "🔍 APP_ENV=$APP_ENV | DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}"
# OCR/Tesseract feature desactivado: se removió chequeo para reducir ruido de logs

USE_SQLITE=${USE_SQLITE:-false}
# Controla si ejecutamos migrate (útil para evitarlo en workers)
RUN_MIGRATIONS=${RUN_MIGRATIONS:-true}
PORT=${PORT:-8080}

# Lista de apps para makemigrations (podés overridear con MIGRATE_APPS)
MIGRATE_APPS_DEFAULT="notifications users products stocks core cuts storages_client metrics manufacturing"
APPS="${MIGRATE_APPS:-$MIGRATE_APPS_DEFAULT}"
ENABLE_SYNCDB=${ENABLE_SYNCDB:-false}

# ⏳ Esperar a la DB si no usamos SQLite
if [ "${USE_SQLITE}" != "true" ]; then
  if [ -z "${DATABASE_URL:-}" ]; then
    echo "❌ Falta DATABASE_URL para conectarse a PostgreSQL"
    exit 1
  fi

  DB_HOST=$(python - <<'PY'
import os, urllib.parse as u
p=u.urlparse(os.environ.get("DATABASE_URL",""))
print(p.hostname or "")
PY
)
  DB_PORT=$(python - <<'PY'
import os, urllib.parse as u
p=u.urlparse(os.environ.get("DATABASE_URL",""))
print(p.port or 5432)
PY
)

  if [ -z "$DB_HOST" ]; then
    echo "❌ No pude extraer DB_HOST desde DATABASE_URL"
    exit 1
  fi

  echo "⏳ Esperando PostgreSQL en $DB_HOST:$DB_PORT..."
  until nc -z "$DB_HOST" "$DB_PORT"; do
    echo "⌛ Esperando conexión a PostgreSQL..."
    sleep 1
  done
  echo "✅ Conexión establecida con PostgreSQL"
else
  echo "🧪 Modo SQLite: no se espera DB"
fi

## � Desactivado AUTO_MAKEMIGRATIONS en runtime.
##    Ahora las migraciones deben versionarse y commitearse.
##    (Se eliminó ejecución condicional para evitar drift entre entornos.)
echo "ℹ️  AUTO_MAKEMIGRATIONS desactivado: se esperan migraciones ya en el repo."

# 🔧 Migraciones (opcional)
if [ "$RUN_MIGRATIONS" = "true" ]; then
  echo "🔧 Aplicando migraciones de base de datos..."
  # 1) Aplicar migraciones normales primero (evita errores de FK con --run-syncdb)
  python manage.py migrate --noinput

  # 2) En local, sincronizar apps sin migraciones luego de aplicar todas las migraciones
  if [ "$APP_ENV" != "prod" ] && [ "$ENABLE_SYNCDB" = "true" ]; then
    echo "🔄 Sincronizando apps sin migraciones (--run-syncdb)"
    python manage.py migrate --noinput --run-syncdb || true
  fi

  # Marcador para healthcheck de que las migraciones finalizaron
  touch /tmp/migrations_done || true
else
  echo "⏭️  RUN_MIGRATIONS=false: omitiendo migrate"
fi

# 🏁 Fallback por defecto: DAPHNE (ASGI)
if [ $# -eq 0 ]; then
  DEFAULT_CMD="daphne -b 0.0.0.0 -p ${PORT:-8080} ERP_management.asgi:application"
  echo "ℹ️  No se recibió CMD. Usando por defecto:"
  echo "    $DEFAULT_CMD"
  set -- sh -lc "$DEFAULT_CMD"
fi

# 🚀 Ejecutar el comando
echo "🚀 Lanzando: $*"
exec "$@"
