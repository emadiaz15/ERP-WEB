# ANÁLISIS: MANUFACTURA, PROCESOS EXTERNOS Y MIGRACIÓN VFP9

## 📊 ESTADO ACTUAL DEL BACKEND

### ✅ MÓDULOS IMPLEMENTADOS

Tu backend **YA TIENE** los siguientes módulos de manufactura completamente implementados:

#### 1. **`manufacturing`** - Manufactura Básica
Modelos implementados:
- ✅ `BillOfMaterials` (Lista de materiales/BOM)
- ✅ `BillOfMaterialsItem` (Componentes de BOM con tipos: raw_material, consumable, labor, service, packaging)
- ✅ `WorkOrder` (Órdenes de trabajo con estados y prioridades)
- ✅ `WorkOrderItem` (Consumo de componentes por orden)
- ✅ `WorkOrderLog` (Logs y seguimiento de órdenes)
- ✅ `ExternalTreatmentOrder` (Órdenes de tratamiento externo: galvanizado, pintura, zincado)
- ✅ `ExternalTreatmentLot` (Lotes de envío/recepción parcial con seguimiento detallado)

**Features clave**:
- ✅ Seguimiento de cantidades enviadas vs recibidas por lote
- ✅ Estados: scheduled, in_transit, partial_return, completed, cancelled
- ✅ Costos de servicio y flete separados
- ✅ Peso por lote (importante para galvanizado)

#### 2. **`manufacturing_pro`** - Manufactura Avanzada
Modelos implementados:
- ✅ `ManufacturingOrder` (Órdenes de fabricación avanzadas)
- ✅ `ManufacturingOrderMaterial` (Materiales/insumos planificados y consumidos)
- ✅ `ManufacturingOperation` (Operaciones con secuencia y tiempos)
- ✅ `ManufacturingOperationLog` (Logs de operaciones)
- ✅ `SupplyCategory` (Rubros de insumos)
- ✅ `SupplyItem` (Insumos con stock, costo, unidad)
- ✅ `SupplyVendor` (Proveedores de insumos con costos por proveedor)
- ✅ `SupplyCostHistory` (Histórico de costos de insumos)
- ✅ `SupplyStockMovement` (Movimientos de stock de insumos con Generic FK)
- ✅ `ExternalProcess` (Procesos externos mejorados)
- ✅ `ExternalProcessDetail` (Detalles por producto/insumo)
- ✅ `ExternalProcessMovement` (Movimientos de envío/recepción)

**Features clave**:
- ✅ Soporte de insumos vinculados a productos (via FK)
- ✅ Múltiples proveedores por insumo con flag "preferred"
- ✅ Histórico de costos con moneda (ARS/USD)
- ✅ Movimientos genéricos (RECEIPT, ISSUE, CONSUMPTION, ADJUSTMENT, TRANSFER)
- ✅ Procesos externos con tipos: GALVANIZADO, PINTURA, ZINCADO, HEAT_TREATMENT, MACHINING, ASSEMBLY, OTHER
- ✅ Seguimiento de cantidades enviadas y recibidas totales
- ✅ Estados: PLANNED, SENT, PARTIAL, RECEIVED, CANCELLED
- ✅ Costos estimados vs reales

### ⚠️ LO QUE FALTA IMPLEMENTAR

#### APIs/Views
Necesitas crear vistas REST para:
- [ ] `manufacturing/api/views/` (actualmente vacío)
- [ ] `manufacturing_pro/api/views/` (actualmente vacío)
- [ ] Serializers para todos los modelos de manufactura
- [ ] Repositories para queries optimizadas
- [ ] Services para lógica de negocio (ej: validación de stock antes de crear orden)
- [ ] Filters para búsquedas avanzadas

#### Lógica de Negocio Crítica
- [ ] **Validación de stock de insumos** antes de liberar orden de fabricación
- [ ] **Reserva de insumos** al planificar orden (similar a reserva de productos en ventas)
- [ ] **Actualización automática de stock** al consumir insumos
- [ ] **Cálculo de costos reales** basado en consumos efectivos
- [ ] **Notificaciones** cuando proceso externo tiene retorno parcial
- [ ] **Alertas de stock mínimo** de insumos
- [ ] **Integración con purchases** para generar órdenes de compra de insumos

## 🔄 MAPEO VFP9/MYSQL → DJANGO/POSTGRES

### Tablas de Manufactura VFP9 → Django

