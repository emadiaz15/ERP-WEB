# CLAUDE.md

Este archivo proporciona orientación a Claude Code (claude.ai/code) al trabajar con código en este repositorio.

## Descripción del Proyecto

Este es un sistema ERP (Enterprise Resource Planning) full-stack para gestión de inventario, especializado en administración de productos, órdenes de corte, seguimiento de stock y procesamiento de pedidos. El sistema consta de:

- **Backend-API**: API REST con Django REST Framework y soporte WebSocket (Django Channels)
- **Frontend-UI-Client**: SPA React + Vite con TanStack Query para manejo de datos

El sistema gestiona flujos de trabajo complejos incluyendo ingesta de pedidos basada en OCR desde WhatsApp, generación automática de órdenes de corte, notificaciones en tiempo real y seguimiento integral de inventario a través de múltiples módulos.

## Convenciones Importantes

**REGLA DE ORO DEL PROYECTO**:
- Todo el código debe escribirse en **INGLÉS** (nombres de variables, funciones, clases, etc.)
- Todos los comentarios deben escribirse en **ESPAÑOL**
- Este archivo CLAUDE.md debe estar siempre en **ESPAÑOL**

Ejemplo:
```python
# Obtener todos los productos activos con sus categorías
def get_active_products_with_categories():
    # Filtrar solo productos con status=True
    return Product.objects.filter(status=True).select_related('category')
```

## Estructura del Repositorio

```
ERP-Web/
├── Backend-API/          # Backend Django
│   ├── ERP_management/   # Configuración principal del proyecto Django
│   ├── apps/             # Aplicaciones Django (arquitectura modular)
│   └── manage.py
└── Frontend-UI-Client/   # Frontend React
    ├── src/
    └── vite.config.js
```

## Comandos Comunes de Desarrollo

### Backend (Django)

```bash
cd Backend-API

# Ejecutar servidor de desarrollo
python manage.py runserver

# Ejecutar tests (usando PyTest o Django test runner)
DJANGO_SETTINGS_MODULE=ERP_management.settings.test python manage.py test
DJANGO_SETTINGS_MODULE=ERP_management.settings.test python -m pytest -q

# Aplicar migraciones
python manage.py migrate

# Crear migraciones
python manage.py makemigrations

# Crear superusuario
python manage.py createsuperuser --username admin --email admin@example.com

# Django shell
python manage.py shell_plus

# Ver estado de migraciones
python manage.py showmigrations

# Aplicar migraciones de una app específica
python manage.py migrate <app_name>
```

**Módulos de Settings**: El proyecto Django usa configuración dividida:
- `ERP_management.settings.local` - Desarrollo (por defecto)
- `ERP_management.settings.production` - Producción
- `ERP_management.settings.test` - Testing

Se configura mediante la variable de entorno `DJANGO_SETTINGS_MODULE`.

### Frontend (React + Vite)

```bash
cd Frontend-UI-Client

# Instalar dependencias
npm install

# Ejecutar servidor de desarrollo (puerto por defecto 5173)
npm run dev

# Build para producción
npm run build

# Preview del build de producción
npm run preview

# Ejecutar linting
npm run lint

# Ejecutar tests
npm test
```

## Arquitectura por Módulos (Backend)

**Nombre del Proyecto**: El proyecto Django se llama `ERP_management` (no `inventory_management` como se menciona en algunos docs).

### `core`
- Modelos base y mixins compartidos
- Paginación custom en `apps.core.pagination`
- Consumers WebSocket para eventos CRUD:
   - Canal principal autenticado: `ws/crud-events`
   - Consumer: `apps.core.consumers.crud_event_consumer.CrudEventConsumer`
- Configuración y utilidades transversales (helpers comunes)

