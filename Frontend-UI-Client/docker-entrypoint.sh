#!/bin/sh
set -e

APP_DIR="/app"
NODE_MODULES_DIR="$APP_DIR/node_modules"

if [ ! -d "$NODE_MODULES_DIR" ] || [ -z "$(ls -A "$NODE_MODULES_DIR" 2>/dev/null)" ]; then
  echo "[entrypoint] Instalando dependencias npm dentro del contenedor..."
  npm install --legacy-peer-deps
else
  echo "[entrypoint] Dependencias ya instaladas, se reutilizan node_modules del volumen."
fi

exec "$@"
