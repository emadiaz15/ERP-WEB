# ANÁLISIS COMPLETO: App `products` e INTEGRACIÓN con `stocks` y `sales`

## 🎯 OBJETIVO: Sistema Integrado de Comercio

El usuario necesita un sistema donde **las apps funcionen en conjunto**, es decir:

```
FLUJO REAL DE NEGOCIO:
1. Cliente hace pedido → SalesOrder se crea
2. Sistema RESERVA stock de productos → ProductStock.quantity_reserved se incrementa
3. Sistema registra en SalesOrderItem → cliente, transporte, cantidades
4. Al facturar/remitar → Stock DISPONIBLE disminuye, RESERVADO se libera
5. Si se cancela → RESERVADO se libera, stock vuelve a estar disponible
```

---

## ✅ LO QUE YA EXISTE (MUY COMPLETO)

### App `products` - **EXCELENTE Estado**

**Modelos Implementados**:
- ✅ `Product` - Producto maestro con:
  - Campos legacy compatibles (code, name, price, last_purchase_cost, unit, min_stock)
  - Campos de negocio (`pending_customer_orders`, `pending_supplier_orders`)
  - Relación con `Category`
  - Flag `has_subproducts` para gestión de stock jerárquica
  - Campos VAT, ubicación, marca
- ✅ `Subproduct` - Subproductos de un producto
- ✅ `Category` - Categorías/rubros
- ✅ `ProductImage`, `SubproductImage` - Imágenes S3/MinIO
- ✅ `CustomerProduct` - Configuración producto por cliente
- ✅ `SupplierProduct` - Configuración producto por proveedor
- ✅ `ProductAbbreviation`, `ProductSynonym`, `ProductAlias`, `GenericTerm` - Diccionario IA
- ✅ `ProductMetrics` - Métricas de rotación ABC

**API REST Completa**:
- ✅ CRUD productos (list, create, detail, update, delete)
- ✅ CRUD categorías
- ✅ CRUD subproductos
- ✅ Files management (upload, download, delete) S3/MinIO
- ✅ Relaciones producto-cliente
- ✅ Relaciones producto-proveedor
- ✅ Catálogo maestro con búsquedas
- ✅ Histórico de stock
- ✅ Métricas
- ✅ Diccionario de términos

**Características Avanzadas**:
- ✅ Repository pattern
- ✅ Cache con Redis + invalidación en signals
- ✅ Filtros con django-filter
- ✅ Documentación con drf-spectacular (CASI completa)
- ✅ Serializers bien organizados

### App `stocks` - **Services YA Implementados**

**Modelos**:
- ✅ `ProductStock` - Stock de productos (con constraint no negativo)
- ✅ `SubproductStock` - Stock de subproductos
- ✅ `StockEvent` - Histórico de movimientos

**Services Implementados** (`stocks/services/`):
- ✅ `product_stock.py`:
  - `initialize_product_stock()` - Crear registro de stock inicial
  - `adjust_product_stock()` - Ajustar stock con validaciones
- ✅ `subproduct_stock.py`:
  - `initialize_subproduct_stock()`
  - `adjust_subproduct_stock()`
- ✅ `reservations.py`:
  - `reserved_qty()` - **SOLO para cutting orders** (órdenes de corte)
- ✅ `validators.py` - Validaciones de stock
- ✅ `sync.py` - Sincronización
- ✅ `status.py` - Estados de stock
- ✅ `queries.py` - Queries optimizadas

**Transacciones Atómicas**: Todos los services usan `@transaction.atomic`

### App `sales` - **Modelos Ya Creados**

**Modelos**:
- ✅ `SalesOrder` - Pedido de venta con:
  - Estados: DRAFT, CONFIRMED, PARTIALLY_SHIPPED, COMPLETED, CANCELLED
  - Campos: customer, order_date, currency, transport, notes
  - Legacy compatible (`legacy_id`, `customer_legacy_id`, `transport_legacy_id`)
- ✅ `SalesOrderItem` - Renglones de pedido con:
  - `product`, `quantity_ordered`, `quantity_shipped`, `unit_price`, `discount_amount`
- ✅ `SalesShipment`, `SalesShipmentItem` - Envíos
- ✅ `SalesInvoice`, `SalesInvoiceItem` - Facturas

**API REST**:
- ✅ Repositories
- ✅ Serializers
- ✅ Views (básicas)
- ✅ URLs

---

## ⚠️ LO QUE FALTA PARA INTEGRACIÓN COMPLETA

### 1. **Campos de Reserva en Stock** ❌

**PROBLEMA**: ProductStock solo tiene `quantity` (stock total).