| VFP9 Table | Django Model | App | Estado | Notas |
|------------|--------------|-----|--------|-------|
| `insumos` | `SupplyItem` | manufacturing_pro | ✅ | Mapear `insu_codi` → `legacy_id` |
| `insu_rubros` | `SupplyCategory` | manufacturing_pro | ✅ | Mapear `insu_rub_id` → `legacy_id` |
| `insu_historicostock` | `SupplyStockMovement` | manufacturing_pro | ✅ | Convertir tipos de movimiento |
| `insu_ajustes` | Crear modelo o usar `SupplyStockMovement` | manufacturing_pro | ⚠️ | Pendiente decisión |
| `insu_articulos` | FK en `SupplyItem.product` | manufacturing_pro | ✅ | Relación directa |
| `insumos_proveedores` | `SupplyVendor` | manufacturing_pro | ✅ | Mapear `insuprov_codi` → id |
| `insu_prov_histocosto` | `SupplyCostHistory` | manufacturing_pro | ✅ | Migrar históricos |
| `orden_fabricacion` | `ManufacturingOrder` | manufacturing_pro | ✅ | Mapear `of_codi` → `legacy_id` |
| `fabricados` | `ManufacturingOrder` o modelo legacy | manufacturing_pro | ⚠️ | Analizar si consolidar |
| `fabricados_compras_articulos` | Relación a revisar | - | ⚠️ | Parece relacionar fab→compra→artículo |
| `procesos_externos` | `ExternalProcess` | manufacturing_pro | ✅ | Mapear `pe_codi` → id |
| `procesos_externos_detalle` | `ExternalProcessDetail` | manufacturing_pro | ✅ | Migrar con relaciones |
| `procesos_externos_movimientos` | `ExternalProcessMovement` | manufacturing_pro | ✅ | Tipos: ENVIO→ISSUE, RECEPCION→RECEIPT |

### Tablas Core VFP9 → Django (Resumen)

| VFP9 | Django | App | Notas Migración |
|------|--------|-----|-----------------|
| `articulos` | `Product` | products | Stock migrará a `StockProduct` |
| `rubros` | `Category` | products | ✅ |
| `clientes` | `Customer` | customers | Incluye saldo |
| `proveedores` | `Supplier` | suppliers | Incluye saldo |
| `personas` | ¿Tipo de proveedor? | - | Revisar uso |
| `pedidos` | `SalesOrder` | sales | ✅ |
| `compras` | `PurchaseOrder` | purchases | ✅ |
| `facturas` | `SalesInvoice` | sales/billing | ✅ |
| `recepciones` | `PurchaseReceipt` | purchases | ✅ |
| `remitos` | `DeliveryNote` | delivery_notes | ✅ |
| `histostock` | `StockEvent` | stocks | ✅ |
| `gastos` | `Expense` | expenses | ✅ |
| `recibos` | `Receipt` | treasury | ✅ |

### Nuevas Tablas en VFP9 para IA/Matching

Tu estructura VFP9 incluye tablas muy interesantes para AI:

| VFP9 Table | Propósito | Implementar en Django? |
|------------|-----------|------------------------|
| `articulo_abreviaciones` | Diccionario abreviaciones por artículo | ✅ Sí, en `products.models.DictionaryModel` |
| `articulo_sinonimos` | Sinónimos (cliente/interno/técnico) | ✅ Sí, mismo modelo |
| `diccionario_terminos` | Términos genéricos (material/medida/unidad) | ✅ Sí |
| `ia_presupuestos_meta` | Metadata de presupuestos generados por IA | ✅ Sí, crear en `sales` o nuevo app `ai_matching` |
| `ia_matching_log` | Log de matching IA línea→artículo | ✅ Sí |
| `ia_alias_articulos` | Alias aprendidos por IA | ✅ Sí |
| `art_metricas` | Métricas de rotación y scoring | ✅ Sí, en `products.models.MetricsModel` |
| `pedidos_preparacion` | Workflow de preparación de pedidos | ✅ Sí, en `orders` o `logistics` |
| `notificaciones` | Sistema de notificaciones VFP | ⚠️ Ya existe `notifications` app |

## 🚀 ESTRATEGIA DE MIGRACIÓN

### Fase 1: Preparación (ANTES de migrar datos)

1. **Completar APIs faltantes**:
   ```bash
   # Crear estructura de APIs
   Backend-API/apps/manufacturing/api/
   ├── serializers/
   │   ├── bom_serializer.py
   │   ├── work_order_serializer.py
   │   └── external_treatment_serializer.py
   ├── views/
   │   ├── bom_views.py
   │   ├── work_order_views.py
   │   └── external_treatment_views.py
   ├── repositories/
   └── urls.py

   Backend-API/apps/manufacturing_pro/api/
   ├── serializers/
   │   ├── supply_serializer.py
   │   ├── manufacturing_order_serializer.py
   │   └── external_process_serializer.py
   ├── views/
   │   ├── supply_views.py
   │   ├── manufacturing_order_views.py
   │   └── external_process_views.py
   ├── repositories/
   └── urls.py
   ```