### `users`
- Autenticación y gestión de usuarios (`apps.users.User` como `AUTH_USER_MODEL`)
- Roles de usuario (`ADMIN`, `MANAGER`, `SALES`, `BILLING`, `TRAVELER`, `OPERATOR`, `WAREHOUSE`, `READONLY`)
- Endpoints de autenticación:
   - `POST /api/v1/users/login/`
   - `POST /api/v1/users/register/`
   - `POST /api/v1/users/logout/`
- Autenticación basada en JWT vía `djangorestframework-simplejwt` (con blacklist habilitado)

### `products`
- Productos, categorías, subproductos
- Imágenes y archivos adjuntos asociados a productos/subproductos (via MinIO/S3)
- Relaciones producto–proveedor y producto–cliente
- Signals para manejo de imágenes y relaciones derivadas

### `stocks`
- Modelos de stock para productos y subproductos
- Registro de eventos de inventario (ingresos, egresos, ajustes)
- Integración con `purchases`, `sales`, `delivery_notes`, `inventory_adjustments` y `manufacturing`

### `cuts`
- Gestión de órdenes de corte y su workflow (`flow_status`)
- Integración con productos que tienen subproductos (`has_subproducts=True`)
- Puede generar órdenes en base a pedidos/ventas

### `notifications`
- Sistema de notificaciones en tiempo real
- Integración con WebSocket (envío de eventos por usuario/rol)
- Cache de notificaciones con TTL corto

### `purchases`
- Órdenes de compra y sus líneas
- `PurchaseReceipt` y recepción de mercadería (total/parcial)
- Actualización de stock disponible a través de servicios de `stocks`

### `sales`
- Presupuestos (quotes) y pedidos de venta
- Validación de stock disponible (reservado vs libre)
- Reserva de stock al confirmar pedidos
- Integración con `billing` y `delivery_notes`

### `customers` y `suppliers`
- Gestión de clientes, proveedores y sus datos fiscales/comerciales
- Ubicaciones y descripciones de productos específicas por cliente

### `expenses`
- Seguimiento de gastos y pagos indirectos
- Integración con `treasury` y `accounting` para imputaciones contables

### `manufacturing` y `manufacturing_pro`
- Listas de materiales (BOM)
- Órdenes de trabajo y procesos de manufactura
- Consumo de insumos y producción de productos terminados

### `orders` y `logistics`
- Gestión de pedidos y transporte
- Transportistas, envíos y cuentas logísticas
- Integración con `delivery_notes` y `sales`

### `inventory_adjustments`
- Conteos de inventario físico
- Ajustes de stock manuales con trazabilidad

### `treasury`
- Bancos, cuentas, depósitos y cobranzas
- Métodos de pago, retenciones y percepciones aplicadas al cobro

### `financial` y `payables`
- Gestión de libro mayor y finanzas
- Cuentas por pagar, vencimientos y estados de cuenta

### `billing`
- Documentos de facturación (facturas, notas de crédito/débito)
- Cálculo de impuestos y retenciones
- Flags de configuración de tipos de comprobante, incluyendo `mover_stock`

### `accounting`
- Asientos contables automáticos y manuales
- Conciliación con módulos de ventas, compras, tesorería y gastos

### `delivery_notes`
- Gestión de remitos electrónicos
- Configuración de tipos de remito con flag `mover_stock`
- Integración logística con `sales`, `orders` y `stocks`

### `locations`
- Países, provincias, localidades, códigos postales y zonas
- Datos geográficos compartidos por clientes, proveedores y sucursales

### `metrics`
- Métricas del sistema y parámetros configurables
- Soporte para dashboards y KPIs operativos

### Patrón Repository–Service–View (todas las apps)
- `api/repositories/`: Capa de acceso a datos y consultas complejas
- `api/serializers/`: Serializers de DRF
- `api/views/`: ViewSets y vistas de API
- `services/`: Lógica de negocio y orquestación de flujos
- `filters/`: Clases de `django-filter`
- `docs/`: Esquemas de API (`drf-spectacular`)
- `models/`: Modelos Django
- `tasks.py`: Tareas Celery (si está presente)
- `routing.py`: Routing WebSocket (si está presente)