**NECESITA**:
```python
# Agregar a ProductStock y SubproductStock
class ProductStock(BaseModel):
    quantity = DecimalField(...)  # Stock TOTAL (físico disponible + reservado)
    quantity_reserved = DecimalField(default=0, ...)  # Stock RESERVADO (pedidos confirmados)

    @property
    def quantity_available(self):
        # Stock LIBRE para nuevos pedidos
        return self.quantity - self.quantity_reserved
```

### 2. **Service de Reservas para Sales Orders** ❌

**PROBLEMA**: `reservations.py` solo calcula reservas de CuttingOrders, NO de SalesOrders.

**NECESITA**:
```python
# Backend-API/apps/stocks/services/sales_reservations.py

@transaction.atomic
def reserve_stock_for_sales_order(sales_order: SalesOrder, user) -> dict:
    """
    Reserva stock al confirmar un pedido de venta.

    Flujo:
    1. Iterar items del pedido
    2. Validar stock disponible (quantity - quantity_reserved >= qty solicitada)
    3. Incrementar ProductStock.quantity_reserved
    4. Crear StockEvent tipo 'reserve_for_sale'
    5. Si falta stock, retornar items problemáticos
    """
    ...

@transaction.atomic
def release_stock_reservation(sales_order: SalesOrder, user) -> None:
    """
    Libera reserva de stock al cancelar pedido.

    Flujo:
    1. Decrementar ProductStock.quantity_reserved
    2. Crear StockEvent tipo 'release_sale_reservation'
    """
    ...

@transaction.atomic
def confirm_stock_movement(sales_order: SalesOrder, shipped_quantities: dict, user) -> None:
    """
    Confirma movimiento de stock al remitar/facturar.

    Flujo:
    1. Decrementar ProductStock.quantity (stock físico)
    2. Decrementar ProductStock.quantity_reserved
    3. Crear StockEvent tipo 'sale_shipment'
    """
    ...
```

### 3. **Integración SalesOrder con Stocks** ❌

**PROBLEMA**: Al crear SalesOrder NO se reserva stock automáticamente.

**NECESITA**:
```python
# Backend-API/apps/sales/services/sales_order_service.py

from apps.stocks.services.sales_reservations import (
    reserve_stock_for_sales_order,
    release_stock_reservation,
    confirm_stock_movement
)

@transaction.atomic
def create_sales_order_with_stock_check(data: dict, user) -> tuple[SalesOrder, dict]:
    """
    Crea pedido de venta CON validación y reserva de stock.

    Returns:
        (sales_order, stock_issues)
        stock_issues = {'product_id': {'requested': X, 'available': Y}}
    """
    # 1. Crear SalesOrder en estado DRAFT
    sales_order = SalesOrder.objects.create(...)

    # 2. Crear SalesOrderItems
    stock_issues = {}
    for item_data in data['items']:
        product = Product.objects.get(id=item_data['product_id'])
        stock = ProductStock.objects.select_for_update().get(product=product)

        # Validar disponibilidad
        available = stock.quantity - stock.quantity_reserved
        requested = Decimal(item_data['quantity'])

        if available < requested:
            stock_issues[product.id] = {
                'requested': requested,
                'available': available,
                'product_name': product.name
            }

        SalesOrderItem.objects.create(
            order=sales_order,
            product=product,
            quantity_ordered=requested,
            ...
        )

    # 3. Si NO hay problemas de stock, confirmar pedido y reservar
    if not stock_issues:
        sales_order.status_label = SalesOrder.Status.CONFIRMED
        sales_order.save(user=user)

        # RESERVAR STOCK
        reserve_stock_for_sales_order(sales_order, user)

    return sales_order, stock_issues

@transaction.atomic
def cancel_sales_order(sales_order_id: int, user):
    """Cancela pedido y libera reservas."""
    sales_order = SalesOrder.objects.select_for_update().get(pk=sales_order_id)

    if sales_order.status_label == SalesOrder.Status.CONFIRMED:
        # Liberar reservas
        release_stock_reservation(sales_order, user)

    sales_order.status_label = SalesOrder.Status.CANCELLED
    sales_order.save(user=user)

@transaction.atomic
def ship_sales_order(sales_order_id: int, shipped_data: dict, user):
    """Remita pedido y descuenta stock real."""
    sales_order = SalesOrder.objects.select_for_update().get(pk=sales_order_id)

    # Confirmar movimiento de stock
    confirm_stock_movement(sales_order, shipped_data, user)

    # Actualizar quantities_shipped en items
    for item in sales_order.items.all():
        shipped_qty = shipped_data.get(item.product_id, 0)
        item.quantity_shipped += shipped_qty
        item.save()

    # Actualizar estado pedido
    total_ordered = sum(i.quantity_ordered for i in sales_order.items.all())
    total_shipped = sum(i.quantity_shipped for i in sales_order.items.all())

    if total_shipped >= total_ordered:
        sales_order.status_label = SalesOrder.Status.COMPLETED
    else:
        sales_order.status_label = SalesOrder.Status.PARTIALLY_SHIPPED

    sales_order.save(user=user)
```

