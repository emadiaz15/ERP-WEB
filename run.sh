#!/usr/bin/env bash
set -e

# Script simple para levantar todo el ERP en Docker
# Uso: ./run.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Construir la imagen de la API si es necesario
echo "[run.sh] Building API image..."
docker compose build api

# Levantar servicios base
echo "[run.sh] Starting db and redis..."
docker compose up -d db redis

# Levantar API en foreground (autoreload activo)
echo "[run.sh] Starting API (logs attached)..."
docker compose up api
