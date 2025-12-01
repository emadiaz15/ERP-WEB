## ---------- Base Node LTS sobre Alpine ----------
FROM node:22-alpine AS base

# Preparar /app con dueño node
WORKDIR /app
RUN apk add --no-cache libc6-compat curl \
 && mkdir -p /app \
 && chown -R node:node /app

USER node

## ---------- Etapa de dependencias ----------
FROM base AS deps
COPY --chown=node:node package*.json ./
# npm install dentro de la imagen para evitar instalaciones locales
RUN npm install --legacy-peer-deps

## ---------- Etapa de desarrollo (con HMR) ----------
FROM base AS development
ENV NODE_ENV=development
ENV VITE_DEBUG=true

# Copiar dependencias
COPY --from=deps /app/node_modules /app/node_modules
COPY --chown=node:node . .

# EntryPoint que asegura instalación de dependencias cuando el volumen está vacío
COPY --chown=node:node docker-entrypoint.sh /usr/local/bin/frontend-entrypoint.sh
RUN chmod +x /usr/local/bin/frontend-entrypoint.sh

# Exponer puerto Vite dev server
EXPOSE 5173

# Healthcheck para desarrollo
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD curl -f http://localhost:5173/ || exit 1

# Comando de desarrollo con HMR
ENTRYPOINT ["/usr/local/bin/frontend-entrypoint.sh"]
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

## ---------- Etapa de build (producción) ----------
FROM base AS build
COPY --chown=node:node package*.json ./
COPY --from=deps /app/node_modules /app/node_modules
COPY --chown=node:node . .

# Variables de build (desde docker-compose)
ARG VITE_API_BASE_URL
ARG VITE_WS_URL_NOTIFICATIONS
ARG VITE_WS_URL_CRUD_EVENTS
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL:-}
ENV VITE_WS_URL_NOTIFICATIONS=${VITE_WS_URL_NOTIFICATIONS:-}
ENV VITE_WS_URL_CRUD_EVENTS=${VITE_WS_URL_CRUD_EVENTS:-}

# Build de producción
RUN npm run build

## ---------- Etapa final (runtime) ----------
FROM base AS runtime
ENV NODE_ENV=production
ENV APP_MODE=prod
ENV PORT=3000

# Copiar dependencias y build
COPY --from=deps /app/node_modules /app/node_modules
COPY --chown=node:node package*.json ./
COPY --from=build /app/dist /app/dist

# Exponer puerto preview
EXPOSE 3000

# Healthcheck para producción
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD curl -f http://localhost:3000/ || exit 1

# Comando preview (sirve dist/)
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]