### 4. **Signals para Actualizaciones Automáticas** ❌

**NECESITA**:
```python
# Backend-API/apps/sales/signals.py

from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from apps.sales.models import SalesOrder
from apps.stocks.services.sales_reservations import release_stock_reservation

@receiver(pre_delete, sender=SalesOrder)
def auto_release_stock_on_delete(sender, instance, **kwargs):
    """
    Al eliminar pedido confirmado, liberar reservas automáticamente.
    """
    if instance.status_label == SalesOrder.Status.CONFIRMED:
        # Usuario sistema para operaciones automáticas
        from django.contrib.auth import get_user_model
        User = get_user_model()
        system_user = User.objects.filter(username='system').first()

        if system_user:
            release_stock_reservation(instance, system_user)
```

### 5. **Actualizar Campos Denormalizados en Product** ❌

**NECESITA**:
```python
# Backend-API/apps/products/services/product_sync_service.py

def update_pending_customer_orders(product_id: int):
    """
    Actualiza Product.pending_customer_orders basado en SalesOrderItems confirmados.
    """
    from apps.sales.models import SalesOrderItem, SalesOrder

    product = Product.objects.get(id=product_id)

    # Sumar cantidades de pedidos confirmados que AÚN no se despacharon completamente
    pending = SalesOrderItem.objects.filter(
        product=product,
        order__status_label__in=[
            SalesOrder.Status.CONFIRMED,
            SalesOrder.Status.PARTIALLY_SHIPPED
        ]
    ).aggregate(
        total=Sum(F('quantity_ordered') - F('quantity_shipped'))
    )['total'] or 0

    product.pending_customer_orders = pending
    product.save(update_fields=['pending_customer_orders'])
```

### 6. **Integración con Logistics (Transporte)** ⚠️

**NECESITA** (si no existe):
```python
# Backend-API/apps/logistics/models/carrier.py

class Carrier(BaseModel):
    """Transportista / carrier."""
    legacy_id = IntegerField(null=True, blank=True, db_index=True)
    name = CharField(max_length=255)
    contact_phone = CharField(max_length=50, blank=True)
    contact_email = EmailField(blank=True)
    is_active = BooleanField(default=True)

# Luego en SalesOrder cambiar:
# transport_legacy_id → transport (FK to Carrier)
```

---

## 📋 FLUJOS DE NEGOCIO COMPLETOS

### Flujo 1: Crear Pedido de Venta

```
1. Usuario crea pedido desde frontend
   ↓
2. POST /api/v1/sales/orders/create/
   {
     "customer_id": 123,
     "transport_id": 5,
     "items": [
       {"product_id": 456, "quantity": 10, "unit_price": 100}
     ]
   }
   ↓
3. SalesOrderService.create_sales_order_with_stock_check()
   - Valida stock disponible (quantity - reserved >= requested)
   - Crea SalesOrder en DRAFT
   - Crea SalesOrderItems
   ↓
4. Si stock OK:
   - Cambia estado a CONFIRMED
   - Llama reserve_stock_for_sales_order()
     → ProductStock.quantity_reserved += 10
     → StockEvent tipo 'reserve_for_sale'
   - Actualiza Product.pending_customer_orders
   ↓
5. Si stock INSUFICIENTE:
   - Mantiene en DRAFT
   - Retorna stock_issues al frontend
   - Usuario decide: cancelar o confirmar parcial
```

### Flujo 2: Remitar/Facturar Pedido

```
1. Usuario remita pedido
   ↓
2. POST /api/v1/sales/orders/{id}/ship/
   {
     "items": [
       {"product_id": 456, "quantity_shipped": 10}
     ]
   }
   ↓
3. SalesOrderService.ship_sales_order()
   - Llama confirm_stock_movement()
     → ProductStock.quantity -= 10 (stock físico)
     → ProductStock.quantity_reserved -= 10 (libera reserva)
     → StockEvent tipo 'sale_shipment'
   - Actualiza SalesOrderItem.quantity_shipped
   - Cambia estado a PARTIALLY_SHIPPED o COMPLETED
   ↓
4. Actualiza Product.pending_customer_orders (decrementar)
```

### Flujo 3: Cancelar Pedido

