# Backend para Sistema de Gestión de Productos

Este proyecto es el backend de un sistema de gestión de productos orientado a la administración de inventarios, especializado en la gestión de un producto en particular (en esta versión, cables). El sistema permite a los administradores y operarios gestionar productos, monitorear niveles de stock, realizar seguimientos de órdenes de corte, y generar reportes. El backend está construido utilizando **Django** y **Django REST Framework (DRF)**.

## **Índice**

- [Descripción del proyecto](#Descripcion-del-proyecto)
- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [API Endpoints](#api-endpoints)
- [Pruebas](#pruebas)
- [Arquitectura](#arquitectura)

## **Descripción del Proyecto**

Nombre del Proyecto: Inventory Management System

**Propósito**: Este sistema facilita la gestión de inventario y permite realizar un seguimiento detallado de productos dentro de una empresa o tienda. Inicialmente se centra en la gestión de cables, permitiendo a los administradores organizar productos, supervisar niveles de stock, manejar órdenes de corte, y generar reportes. Los operarios también pueden acceder a funciones como la consulta de productos y el cambio de estado de las órdenes de corte.

## **Características**

- CRUD para productos, categorías, tipos y marcas.
- Gestión de stock y visualización de la ubicación de productos en el depósito.
- Sistema de autenticación y autorización basado en JWT.
- Gestión de usuarios, roles y permisos.
- Gestión de órdenes de corte con cambio de estado (pendiente, en proceso, finalizado).
- Generación de reportes de inventarios, incluyendo órdenes de corte y productos faltantes.

## **Requisitos**

Antes de empezar, asegúrate de tener instalado lo siguiente en tu entorno:

- **Python 3.8+**
- **Django 3.2+**
- **PostgreSQL**
- **Pipenv** (opcional, para manejo de entornos virtuales)

## **Instalación**

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/emadiaz15/InventoryManagementSystem-API.git
   cd Backend-API
   ```
2. **Crear entorno virtual (opcional)**:
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```
3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configurar la base de datos** (`settings/local.py`):
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'nombre_base_datos',
           'USER': 'tu_usuario',
           'PASSWORD': 'tu_contraseña',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```
5. **Aplicar migraciones**:
   ```bash
   python manage.py migrate
   ```
6. **Correr el servidor**:
   ```bash
   python manage.py runserver
   ```

## **Configuración**

### Configurar las variables de entorno

Crea un archivo `.env` en la raíz del proyecto y agrega las variables de entorno necesarias, como la configuración de la base de datos, las claves secretas, etc.

Ejemplo de `.env`:

```bash
DEBUG=True
SECRET_KEY=tu_clave_secreta_aqui
DATABASE_URL=postgres://tu_usuario:tu_contraseña@localhost:5432/nombre_base_datos
```

## **Uso**

### Endpoints principales

- **Autenticación**: `/api/v1/user/`
- **Productos**: `/api/v1/products/`
- **Categorías**: `/api/v1/categories/`
- **Tipos**: `/api/v1/types/`

## **API Endpoints**

| Método| Endpoint              | Descripción                           |
| ------| -------------------   | ------------------------------------- |
| POST  |/api/v1/user/login/    | Inicia sesión y obtiene el token JWT. |
| GET   |/api/v1/products/      | Obtiene la lista de productos.        |
| POST  |/api/v1/products       | Crea un nuevo producto.               |
| GET   |/api/v1/products/<id>/ | Obtiene los detalles de un producto.  |
| PUT   |/api/v1/products/<id>/ | Actualiza un producto existente.      |
| DELETE|/api/v1/products/<id>/ | Elimina un producto.                  |

### Archivos de Productos y Subproductos

| Método | Endpoint | Descripción | Permisos |
| ------ | -------- | ----------- | -------- |
| POST | /api/products/<product_id>/files/upload/ | Sube archivos para el producto | Admin |
| GET | /api/products/<product_id>/files/ | Lista archivos del producto | Autenticado |
| GET | /api/products/<product_id>/files/<file_id>/download/ | Descarga un archivo del producto | Autenticado |
| DELETE | /api/products/<product_id>/files/<file_id>/delete/ | Elimina un archivo del producto | Admin |
| POST | /api/products/<product_id>/subproducts/<subproduct_id>/files/upload/ | Sube archivos para el subproducto | Admin |
| GET | /api/products/<product_id>/subproducts/<subproduct_id>/files/ | Lista archivos del subproducto | Autenticado |
| GET | /api/products/<product_id>/subproducts/<subproduct_id>/files/<file_id>/download/ | Descarga un archivo del subproducto | Autenticado |
| DELETE | /api/products/<product_id>/subproducts/<subproduct_id>/files/<file_id>/delete/ | Elimina un archivo del subproducto | Admin |

Los endpoints de subida y eliminación requieren permisos de **administrador**. Para listar o descargar archivos basta con estar **autenticado**.

### Categorías

| Método | Endpoint | Descripción | Permisos |
| ------ | -------- | ----------- | -------- |
| GET | /api/categories/ | Lista las categorías activas | Autenticado |
| POST | /api/categories/create/ | Crea una nueva categoría | Admin |
| GET | /api/categories/<id>/ | Detalles de una categoría | Autenticado |
| PUT | /api/categories/<id>/ | Actualiza una categoría | Admin |
| DELETE | /api/categories/<id>/ | Elimina una categoría | Admin |

### Subproductos

| Método | Endpoint | Descripción | Permisos |
| ------ | -------- | ----------- | -------- |
| GET | /api/products/<product_id>/subproducts/ | Lista los subproductos de un producto | Autenticado |
| POST | /api/products/<product_id>/subproducts/create/ | Crea un subproducto | Admin |
| GET | /api/products/<product_id>/subproducts/<subproduct_id>/ | Detalles de un subproducto | Autenticado |
| PUT | /api/products/<product_id>/subproducts/<subproduct_id>/ | Actualiza un subproducto | Admin |
| DELETE | /api/products/<product_id>/subproducts/<subproduct_id>/ | Elimina un subproducto | Admin |

### Órdenes de Corte

| Método | Endpoint | Descripción | Permisos |
| ------ | -------- | ----------- | -------- |
| GET | /api/cutting-orders/ | Lista todas las órdenes de corte | Autenticado |
| GET | /api/cutting-orders/assigned/ | Órdenes asignadas al usuario | Autenticado |
| POST | /api/cutting-orders/create/ | Crea una orden de corte | Admin |
| GET | /api/cutting-orders/<id>/ | Detalle de una orden | Autenticado |
| PUT | /api/cutting-orders/<id>/ | Actualiza una orden | Admin |
| PATCH | /api/cutting-orders/<id>/ | Actualiza parcialmente una orden | Admin |
| DELETE | /api/cutting-orders/<id>/ | Elimina una orden | Admin |

### Eventos de Stock

| Método | Endpoint | Descripción | Permisos |
| ------ | -------- | ----------- | -------- |
| GET | /api/products/<id>/stock/events/ | Historial de stock del producto | Autenticado |
| GET | /api/products/<product_id>/subproducts/<subproduct_id>/stock/events/ | Historial de stock del subproducto | Autenticado |

### Usuarios

| Método | Endpoint | Descripción | Permisos |
| ------ | -------- | ----------- | -------- |
| POST | /api/users/login/ | Inicia sesión y obtiene el token JWT | Público |
| POST | /api/users/register/ | Registra un nuevo usuario | Público |
| POST | /api/users/logout/ | Cierra la sesión del usuario | Autenticado |
| GET | /api/users/profile/ | Obtiene el perfil del usuario autenticado | Autenticado |
| GET | /api/users/list/ | Lista todos los usuarios | Admin |
| GET | /api/users/<id>/ | Detalles de un usuario | Autenticado |
| PUT | /api/users/<id>/ | Actualiza un usuario | Propietario/Admin |
| DELETE | /api/users/<id>/ | Elimina un usuario | Admin |
| DELETE | /api/users/image/<file_id>/delete/ | Elimina una imagen de perfil | Autenticado |
| PUT | /api/users/image/<file_id>/replace/ | Reemplaza una imagen de perfil | Autenticado |
| POST | /api/users/password-reset/confirm/<uidb64>/<token>/ | Confirma el restablecimiento de contraseña | Admin |

## **Arquitectura**

La arquitectura de este proyecto sigue un patrón tradicional de MVC (Modelo-Vista-Controlador) y está dividida en módulos clave para la gestión de productos, categorías y tipos.

### Estructura del Proyecto:

- **Django** como el framework para el backend.
- **Django REST Framework (DRF)** para la creación de la API.
- **PostgreSQL** como base de datos relacional.

## **Tecnologías Utilizadas**

- **Back-End**: Django, Django REST Framework
- **Base de Datos**: PostgreSQL
- **Autenticación**: JWT (JSON Web Tokens)
- **Control de Versiones**: Git y GitHub

## **Pruebas**

Para ejecutar las pruebas utiliza la configuración de tests ubicada en `inventory_management.settings.test`.


```bash
DJANGO_SETTINGS_MODULE=inventory_management.settings.test python manage.py test
```
O bien con PyTest:

También puedes usar `pytest` de la siguiente forma:

```bash
DJANGO_SETTINGS_MODULE=inventory_management.settings.test python -m pytest -q
```

## 📦 Módulos Nuevos: OCR & Intake (WhatsApp Orders)

Este backend ahora incluye un pipeline para recepcionar pedidos vía WhatsApp (multi‑imagen) procesados por OCR y convertirlos en órdenes estructuradas dentro del sistema.

### 🔠 OCR

Endpoints:

| Método | Endpoint | Descripción |
| ------ | -------- | ----------- |
| POST | /api/v1/ocr/ocr/ | OCR de una imagen (`image_url`) |
| POST | /api/v1/ocr/ocr-multi/ | OCR de múltiples imágenes (`image_urls[]`) |

Payload ejemplo (single):
```json
{ "image_url": "https://.../p1.jpg", "lang": "spa+eng", "psm": "6" }
```
Respuesta:
```json
{ "text": "...", "lang": "spa+eng", "psm": "6", "oem": "3" }
```

### 🗂 Intake

Modelos clave:
- IntakeBatch (conversación / lote)
- IntakeDocument (una por página OCR)
- IntakeOrder (cabecera estructurada)
- IntakeOrderItem (líneas)
- WorkAssignment (asignación a operario)
- AuditLog (auditoría de eventos)

Endpoints:

| Método | Endpoint | Descripción |
| ------ | -------- | ----------- |
| POST | /api/v1/intake/intake-batches/ | Crea batch |
| POST | /api/v1/intake/intake-documents/ | Crea documento (página) |
| POST | /api/v1/intake/intake-orders/ | Crea orden + items |
| POST | /api/v1/intake/intake-orders/{id}/assign/ | Asigna orden a usuario |
| GET | /api/v1/intake/intake-orders/ | Lista órdenes |
| GET | /api/v1/intake/intake-orders/{id}/ | Detalle orden |
| POST | /api/v1/intake/parse/ | Parseo de texto OCR → estructura preliminar |

Ejemplo crear batch:
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
   -d '{"source":"whatsapp","external_conversation_id":"wamid.123"}' \
   https://api.example.com/api/v1/intake/intake-batches/
```

Ejemplo crear orden:
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
   -d '{
   "batch":42,
   "source":"whatsapp",
   "external_id":"wamid.123",
   "customer_name":"Cliente SA",
   "locality":"Córdoba",
   "order_number":"PO-778",
   "order_date":"2025-09-23",
   "carrier":"Trans A",
   "carrier_redespacho":"Redesp B",
   "declared_value":null,
   "notes":"Entrega urgente",
   "raw_text_merged":"(texto original OCR)",
   "payload":{},
   "status":"validated",
   "items":[{"line_no":1,"qty":5,"code":"00311615","raw_description":"Cable x", "sku":"00311615","name":"Cable X","confidence":0.92}]
}' https://api.example.com/api/v1/intake/intake-orders/
```

Asignar:
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
   -d '{"assigned_to":7}' \
   https://api.example.com/api/v1/intake/intake-orders/314/assign/
```

### 🔁 Disparo de Orden de Corte Automática
Si algún `IntakeOrderItem` matchea un `Product` con `has_subproducts=True`, se intenta crear una CuttingOrder (modo vacío para que el operario defina subproductos). Se registra en `AuditLog` (`cutting_order_triggered` o `cutting_order_error`).

### ⚙ Variables de Entorno OCR
| Variable | Default | Descripción |
| -------- | ------- | ----------- |
| OCR_LANG | spa+eng | Idiomas Tesseract combinados |
| OCR_PSM | 6 | Page segmentation mode |
| OCR_OEM | 3 | OCR Engine Mode |
| OCR_MAX_MB | 10 | Peso máximo por imagen (MB) |
| TESSDATA_PREFIX | /usr/share/tesseract-ocr/4.00/ | Ruta de datos de idioma |

### 🧪 QA Rápido (cURL)
```bash
# OCR single
curl -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
   -d '{"image_url":"https://.../img1.jpg"}' https://api.example.com/api/v1/ocr/ocr/

# Parse texto
curl -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
   -d '{"raw_text_merged":"Cliente: ACME SA\nLocalidad: Córdoba\nPedido: P-1\nFecha: 12/09/2025"}' \
   https://api.example.com/api/v1/intake/parse/
```

### 📄 Notas
- No se loguea el `raw_text_merged` completo en errores críticos (recomendado reforzar filtros de logging si se agrega más debug).
- La seguridad aplica `IsAuthenticated`; se puede agregar un permiso específico para `assign`.
- El parseo actual es baseline (regex inicial); se recomienda iterar con ejemplos reales.

## 🚀 Despliegue en Docker + PostgreSQL

Esta sección describe un flujo de despliegue productivo con PostgreSQL, uso de la migración squashed y estrategias de rollback / cero downtime.

### 1. Imagen y Servicios

Ejemplo mínimo de `docker-compose.override.yml` para local/prod (ajusta variables en `.env`):
```yaml
version: '3.9'
services:
   db:
      image: postgres:15-alpine
      environment:
         POSTGRES_DB: ${POSTGRES_DB}
         POSTGRES_USER: ${POSTGRES_USER}
         POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      volumes:
         - postgres_data:/var/lib/postgresql/data
      healthcheck:
         test: ["CMD", "pg_isready", "-U", "${POSTGRES_USER}" ]
         interval: 10s
         timeout: 5s
         retries: 5
   api:
      build: .
      depends_on:
         db:
            condition: service_healthy
      env_file: .env
      command: ["./entrypoint.sh", "gunicorn"]
      ports:
         - "8000:8000"
volumes:
   postgres_data:
```

Variables `.env` mínimas:
```env
POSTGRES_DB=ims
POSTGRES_USER=ims
POSTGRES_PASSWORD=ims_pass
DATABASE_URL=postgres://ims:ims_pass@db:5432/ims
DJANGO_SETTINGS_MODULE=inventory_management.settings.production
SECRET_KEY=change-me
ALLOWED_HOSTS=*
```

### 2. Migraciones Squashed

Se consolidó el historial inicial (squash) y actualmente se mantiene un único archivo base (`0001_initial.py`) que ya incluye los campos antes repartidos en las antiguas `0001_squashed_0005_initial`, `0002_intakeorder_address_fields` y `0003_pagination_fields`.

Si tu base de datos venía de un estado previo con esas migraciones registradas y quieres “remigrar” sólo `intake`:

Opción limpia (destructiva sobre datos intake):
1. Ejecutar script `./scripts/reset_intake.sh` (recrea tablas y aplica 0001).

Opción conservadora (si la estructura ya coincide y sólo falta alinear historial):
1. Eliminar entradas de `django_migrations` para intake manualmente.
2. `python manage.py migrate intake 0001_initial --fake`.

El script soporta modo fake:
```bash
./scripts/reset_intake.sh --fake
```
Esto marca la migración como aplicada sin tocar tablas.

Primera instalación (sin datos previos):
```bash
python manage.py migrate --noinput
```
Esto aplica directamente la squashed + las nuevas.

Entorno ya existente (antes de squash) – estrategia recomendada:
1. Deploy previo (antes de merge squash) aplica hasta `0005_*`.
2. Congelas tráfico/escalas a 0 workers (opcional en bajo volumen) o ejecutas en ventana controlada.
3. Actualizas código que trae la migración squashed.
4. En DB que ya tiene 0001-0005, Django marcará la squashed como aplicada porque tiene `replaces=` => no re-ejecuta DDL redundante.
5. Ejecutas `python manage.py migrate` para continuar con migraciones posteriores (>=0002 nuevas).

### 3. Estrategia Cero Downtime (Blue-Green / Rolling)

Para minimizar downtime:
- Paso A: Construir nueva imagen (incluye migraciones nuevas).
- Paso B: Ejecutar job de migraciones en un contenedor temporal: `docker compose run --rm api python manage.py migrate`.
- Paso C: Una vez exitoso, escalar nuevos pods/containers con la nueva imagen y retirar los antiguos.
- Evitar cambios destructivos: no renombrar/eliminar columnas en una sola release si el código aún las lee. Usar fases (add → backfill → switch → drop).

### 4. Rollback Seguro

Tipos de rollback:
- Código solamente (migraciones no divergentes): volver a imagen anterior; no requiere acción en DB.
- Código + migraciones ya aplicadas: SI la migración es no reversible y cambió esquema (drop column), se debe preparar `reverse migration` antes. Buenas prácticas:
   1. Evitar drops en la misma release crítica.
   2. Marcar migraciones potencialmente sensibles con `RunPython` reversible.
   3. Respaldar (snapshot) antes de `migrate` en producción.

Checklist previo a rollback:
1. ¿Hay migraciones irreversibles? (`RunPython` sin `reverse_code`).
2. ¿Se eliminaron columnas requeridas por la versión anterior? (si sí → no rollback directo).
3. ¿Se cambiaron tipos incompatibles? (ej.: numeric→text). Considerar migración compensatoria.

### 5. Variables de Entorno Clave Producción

| Variable | Descripción |
|----------|-------------|
| DATABASE_URL | Cadena completa a Postgres |
| SECRET_KEY | Clave Django |
| ALLOWED_HOSTS | Hosts permitidos |
| DJANGO_SETTINGS_MODULE | `inventory_management.settings.production` |
| CELERY_BROKER_URL | Redis / RabbitMQ si se activa Celery real |
| OCR_LANG / OCR_PSM / OCR_OEM | Parámetros OCR |
| MEDIA_ROOT / MEDIA_URL | Almacenamiento de archivos |

### 6. Migraciones Lentas / Grandes

Si surge una migración pesada (ej. columnas nuevas con default costoso):
1. Crear columna NULL sin default.
2. Backfill por lotes (script / management command) fuera de transacción global.
3. Agregar constraint / not null en migración subsecuente.

### 7. Monitoreo Post Deploy

- Verificar errores en logs (`django-error.log`).
- Confirmar conteos clave: `IntakeOrder` recientes, `AuditLog` incrementándose.
- Chequear health endpoint (si se expone) o `GET /api/v1/intake/intake-orders/?page=1`.

### 8. Ejecución Tests en Postgres (CI / Local)

Settings dedicados recomendados (`settings/testing.py` existe, se puede crear uno para Postgres test). Ejemplo variable:
```bash
DJANGO_SETTINGS_MODULE=inventory_management.settings.test_postgres \
DATABASE_URL=postgres://ims:ims_pass@localhost:5432/ims_test pytest -q
```
O usar `TEST` dict en `DATABASES` si se mantiene SQLite productivo (no recomendado para este caso).

### 9. Limpieza de Migraciones Futuras

Sólo volver a hacer squash cuando:
- Se haya estabilizado un gran bloque nuevo.
- No haya datos críticos difíciles de recrear, o se haga offline con respaldo.

## ♻️ Rollback de Cutting Orders y Señales

Las CuttingOrders se crean vía señal `post_save` de `IntakeOrderItem`. Para mitigar efectos indeseados en rollback:
1. Feature flag opcional (añadir setting `INTAKE_ENABLE_AUTO_CUTTING=True`).
2. Si se desactiva, la señal puede leer `if not settings.INTAKE_ENABLE_AUTO_CUTTING: return`.
3. Añadir migración futura para persistir flag en DB si se requiere control operacional.

## ✅ Checklist Hermeticidad (Resumen)

| Ítem | Estado | Notas |
|------|--------|-------|
| Soft delete BaseModel en intake | OK | Todos heredan o tienen status+deleted_at |
| Separación flow_status vs status | OK | `flow_status` para workflow, boolean `status` para soft delete |
| Squash migración inicial | OK | 0001_squashed_0005_initial + incrementales |
| Parser avanzado (address, declared, shipping, items) | OK | `parse_service.py` |
| Normalización códigos sin 00 | OK | `normalize_code` en parser |
| Señal cutting por item | OK | Evita duplicados con AuditLog |
| Auditoría parse | OK | action=parsed con métricas |
| Campos paginación (footer, expected, page_total) | OK | Modelos y serializers |
| Inconsistencia footer logging | OK | action=footer_inconsistency |
| Tests parser 3 casos | OK | `tests_parser.py` |
| Postgres deploy doc | (Ahora) | Esta sección añadida |
| Rollback strategy | OK | Documentado arriba |
| Cero downtime | OK | Flujo blue-green descrito |

## 🔄 Flujo n8n (Resumen Lógico)

1. Recibir imagen → crear/recuperar `IntakeBatch` (por `external_conversation_id`).
2. OCR por página → `IntakeDocument` (se parsea footer, se actualiza `expected_pages`).
3. Cuando el usuario envía mensaje final / trigger de cierre:
    - Si `expected_pages` y `count(documents) < expected_pages` → esperar (o timeout).
    - Else → unir `raw_text` de documentos en orden y llamar a `/api/v1/intake/parse/`.
4. Crear `IntakeOrder` con JSON parseado (incluyendo `page_total`).
5. Items generan potencial CuttingOrder (señal) si aplica.
6. Asignación manual vía `/assign/` (idempotente). Cierre cuando CuttingOrders listos.

## 🧪 Comandos Operacionales Útiles

```bash
# Crear superuser rápido
python manage.py createsuperuser --username admin --email admin@example.com

# Ver migraciones
python manage.py showmigrations intake

# Aplicar sólo intake
python manage.py migrate intake

# Revisar logs error
tail -f logs/django-error.log

# Shell inspección rápida
python manage.py shell_plus
```

## 🔐 Seguridad y Datos Sensibles

- Asegura rotación de `SECRET_KEY` en caso de incidente (invalida sesiones).
- Revisa exposición de `raw_text_merged` en logs (actualmente no se loguea completo).
- Implementar rate limiting en endpoints OCR si se abre al exterior.

---
Fin de la sección de despliegue y operación.

## 🛠 Monitoreo Post-Deploy (DB, Cache, Notificaciones)

### Objetivos
- Verificar reducción de queries repetitivas a categorías y métricas.
- Confirmar que el frontend ya no hace doble request (lista + unread) sino `summary`.
- Validar tiempos de respuesta más estables al activar caching corto.

### Checklist Rápido
1. Activar temporalmente logging SQL (máx pocos minutos):
   ```bash
   export DJANGO_SQL_LOG_LEVEL=INFO
   ```
2. Hacer un ciclo de uso normal del frontend (abrir panel notificaciones, navegar categorías, dashboard métricas).
3. Revisar logs: contar SELECT a `products_category` y queries de agregación de métricas.
4. Confirmar que requests HTTP muestran `/notifications/summary/` y no `/notifications/unread-count/` reiterado.
5. Desactivar logging SQL:
   ```bash
   unset DJANGO_SQL_LOG_LEVEL
   ```

### Postgres (pg_stat_statements)
```sql
SELECT query, calls, total_exec_time, mean_exec_time
FROM pg_stat_statements
WHERE query ILIKE '%products_category%' OR query ILIKE '%products_with_files%'
ORDER BY calls DESC
LIMIT 20;
```

### Redis / Cache (opcional)
```bash
redis-cli INFO stats | grep hits
```
Interpretar: aumento de hits y moderado número de misses tras algunas navegaciones repetidas.

### Ajustes Finos
- Si categorías cambian muy a menudo: bajar TTL a 30s.
- Si casi no cambian: subir TTL a 120s.
- Para métricas costosas ampliar TTL si se vuelve hot spot.

## 📄 robots.txt y Cache-Control

Si sirves `robots.txt` directamente por Django sin un servidor frontal (Nginx / Caddy) que inyecte headers, puedes añadir un pequeño view o middleware para enviar:

```
Cache-Control: public, max-age=86400
```

Ejemplo rápido de view (añadir a un módulo `core/views_public.py`):
```python
from django.http import HttpResponse

def robots_txt(request):
    content = "User-agent: *\nDisallow:\n"
    resp = HttpResponse(content, content_type="text/plain")
    resp['Cache-Control'] = 'public, max-age=86400'
    return resp
```
Y en `urls.py` principal:
```python
from core.views_public import robots_txt
urlpatterns += [path('robots.txt', robots_txt)]
```

Si usas Nginx:
```
location = /robots.txt { add_header Cache-Control "public, max-age=86400"; }
```

---
Monitoreo y headers añadidos: ajusta según tu infraestructura.

