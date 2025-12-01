# App `users` - Sistema de Autenticación y Permisos

## Descripción

Módulo completo de gestión de usuarios con autenticación JWT, permisos granulares por rol, y control de acceso a todos los módulos del sistema.

## Características

✅ **Autenticación JWT** con blacklist de tokens
✅ **8 Roles de usuario** con permisos diferenciados
✅ **CRUD completo** de usuarios con soft delete
✅ **Gestión de imágenes** de perfil en MinIO/S3
✅ **Cache system** con invalidación automática
✅ **WebSocket events** para actualizaciones en tiempo real
✅ **Búsqueda inteligente** case/accent insensitive
✅ **Documentación completa** OpenAPI/Swagger

## Roles Disponibles

| Rol | Código | Descripción | Acceso Principal |
|-----|--------|-------------|------------------|
| Administrador | `ADMIN` | Acceso total al sistema | Todo el sistema |
| Gerente | `MANAGER` | Control módulos operativos | Ventas, compras, manufactura, reportes |
| Vendedor | `SALES` | Gestión comercial | Clientes, presupuestos, pedidos |
| Facturación | `BILLING` | Comprobantes fiscales | Facturas, remitos, tesorería |
| Viajante | `TRAVELER` | Acceso móvil | Clientes, pedidos en ruta |
| Operario | `OPERATOR` | Producción | Órdenes de trabajo, procesos externos |
| Depósito | `WAREHOUSE` | Inventario y logística | Stock, compras, remitos |
| Solo lectura | `READONLY` | Visualización | Todo (sin modificación) |

## Uso del Sistema de Permisos

### Importar Permisos en Views

```python
# En tu archivo de views (ej: apps/sales/api/views/sales_views.py)
from apps.users.permissions import CanManageSales, CanApproveSalesOrders

@api_view(['POST'])
@permission_classes([IsAuthenticated, CanManageSales])
def create_sales_order(request):
    # Solo ADMIN, MANAGER, SALES, TRAVELER pueden crear pedidos
    ...

@api_view(['POST'])
@permission_classes([IsAuthenticated, CanApproveSalesOrders])
def approve_sales_order(request, pk):
    # Solo ADMIN y MANAGER pueden aprobar pedidos
    ...
```

### Permisos Disponibles por Módulo

#### Usuarios (`users`)
- `CanManageUsers` - CRUD usuarios (solo ADMIN)
- `CanViewUsers` - Ver usuarios (ADMIN, MANAGER, READONLY)

#### Productos (`products`)
- `CanManageProducts` - CRUD productos (ADMIN, MANAGER, WAREHOUSE*)
- `CanViewProducts` - Ver productos (Todos los roles)

*WAREHOUSE puede actualizar, no crear/eliminar

#### Clientes (`customers`)
- `CanManageCustomers` - CRUD clientes (ADMIN, MANAGER, SALES*, TRAVELER*)
- `CanViewCustomers` - Ver clientes (Todos menos OPERATOR)

*SALES puede crear/actualizar, TRAVELER solo actualizar

#### Proveedores (`suppliers`)
- `CanManageSuppliers` - CRUD proveedores (ADMIN, MANAGER, WAREHOUSE*)

*WAREHOUSE solo puede actualizar

#### Ventas (`sales`)
- `CanManageSales` - CRUD ventas (ADMIN, MANAGER, SALES, TRAVELER)
- `CanApproveSalesOrders` - Aprobar pedidos (ADMIN, MANAGER)

#### Compras (`purchases`)
- `CanManagePurchases` - CRUD compras (ADMIN, MANAGER, WAREHOUSE)
- `CanReceivePurchases` - Recibir mercadería (ADMIN, MANAGER, WAREHOUSE)

#### Facturación (`billing`)
- `CanManageBilling` - CRUD facturas (ADMIN, MANAGER, BILLING)
- `CanViewBilling` - Ver facturas (ADMIN, MANAGER, BILLING, SALES, READONLY)

#### Remitos (`delivery_notes`)
- `CanManageDeliveryNotes` - CRUD remitos (ADMIN, MANAGER, WAREHOUSE)

#### Stock (`stocks`, `inventory_adjustments`)
- `CanManageStock` - Gestión stock (ADMIN, MANAGER, WAREHOUSE*)
- `CanMakeInventoryAdjustments` - Crear ajustes (ADMIN, MANAGER, WAREHOUSE)
- `CanViewStockHistory` - Ver histórico (Todos menos TRAVELER)