```
1. Usuario cancela pedido confirmado
   ↓
2. POST /api/v1/sales/orders/{id}/cancel/
   ↓
3. SalesOrderService.cancel_sales_order()
   - Llama release_stock_reservation()
     → ProductStock.quantity_reserved -= 10
     → StockEvent tipo 'release_sale_reservation'
   - Cambia estado a CANCELLED
   ↓
4. Actualiza Product.pending_customer_orders = 0
```

---

## 🎯 PLAN DE IMPLEMENTACIÓN

### Fase 1: Modificar Modelos (Migraciones)

```bash
# 1. Agregar quantity_reserved a ProductStock y SubproductStock
python manage.py makemigrations stocks --name add_quantity_reserved

# 2. Agregar FK transport a SalesOrder (opcional)
python manage.py makemigrations sales --name add_transport_fk

# 3. Aplicar migraciones
python manage.py migrate
```

### Fase 2: Crear Services de Integración

```bash
# Crear archivos
touch Backend-API/apps/stocks/services/sales_reservations.py
touch Backend-API/apps/sales/services/sales_order_service.py
touch Backend-API/apps/products/services/product_sync_service.py
touch Backend-API/apps/sales/signals.py
```

### Fase 3: Actualizar Views de Sales

```python
# En apps/sales/api/views/order_views.py
from apps.sales.services.sales_order_service import (
    create_sales_order_with_stock_check,
    cancel_sales_order,
    ship_sales_order
)

@api_view(['POST'])
@permission_classes([IsAuthenticated, CanManageSales])
@extend_schema(**create_sales_order_doc)
def create_sales_order_view(request):
    sales_order, stock_issues = create_sales_order_with_stock_check(
        request.data,
        request.user
    )

    if stock_issues:
        return Response({
            'order': SalesOrderSerializer(sales_order).data,
            'stock_issues': stock_issues,
            'warning': 'Pedido creado en DRAFT. Stock insuficiente para confirmar.'
        }, status=status.HTTP_201_CREATED)

    return Response(
        SalesOrderSerializer(sales_order).data,
        status=status.HTTP_201_CREATED
    )
```

### Fase 4: Tests de Integración

```python
# apps/sales/tests/test_sales_stock_integration.py

def test_create_order_reserves_stock():
    # Dado: producto con stock 100
    product = Product.objects.create(...)
    ProductStock.objects.create(product=product, quantity=100)

    # Cuando: se crea pedido de 10 unidades
    sales_order, _ = create_sales_order_with_stock_check({...}, user)

    # Entonces: stock reservado = 10, disponible = 90
    stock = ProductStock.objects.get(product=product)
    assert stock.quantity_reserved == 10
    assert stock.quantity_available == 90

def test_cancel_order_releases_stock():
    # ... (test de liberación)

def test_ship_order_decrements_physical_stock():
    # ... (test de despacho)
```

### Fase 5: Documentación Completa

```python
# apps/sales/docs/sales_order_doc.py

create_sales_order_doc = {
    "tags": ["Sales"],
    "summary": "Crear pedido de venta",
    "description": """
    Crea un pedido de venta CON validación automática de stock.

    **Flujo**:
    1. Valida stock disponible para cada producto
    2. Si hay stock: crea pedido CONFIRMED y RESERVA stock
    3. Si falta stock: crea pedido DRAFT y retorna stock_issues

    **Integración con Stock**:
    - Incrementa `ProductStock.quantity_reserved`
    - Crea `StockEvent` tipo 'reserve_for_sale'
    - Actualiza `Product.pending_customer_orders`

    **Permisos**: ADMIN, MANAGER, SALES, TRAVELER
    """,
    ...
}
```

---

## ✅ BENEFICIOS DE LA INTEGRACIÓN COMPLETA

1. **Stock en Tiempo Real**: Disponibilidad siempre actualizada
2. **Sin Sobreventa**: Validación automática antes de confirmar pedidos
3. **Reservas Automáticas**: Stock bloqueado para pedidos confirmados
4. **Trazabilidad Total**: StockEvents registran TODO (reservas, liberaciones, despachos)
5. **Reportes Precisos**: Product.pending_customer_orders siempre correcto
6. **Auditoría Completa**: Todos los movimientos con usuario y timestamp
7. **Transacciones Atómicas**: No hay estados inconsistentes

---

## 🚀 PRÓXIMOS PASOS

**¿Qué quieres que implemente primero?**

1. **Opción A**: Modificar modelos (agregar `quantity_reserved`)
2. **Opción B**: Crear services de integración completos
3. **Opción C**: Todo de una vez (modelos + services + views + tests + docs)
4. **Opción D**: Revisar primero otra app (customers, suppliers, etc.)

**Dime cuál opción prefieres y arranco con el desarrollo! 🚀**