2. **Agregar campos `legacy_id` donde falten**:
   - Asegurar que TODOS los modelos tengan campo `legacy_id` para mapeo
   - Crear índices en `legacy_id` para performance

3. **Implementar modelos de diccionario/IA**:
   ```python
   # Backend-API/apps/products/models/dictionary_models.py

   class ProductAbbreviation(BaseModel):
       product = ForeignKey(Product, ...)
       abbreviation = CharField(max_length=50)
       full_word = CharField(max_length=255)
       weight = IntegerField(default=1)
       notes = TextField(blank=True)

   class ProductSynonym(BaseModel):
       product = ForeignKey(Product, ...)
       synonym = CharField(max_length=255)
       type = CharField(choices=['cliente', 'interno', 'tecnico'])

   class GenericTerm(BaseModel):
       term = CharField(max_length=255)
       type = CharField(choices=['material', 'medida', 'unidad', 'accion'])
       value = CharField(max_length=255, blank=True)
   ```

4. **Crear app `ai_matching` (opcional)**:
   ```bash
   python manage.py startapp ai_matching
   ```

   Modelos sugeridos:
   - `AIQuoteMeta` → metadata de presupuestos IA
   - `AIMatchingLog` → log de matching
   - `AIProductAlias` → aliases aprendidos

### Fase 2: Scripts de Migración

1. **Crear management commands**:
   ```bash
   Backend-API/apps/products/management/commands/
   ├── migrate_from_mysql.py  # Master command
   ├── migrate_products.py
   ├── migrate_customers.py
   ├── migrate_suppliers.py
   └── ...

   Backend-API/apps/manufacturing_pro/management/commands/
   ├── migrate_supplies.py
   ├── migrate_manufacturing_orders.py
   └── migrate_external_processes.py
   ```

2. **Estructura de comando típico**:
   ```python
   # Obtener todos los productos activos con sus categorías
   from django.core.management.base import BaseCommand
   from django.db import transaction
   import pymysql

   class Command(BaseCommand):
       help = 'Migrar insumos desde MySQL VFP9'

       def add_arguments(self, parser):
           parser.add_argument('--host', default='localhost')
           parser.add_argument('--database', required=True)
           parser.add_argument('--user', required=True)
           parser.add_argument('--password', required=True)
           parser.add_argument('--batch-size', type=int, default=1000)
           parser.add_argument('--dry-run', action='store_true')

       def handle(self, *args, **options):
           # Conectar a MySQL
           connection = pymysql.connect(...)

           with connection.cursor(pymysql.cursors.DictCursor) as cursor:
               # Leer datos VFP9
               cursor.execute("SELECT * FROM insumos WHERE insu_activo = 1")

               # Migrar en batches
               batch = []
               for row in cursor:
                   supply = SupplyItem(
                       legacy_id=row['insu_codi'],
                       code=row.get('insu_desc'),  # Revisar campo
                       name=row['insu_desc'],
                       unit=self.map_unit(row['insu_unimed']),
                       stock_quantity=row['insu_stock'] or 0,
                       min_stock=row['insu_stmin'] or 0,
                       cost_current=row['insu_costo'] or 0,
                       last_purchase_cost=row['insu_ultcpra'] or 0,
                       is_active=bool(row['insu_activo']),
                       details=row.get('insu_detalle', ''),
                   )
                   batch.append(supply)

                   if len(batch) >= options['batch_size']:
                       if not options['dry_run']:
                           with transaction.atomic():
                               SupplyItem.objects.bulk_create(batch)
                       self.stdout.write(f"Migrados {len(batch)} insumos")
                       batch = []

               # Último batch
               if batch and not options['dry_run']:
                   SupplyItem.objects.bulk_create(batch)
   ```

### Fase 3: Orden de Migración

**CRÍTICO**: Respetar este orden por dependencias:

1. ✅ Datos maestros sin FK:
   - Zonas, provincias, localidades, códigos postales
   - Condiciones IVA
   - Rubros de artículos
   - Rubros de insumos
   - Bancos

2. ✅ Entidades principales:
   - Vendedores
   - Transportes
   - Clientes
   - Proveedores
   - Usuarios

3. ✅ Productos e Insumos:
   - Artículos (products)
   - Insumos (supplies)
   - Relaciones artículo-cliente
   - Relaciones artículo-proveedor
   - Relaciones insumo-proveedor
   - Históricos de costos

4. ✅ Inventario:
   - Stock inicial de productos
   - Stock inicial de insumos
   - Ajustes de inventario

5. ✅ Transacciones:
   - Presupuestos
   - Pedidos de venta
   - Órdenes de compra
   - Órdenes de fabricación
   - Procesos externos
   - Recepciones
   - Remitos
   - Facturas
   - Gastos

6. ✅ Finanzas:
   - Recibos
   - Pagos
   - Regularizaciones
   - Retenciones