*WAREHOUSE puede ver/actualizar, no eliminar

#### Manufactura (`manufacturing`, `manufacturing_pro`)
- `CanManageManufacturing` - CRUD manufactura (ADMIN, MANAGER, OPERATOR*)
- `CanManageExternalProcesses` - Procesos externos (ADMIN, MANAGER, OPERATOR)
- `CanManageSupplies` - CRUD insumos (ADMIN, MANAGER, WAREHOUSE*, OPERATOR**)

*OPERATOR puede ver/actualizar, **OPERATOR solo lectura en insumos

#### Órdenes de Corte (`cuts`)
- `CanManageCuttingOrders` - CRUD órdenes corte (ADMIN, MANAGER, OPERATOR*)

*OPERATOR puede ver/actualizar estado

#### Gastos (`expenses`)
- `CanManageExpenses` - CRUD gastos (ADMIN, MANAGER, BILLING*)

*BILLING puede crear/ver, no actualizar/eliminar

#### Tesorería (`treasury`)
- `CanManageTreasury` - CRUD tesorería (ADMIN, MANAGER, BILLING*)

*BILLING puede crear/ver recibos

#### Contabilidad (`accounting`)
- `CanManageAccounting` - CRUD asientos (ADMIN, MANAGER, BILLING*)

*BILLING solo lectura

#### Reportes
- `CanViewReports` - Reportes generales (ADMIN, MANAGER, BILLING, SALES, WAREHOUSE, READONLY)
- `CanViewFinancialReports` - Reportes financieros (ADMIN, MANAGER, BILLING)

### Uso de Helper `user_can()`

Para verificaciones programáticas fuera de decoradores:

```python
# En servicios o lógica de negocio
from apps.users.permissions import user_can

def some_business_logic(user, product_id):
    # Verificar si usuario puede crear productos
    if not user_can(user, 'products', 'create'):
        raise PermissionDenied("No tienes permiso para crear productos")

    # Lógica de creación
    ...

# En views con lógica condicional
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def conditional_action(request):
    if user_can(request.user, 'sales', 'approve'):
        # Aprobar pedido
        ...
    else:
        # Solo crear pedido sin aprobar
        ...
```

### Acciones Disponibles

Las acciones soportadas por `user_can()` son:
- `create` - Crear nuevos registros
- `read` - Ver/listar registros
- `update` - Actualizar registros existentes
- `delete` - Eliminar registros
- `approve` - Aprobar/rechazar (módulos específicos)

### Ejemplo Completo: View con Permisos Diferenciados

```python
# apps/inventory_adjustments/api/views/adjustment_views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.users.permissions import (
    CanMakeInventoryAdjustments,
    CanViewStockHistory,
    user_can
)
from apps.users.models.user_model import User

@api_view(['GET'])
@permission_classes([IsAuthenticated, CanViewStockHistory])
def list_inventory_adjustments(request):
    """
    Listar ajustes de inventario
    Acceso: ADMIN, MANAGER, WAREHOUSE, READONLY
    """
    adjustments = InventoryAdjustment.objects.filter(is_active=True)
    serializer = AdjustmentSerializer(adjustments, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, CanMakeInventoryAdjustments])
def create_inventory_adjustment(request):
    """
    Crear ajuste de inventario
    Acceso: ADMIN, MANAGER, WAREHOUSE

    Nota: WAREHOUSE crea ajustes pendientes de aprobación
    """
    serializer = AdjustmentCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # WAREHOUSE crea en estado PENDING, ADMIN/MANAGER en APPROVED
    initial_status = 'PENDING'
    if request.user.role in [User.Role.ADMIN, User.Role.MANAGER]:
        initial_status = 'APPROVED'

    adjustment = serializer.save(
        created_by=request.user,
        status=initial_status
    )

    return Response(
        AdjustmentSerializer(adjustment).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_inventory_adjustment(request, pk):
    """
    Actualizar ajuste de inventario
    Acceso: Solo ADMIN y MANAGER pueden actualizar/aprobar
    """
    # Verificación manual de permisos
    if not user_can(request.user, 'inventory_adjustments', 'update'):
        return Response(
            {"detail": "No tienes permiso para actualizar ajustes"},
            status=status.HTTP_403_FORBIDDEN
        )

    adjustment = get_object_or_404(InventoryAdjustment, pk=pk)
    serializer = AdjustmentUpdateSerializer(
        adjustment,
        data=request.data,
        partial=True
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data)
```