### Infraestructura Transversal Backend
- **Tareas en Background**:
   - Celery con broker Redis
   - `django-celery-beat` para tareas programadas
   - `django-celery-results` para resultados persistentes
- **Almacenamiento de Archivos**:
   - Integración MinIO/S3 vía `django-storages` (boto3)
   - Buckets diferenciados para productos/subproductos y perfiles de usuario
   - URLs presignadas para uploads/downloads
- **Caching**:
   - Backend de cache en Redis vía `django-redis`
   - Decoradores de cache en `utils/cache_decorators.py`
   - Gestión de claves en `utils/cache_keys.py`
   - Patrones de invalidación en `utils/cache_invalidation.py`

## Arquitectura del Frontend por Módulos

### Stack y Estructura General
- React 18 con Vite
- TanStack Query para estado del servidor
- Zustand para estado local
- React Router v6 para routing
- React Hook Form + Yup para formularios
- Axios como cliente HTTP
- Socket.io-client para WebSockets
- Tailwind CSS para estilos y Framer Motion para animaciones

Estructura base:
- `src/features/`: Organización basada en features (products, categories, users, cutting orders, notifications, etc.)
   - Cada feature tiene: `components/`, `pages/`, `services/`, `router/`
- `src/components/`: Componentes UI compartidos (common, ui, kanban)
- `src/hooks/`: Hooks React reutilizables
- `src/api/`: Configuración de clientes API (`clients.js`)
- `src/context/`: Contextos globales (por ejemplo, `DataPrefetchContext`, `NotificationsSocketBridge`)

### Comunicación con API
- URL base configurada con `VITE_API_BASE_URL`
- En desarrollo, proxy de Vite para `/api` y `/ws` (ver `vite.config.js`)
- En producción, conexión directa al backend en `/api/v1/`
- `src/api/clients.js` se encarga de inyectar el token JWT y manejar errores 401

### Tiempo Real, WebSockets y Notificaciones
- Conexión WebSocket a `/ws/crud-events`
- Eventos CRUD recibidos se traducen en invalidaciones de cache de TanStack Query o en patches in-memory
- Componente `NotificationsSocketBridge` conecta la capa de WebSocket con el árbol de React
- El frontend no implementa lógica de autorización: solo muestra lo que el backend envía

### Patrones Frontend Clave
- **Infinite Scroll**: Hook `useInfinitePageQuery` (envuelve `useInfiniteQuery`) para listas paginadas.
- **Modales CRUD**: Hook `useEntityModal` para flujos create/edit/view/delete.
- **Formularios**: React Hook Form + Yup; componentes en `components/ui/form/`.
- **Notificaciones de Éxito**: Hook `useSuccess` para toasts estándar.
- **Sesión**: Hook `useSession` maneja tokens JWT, expiración y logout.

## Variables de Entorno

### Backend

Variables clave (configurar en `.env` o environment):
- `DJANGO_SETTINGS_MODULE`: Módulo de settings (por defecto: `ERP_management.settings.local`)
- `SECRET_KEY`: Secret key de Django
- `DATABASE_URL`: String de conexión PostgreSQL
- `ALLOWED_HOSTS`: Hosts permitidos separados por comas
- `CORS_ALLOWED_ORIGINS`: URLs del frontend para CORS
- `REDIS_URL` / `CELERY_BROKER_URL`: Conexión Redis para Celery y caching
- `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`: Almacenamiento S3/MinIO
- `OCR_LANG`, `OCR_PSM`, `OCR_OEM`: Parámetros Tesseract OCR (si módulo OCR está activo)

### Frontend

- `VITE_API_BASE_URL`: URL base de la API del backend (opcional en dev, requerido en prod)
- `VITE_API_TARGET`: Target del proxy para desarrollo (por defecto: `http://localhost:8000`)
- `PORT`: Puerto del servidor dev (por defecto: 5173)

