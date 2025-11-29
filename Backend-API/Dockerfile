FROM python:3.11-slim

# 📁 Directorio de trabajo
WORKDIR /app

# 🔧 Paquetes del sistema necesarios (libs Pillow + Postgres client build)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev zlib1g-dev libpng-dev libtiff-dev libglib2.0-0 \
    libpq-dev gcc build-essential curl netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

# ⚡ PIP & wheels
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 📦 Dependencias Python (capa cacheable)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 📁 Código
COPY . /app

# 🔐 Entrypoint ejecutable
RUN chmod +x /app/entrypoint.sh

# 👤 Usuario no-root
ARG APP_UID=1000
ARG APP_GID=1000
RUN groupadd -g ${APP_GID} app && useradd -u ${APP_UID} -g app -M -d /app -s /bin/bash app \
 && chown -R app:app /app
USER app

# 🧠 Entorno básico
ENV PYTHONUNBUFFERED=1

# (Variables OCR eliminadas: procesamiento ahora lo hace LLM externo)

# 🌐 EXPOSE informativo (Railway usa $PORT)
EXPOSE 8080

# 🚀 Entrypoint: espera DB + migrate y luego ejecuta CMD
ENTRYPOINT ["/app/entrypoint.sh"]

# 🏁 Server ASGI con Daphne (respeta $PORT de Railway)
CMD ["sh","-lc","daphne -b 0.0.0.0 -p ${PORT:-8080} ERP_management.asgi:application"]