## Endpoints Documentados

Todos los endpoints están completamente documentados con OpenAPI 3.0 en `apps/users/docs/user_doc.py`.

**Para ver la documentación interactiva**:
```bash
# Ejecutar servidor
python manage.py runserver

# Acceder a Swagger UI
http://localhost:8000/api/schema/swagger-ui/

# Acceder a Redoc
http://localhost:8000/api/schema/redoc/
```

### Endpoints Disponibles

**Autenticación**:
- `POST /api/v1/users/login/` - Login con JWT
- `POST /api/v1/users/logout/` - Logout (blacklist token)
- `POST /api/v1/users/register/` - Crear usuario (Admin only)
- `POST /api/v1/users/password-reset/confirm/<uidb64>/<token>/` - Reset contraseña

**Gestión de Usuarios**:
- `GET /api/v1/users/profile/` - Perfil del usuario autenticado
- `GET /api/v1/users/list/` - Listar usuarios (paginado, filtrado)
- `GET /api/v1/users/lookup/?q=nombre` - Búsqueda rápida
- `GET /api/v1/users/<id>/` - Detalle de usuario
- `PUT /api/v1/users/<id>/` - Actualizar usuario
- `DELETE /api/v1/users/<id>/` - Soft delete usuario

**Imágenes de Perfil**:
- `PUT /api/v1/users/image/<file_id>/replace/` - Reemplazar imagen
- `DELETE /api/v1/users/image/<file_id>/delete/` - Eliminar imagen

## Testing

```bash
# Ejecutar tests de users
python manage.py test apps.users

# Con pytest
pytest apps/users/tests/
```

## Cache

El módulo usa cache Redis con invalidación automática:

```python
# Cache se invalida automáticamente en:
# - Creación de usuario
# - Actualización de usuario
# - Eliminación de usuario

# Invalidación manual si es necesario:
from apps.users.utils.cache_invalidation import invalidate_user_cache
invalidate_user_cache(user_id=123)
```

## WebSocket Events

Al crear/actualizar/eliminar usuarios, se emiten eventos WebSocket al grupo `crud_events`:

```json
{
  "type": "crud_event",
  "data": {
    "model": "User",
    "action": "created|updated|deleted",
    "id": 123,
    "data": { /* serialized user object */ }
  }
}
```

El frontend puede escuchar estos eventos para actualizar la UI en tiempo real.

## Consideraciones de Seguridad

1. **Soft Delete**: Los usuarios nunca se eliminan físicamente, se marcan como `is_deleted=True`
2. **Token Blacklist**: Los refresh tokens se invalidan al hacer logout
3. **Historical Records**: Todos los cambios se registran vía django-simple-history
4. **Permisos Granulares**: Cada rol tiene permisos específicos por módulo
5. **Field Restrictions**: Usuarios no-admin no pueden cambiar campos sensibles (role, is_staff, etc.)
6. **Image Security**: Solo el usuario o admin pueden modificar imagen de perfil

## Migración desde VFP9

Si necesitas migrar usuarios desde el sistema VFP9:

```bash
# Crear migration command
python manage.py migrate_users --source mysql_vfp9 --batch-size 1000

# Mapear tabla 'usuarios' de VFP9:
# usu_codi -> no necesario (nuevo PK en Django)
# usu_nombre -> username
# usu_email -> email
# usu_nombre_completo -> name + last_name (split)
# usu_rol -> role (mapeo de códigos)
# usu_activo -> is_active
```

## Troubleshooting

**Error: "Token inválido o expirado"**
- Verificar que djangorestframework-simplejwt esté instalado
- Verificar configuración de `SIMPLE_JWT` en settings
- Revisar que el token no esté en blacklist

**Error: "No tienes permiso"**
- Verificar que el usuario tenga el rol correcto
- Verificar que el permiso esté asignado al rol en `permissions.py`
- Verificar que el decorador `@permission_classes` esté aplicado

**Error: "Usuario no encontrado"**
- Verificar que el usuario no esté marcado como `is_deleted=True`
- Verificar que `is_active=True`

## Contacto

Para preguntas sobre el módulo users, contactar al equipo de desarrollo.