## Estructura de API

Todas las APIs del backend siguen el patrón: `/api/v1/<recurso>/`

**Autenticación**:
- `POST /api/v1/users/login/` - Login (retorna tokens JWT)
- `POST /api/v1/users/register/` - Registro
- `POST /api/v1/users/logout/` - Logout

**Patrones Comunes**:
- Listar: `GET /api/v1/<recurso>/`
- Crear: `POST /api/v1/<recurso>/create/`
- Obtener: `GET /api/v1/<recurso>/<id>/`
- Actualizar: `PUT /api/v1/<recurso>/<id>/`
- Actualización Parcial: `PATCH /api/v1/<recurso>/<id>/`
- Eliminar: `DELETE /api/v1/<recurso>/<id>/`

**Operaciones de Archivos**:
- Upload: `POST /api/v1/products/<id>/files/upload/`
- Download: `GET /api/v1/products/<id>/files/<file_id>/download/`
- Delete: `DELETE /api/v1/products/<id>/files/<file_id>/delete/`

**Notificaciones**:
- Summary: `GET /api/v1/notifications/summary/` (combina lista + contador no leídas)
- Marcar como leída: `PATCH /api/v1/notifications/<id>/mark-read/`

## Base de Datos

**Base de Datos Principal**: PostgreSQL
**ORM**: Django ORM con migraciones

Para queries complejas, los repositories usan `.select_related()` y `.prefetch_related()` para optimizar acceso a base de datos.

## Lógica de Negocio Clave

**Órdenes de Corte**:
- Creadas desde productos que tienen subproductos (`has_subproducts=True`)
- Pueden auto-generarse vía signals cuando pedidos coinciden con productos elegibles
- Estados de workflow rastreados vía campo `flow_status`

**Gestión de Stock**:
- Modelos separados para stock de productos y stock de subproductos
- Eventos de stock rastrean todos los movimientos de inventario con timestamps
- Ajustes de stock a través del módulo inventory_adjustments

**Jerarquía de Productos**:
- Product → Subproduct (uno-a-muchos)
- Productos pueden tener categorías, proveedores, clientes
- Imágenes almacenadas por separado (modelos ProductImage, SubproductImage)

**Integración Multi-módulo**:
- Órdenes de venta pueden generar envíos y facturas
- Órdenes de compra generan recibos y afectan stock
- Órdenes de manufactura consumen materiales y producen productos

**Ciclo de Producto y Control de Stock**:
- **Ingreso de mercadería**: Toda compra genera un `PurchaseReceipt` asociado; cada línea indica cantidad recibida y si la recepción es total o parcial. Solo las cantidades efectivamente recepcionadas incrementan el stock disponible.
- **Disponibilidad en inventario**: Una vez confirmada la recepción, los movimientos se registran en servicios de `stocks` para reflejar los niveles por producto y subproducto. Ajustes posteriores usan el módulo `inventory_adjustments`.
- **Presupuestos (Quotes)**: La generación de presupuestos debe consultar siempre stock disponible (reservado vs. libre) para informar si hay cobertura; no bloquea stock pero expone alertas cuando no hay disponibilidad.
- **Pedidos de venta**: Al confirmar un pedido, se valida stock disponible. El sistema puede reservar cantidades (estado `reserved`) hasta que se facture o remita, evitando sobreventa.
- **Facturación sin movimiento de stock**: Se permite emitir facturas con `mover_stock=false` para casos de cobros anticipados u operaciones financieras. No se descuenta inventario hasta que exista un documento logístico (remito) o una factura posterior con `mover_stock=true`.
- **Remitos y descuentos finales**: El remito confirma la salida física. Cuando `mover_stock=true`, descuenta inventario y libera reservas. Si la factura ya movió stock, el remito debe emitirse con `mover_stock=false` para evitar doble impacto.
- **Regla de exclusión**: En cualquier flujo, solo uno de los documentos (factura o remito) puede mover stock. La lógica de negocio debe validar que si un comprobante ya actualizó inventario, el relacionado ajuste automáticamente `mover_stock` a `false`.