7. ✅ Históricos:
   - Histórico de stock (productos)
   - Histórico de stock (insumos)
   - Movimientos de procesos externos

8. ✅ IA/Métricas (nuevo):
   - Métricas de artículos
   - Diccionario de términos
   - Abreviaciones y sinónimos

### Fase 4: Validación Post-Migración

```python
# Script de validación
python manage.py validate_migration --verbose

# Verificar:
# - Conteos coinciden con MySQL
# - Saldos de clientes/proveedores cuadran
# - Stock total coincide
# - Relaciones FK intactas
# - Sin registros huérfanos
```

## 📋 CHECKLIST PRE-PRODUCCIÓN

### Backend

- [ ] Todas las APIs de `manufacturing` implementadas
- [ ] Todas las APIs de `manufacturing_pro` implementadas
- [ ] Services de manufactura con validaciones
- [ ] Tests unitarios para lógica crítica
- [ ] Migración VFP9 probada en staging
- [ ] Cache configurado (Redis)
- [ ] MinIO configurado para archivos
- [ ] Permisos por rol configurados
- [ ] Logs de auditoría habilitados
- [ ] Backup automático de Postgres configurado

### Migración

- [ ] Script de migración completo y testeado
- [ ] Validación de integridad referencial
- [ ] Plan de rollback documentado
- [ ] Ventana de migración definida
- [ ] Equipo capacitado en nuevo sistema
- [ ] Datos de prueba migrados exitosamente

### Infraestructura

- [ ] Postgres 15+ configurado con `work_mem` adecuado
- [ ] Redis para cache y Celery
- [ ] MinIO para archivos estáticos
- [ ] Nginx/Caddy como reverse proxy
- [ ] SSL/TLS configurado
- [ ] Monitoreo (Sentry/NewRelic)
- [ ] Backups automáticos

## 💡 RECOMENDACIONES CRÍTICAS

### 1. Manejo de Procesos Externos con Recepciones Parciales

**Implementar lógica**:
```python
# En services/external_process_service.py

# Registrar recepción parcial desde remito de proveedor
def register_partial_reception(
    external_process_id: int,
    product_id: int,
    quantity_received: Decimal,
    remit_number: str,
    user
) -> ExternalProcessMovement:
    # Validar que no se reciba más de lo enviado
    # Actualizar total_received_quantity
    # Cambiar estado a PARTIAL si corresponde
    # Crear movimiento tipo RECEIPT
    # Notificar si falta recibir más del 10%
    ...
```

### 2. Integración Stocks de Insumos con Manufactura

**Flujo sugerido**:
1. Al crear `WorkOrder` → reservar insumos (similar a productos en ventas)
2. Al iniciar producción → consumir insumos de stock
3. Al finalizar → liberar insumos no utilizados
4. Registrar merma si aplica

### 3. Costos Reales vs Estimados

**Implementar**:
```python
# Al finalizar WorkOrder
def calculate_actual_costs(work_order: WorkOrder):
    # Sumar costos de insumos consumidos
    # Sumar costos de procesos externos
    # Sumar mano de obra (si se trackea)
    # Actualizar cost_actual en WorkOrder
    # Comparar con cost_estimate y alertar si desviación >20%
```

### 4. Alertas de Stock Mínimo

**Celery task periódica**:
```python
# En tasks.py
@periodic_task(run_every=timedelta(hours=6))
def check_supply_min_stock():
    # Buscar insumos con stock < min_stock
    # Generar notificación interna
    # Opcional: crear draft de orden de compra automática
```

## 🎯 PRÓXIMOS PASOS SUGERIDOS

### Corto Plazo (1-2 semanas)

1. **Crear APIs REST completas** para `manufacturing` y `manufacturing_pro`
2. **Implementar services** con validaciones de negocio
3. **Agregar tests** para flujos críticos
4. **Crear modelos de diccionario** para IA/matching

### Mediano Plazo (3-4 semanas)

1. **Desarrollar scripts de migración** para cada módulo
2. **Probar migración** en ambiente staging
3. **Ajustar modelos** según resultados de pruebas
4. **Capacitar equipo** en nuevo sistema

### Largo Plazo (1-2 meses)

1. **Migración a producción** en ventana planificada
2. **Monitoreo intensivo** primeras semanas
3. **Ajustes finos** basados en feedback
4. **Descomisionar** sistema VFP9 gradualmente

---

## 📞 CONTACTO PARA DUDAS

Este análisis fue generado para asistir en la migración del sistema VFP9 a Django REST Framework con PostgreSQL.

**Recuerda**: Este sistema debe entrar en producción **INSTANTÁNEAMENTE** manteniendo TODOS los datos actuales de la empresa. Por lo tanto, la fase de pruebas y validación es **CRÍTICA**.