**Configuración `mover_stock` en Comprobantes**:
- Tanto tipos de factura como de remito deben incluir un flag `mover_stock` configurable (por ejemplo, en modelos de tipo de documento de `billing` y `delivery_notes`).
- El flag controla la generación de eventos de stock: facturas y remitos consultan su propio valor de `mover_stock` y crean o no movimientos en los servicios de `stocks`.
- Reglas de negocio deben impedir emitir dos comprobantes vinculados con `mover_stock=true` simultáneamente o, a la inversa, dos con `mover_stock=false` cuando una salida física ya fue registrada.

## Cumplimiento Fiscal (Argentina)

### Módulos y Responsabilidades
- `billing`: Emisión de comprobantes electrónicos (facturas, notas de crédito/débito) y cálculo de impuestos.
- `delivery_notes`: Generación y trazabilidad de remitos electrónicos.
- `accounting` y `financial`: Registro contable de comprobantes y generación de asientos automáticos.
- `treasury`: Gestión de cobranzas, retenciones y percepciones aplicables.

### Integración con AFIP (RG 2485, RG 4290 y normativas vigentes 2025)
- Servicios web usados: `wsfev1` (facturación), `wsremit` (remitos) y `ws_sr_padron_a4` (consulta de padrón).
- Flujo general: autenticación con `WSAA`, obtención de `Cuit`, `Sign` y `Token`, generación de comprobante, solicitud de CAE/CAEA y almacenamiento del resultado.
- Validaciones obligatorias: CUIT del receptor, condición frente al IVA, punto de venta habilitado, tope de montos según categoría.
- Reintentos y cola: usar Celery (`billing.tasks`) para reprocesar rechazados y tareas nocturnas.

### Libros IVA y Reportes Fiscales
- `billing.services.vat_books`: Genera Libro IVA Ventas/Compras en formatos PDF y CSV homologados.
- Exportaciones periódicas: cron Celery (`django-celery-beat`) para cierres mensuales; almacenar evidencia en MinIO bajo prefijo `fiscal/`.
- Conciliación contable: los asientos generados se validan contra plan de cuentas en `accounting.services.ledger_service`.

### Retenciones y Percepciones Provinciales
- Tablas de alícuotas ARBA/AGIP en `billing.models.tax` y `treasury.models.retention`.
- Servicios: `billing.services.retention_calculator` aplica percepciones según padrón actualizado; actualizar padrón vía tarea programada que consume los CSV oficiales.
- Debe registrarse el agente de recaudación actual en `settings` (`FISCAL_AGENT_CODE`).

### Variables de Entorno Relevantes
- `AFIP_CERT_PATH`, `AFIP_KEY_PATH`: Certificados X.509 productivo/homologación.
- `AFIP_ENV`: `production` o `testing` para seleccionar WSAA.
- `AFIP_TAXPAYER_CUIT`: CUIT emisor.
- `FISCAL_TIMEZONE`: Zona horaria para cortes diarios (ejemplo `America/Argentina/Buenos_Aires`).
- `VAT_BOOK_BUCKET`: Bucket S3/MinIO para respaldos fiscales.

### Checklist Normativo (2025)
- Factura electrónica obligatoria para todas las categorías: soportar tipos A, B, C, M y E.
- Remito electrónico exigible (RG 1415 y complementarias): generar CAI y QR.
- Registro de percepciones IVA/Ingresos Brutos según RG 2109 y resoluciones provinciales vigentes.
- Declaración libro IVA Digital: exportar archivo compatible con presentación mensual.
- Guarda cronológica de comprobantes por 10 años en almacenamiento inmutable (activar `MINIO_OBJECT_LOCK` si está disponible).

## Flujo de Trabajo de Desarrollo

1. **Cambios en Backend**:
   - Crear/modificar modelos en `apps/<app>/models/`
   - Generar migraciones: `python manage.py makemigrations <app>`
   - Aplicar: `python manage.py migrate`
   - Agregar/actualizar serializers en `api/serializers/`
   - Implementar lógica de negocio en `services/`
   - Crear/actualizar vistas en `api/views/`
   - Registrar URLs en `api/urls.py`
   - Agregar tests en `tests.py` o `tests_*.py`

2. **Cambios en Frontend**:
   - Agregar/modificar componentes en `src/features/<feature>/components/`
   - Crear páginas en `src/features/<feature>/pages/`
   - Definir funciones de servicio API en `src/features/<feature>/services/`
   - Usar hooks de TanStack Query para data fetching
   - Registrar rutas en `src/features/<feature>/router/`
   - Agregar tests en `src/__tests__/features/<feature>/`

3. **Testing**:
   - Backend: Ejecutar tests con `pytest` o `python manage.py test`
   - Frontend: Ejecutar `npm test`
   - Verificar linting: `npm run lint` (frontend)

4. **Deployment**:
   - Backend: Usar gunicorn + uvicorn para soporte ASGI
   - Frontend: Build con `npm run build`, servir directorio `dist/`
   - Asegurar que variables de entorno estén configuradas correctamente
   - Ejecutar migraciones antes de deployar nuevo código del backend
   - Ver instrucciones detalladas de deployment en Backend-API/README.md (Docker, Postgres, estrategias de rollback)

## Permisos y Roles

- **Admin**: Acceso total al sistema, gestión de usuarios, configuración global y operaciones críticas.
- **Manager (Gerente)**: Control sobre módulos operativos (ventas, compras, logística), aprobación de transacciones clave.
- **Sales (Vendedor)**: Gestión de oportunidades y pedidos de venta, acceso a información comercial y reportes asociados.
- **Billing (Facturación)**: Emisión de facturas, notas de crédito/débito y gestión de documentación fiscal.
- **Traveler (Viajante)**: Acceso móvil a cartera de clientes, toma de pedidos y seguimiento de entregas en ruta.
- **Operator (Operario)**: Ejecución de órdenes de corte, actualizaciones de estado y registro de avances de producción.
- **Warehouse (Depósito/Logística)**: Control de inventario, movimientos de stock, preparación de remitos y recepciones.
- **Readonly (Solo lectura)**: Visualización de datos sin permisos de modificación, ideal para auditorías o perfiles consultivos.
- La verificación de permisos se implementa en las vistas DRF mediante clases de permisos personalizadas y validaciones por rol.

## Eventos WebSocket

Los eventos CRUD se transmiten al grupo `crud_events` con la siguiente estructura:
```json
{
  "type": "crud_event",
  "data": {
    "model": "product|category|cuttingorder|etc",
    "action": "created|updated|deleted",
    "id": 123,
    "data": { /* objeto serializado */ }
  }
}
```

El frontend escucha e invalida caches relevantes de TanStack Query automáticamente.

## Notas Importantes

- Frontend usa imports absolutos vía alias `@/` (mapea a `src/`)
- Apps del backend son altamente modulares - cada una tiene sus propios models, views, serializers
- Uploads de archivos usan URLs presignadas desde MinIO/S3 - backend genera URLs, frontend sube directamente
- Notificaciones se cachean con TTL corto para reducir queries a base de datos
- Categorías se cachean para evitar queries repetidas
- El sistema soporta OCR multi-idioma (Español + Inglés por defecto)
- Audit logs rastrean operaciones importantes (en apps relevantes)
- Simple History está habilitado para rastrear cambios en modelos a lo largo del tiempo
- **RECORDATORIO**: Todo el código debe escribirse en inglés con comentarios en español
