"""
Sistema de Permisos por ROL para ERP-Web

Define qué roles pueden acceder a qué módulos y qué acciones pueden realizar.
Los permisos se verifican mediante clases de DRF Permission que pueden usarse
en views como @permission_classes([IsAdminOrManager, CanManageSales])

Roles disponibles:
- ADMIN: Acceso total al sistema
- MANAGER: Control sobre módulos operativos
- SALES: Gestión de ventas y presupuestos
- BILLING: Facturación y documentación fiscal
- TRAVELER: Acceso móvil a clientes y pedidos
- OPERATOR: Ejecución de órdenes de producción
- WAREHOUSE: Control de inventario y logística
- READONLY: Solo lectura en todos los módulos
"""

from rest_framework.permissions import BasePermission
from apps.users.models.user_model import User


# ============================================================================
# PERMISOS BASE POR ROL
# ============================================================================

class IsAdmin(BasePermission):
    """Solo usuarios con rol ADMIN"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.ADMIN


class IsAdminOrManager(BasePermission):
    """Usuarios con rol ADMIN o MANAGER"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.ADMIN,
            User.Role.MANAGER
        ]


class IsReadOnly(BasePermission):
    """Permite solo lectura (GET, HEAD, OPTIONS)"""
    def has_permission(self, request, view):
        return request.method in ['GET', 'HEAD', 'OPTIONS']


# ============================================================================
# PERMISOS: GESTIÓN DE USUARIOS
# ============================================================================

class CanManageUsers(BasePermission):
    """
    Gestión completa de usuarios (CRUD)
    - ADMIN: Acceso total
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.ADMIN


class CanViewUsers(BasePermission):
    """
    Ver listado y detalle de usuarios
    - ADMIN, MANAGER: Acceso completo
    - READONLY: Solo lectura
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.ADMIN,
            User.Role.MANAGER,
            User.Role.READONLY
        ]


# ============================================================================
# PERMISOS: PRODUCTOS (products)
# ============================================================================

class CanManageProducts(BasePermission):
    """
    Gestión completa de productos, categorías y subproductos
    - ADMIN: Acceso total
    - MANAGER: Acceso total
    - WAREHOUSE: Puede actualizar stock y ver productos
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # ADMIN y MANAGER pueden todo
        if request.user.role in [User.Role.ADMIN, User.Role.MANAGER]:
            return True

        # WAREHOUSE solo puede leer y actualizar (no crear/eliminar)
        if request.user.role == User.Role.WAREHOUSE:
            return request.method in ['GET', 'PUT', 'PATCH']

        return False


class CanViewProducts(BasePermission):
    """
    Ver productos y categorías
    - Todos los roles excepto READONLY tienen acceso
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.ADMIN,
            User.Role.MANAGER,
            User.Role.SALES,
            User.Role.BILLING,
            User.Role.TRAVELER,
            User.Role.OPERATOR,
            User.Role.WAREHOUSE,
            User.Role.READONLY
        ]


# ============================================================================
# PERMISOS: CLIENTES (customers)
# ============================================================================

class CanManageCustomers(BasePermission):
    """
    Gestión completa de clientes
    - ADMIN: Acceso total
    - MANAGER: Acceso total
    - SALES: Puede crear y actualizar clientes
    - TRAVELER: Puede actualizar clientes (datos de contacto, notas)
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # ADMIN y MANAGER pueden todo
        if request.user.role in [User.Role.ADMIN, User.Role.MANAGER]:
            return True

        # SALES puede crear, leer y actualizar (no eliminar)
        if request.user.role == User.Role.SALES:
            return request.method in ['GET', 'POST', 'PUT', 'PATCH']

        # TRAVELER solo puede leer y actualizar
        if request.user.role == User.Role.TRAVELER:
            return request.method in ['GET', 'PUT', 'PATCH']

        return False


class CanViewCustomers(BasePermission):
    """Ver clientes - Todos menos OPERATOR"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.ADMIN,
            User.Role.MANAGER,
            User.Role.SALES,
            User.Role.BILLING,
            User.Role.TRAVELER,
            User.Role.WAREHOUSE,
            User.Role.READONLY
        ]


# ============================================================================
# PERMISOS: PROVEEDORES (suppliers)
# ============================================================================

class CanManageSuppliers(BasePermission):
    """
    Gestión de proveedores
    - ADMIN: Acceso total
    - MANAGER: Acceso total
    - WAREHOUSE: Puede actualizar (contacto, notas)
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role in [User.Role.ADMIN, User.Role.MANAGER]:
            return True

        if request.user.role == User.Role.WAREHOUSE:
            return request.method in ['GET', 'PUT', 'PATCH']

        return False


# ============================================================================
# PERMISOS: VENTAS (sales, presupuestos, pedidos)
# ============================================================================

class CanManageSales(BasePermission):
    """
    Gestión de presupuestos y pedidos de venta
    - ADMIN, MANAGER: Acceso total
    - SALES: Puede crear, actualizar y ver
    - TRAVELER: Puede crear y actualizar pedidos
    - BILLING: Solo lectura
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # ADMIN y MANAGER pueden todo
        if request.user.role in [User.Role.ADMIN, User.Role.MANAGER]:
            return True

        # SALES puede crear, leer y actualizar (no eliminar)
        if request.user.role == User.Role.SALES:
            return request.method in ['GET', 'POST', 'PUT', 'PATCH']

        # TRAVELER puede crear, leer y actualizar
        if request.user.role == User.Role.TRAVELER:
            return request.method in ['GET', 'POST', 'PUT', 'PATCH']

        # BILLING solo puede leer
        if request.user.role == User.Role.BILLING:
            return request.method == 'GET'

        return False


class CanApproveSalesOrders(BasePermission):
    """
    Aprobar/rechazar pedidos de venta
    - ADMIN, MANAGER: Pueden aprobar
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.ADMIN,
            User.Role.MANAGER
        ]


# ============================================================================
# PERMISOS: COMPRAS (purchases)
# ============================================================================

class CanManagePurchases(BasePermission):
    """
    Gestión de órdenes de compra
    - ADMIN, MANAGER: Acceso total
    - WAREHOUSE: Puede crear y actualizar órdenes
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role in [User.Role.ADMIN, User.Role.MANAGER]:
            return True

        if request.user.role == User.Role.WAREHOUSE:
            return request.method in ['GET', 'POST', 'PUT', 'PATCH']

        return False


class CanReceivePurchases(BasePermission):
    """
    Recibir mercadería (PurchaseReceipt)
    - ADMIN, MANAGER, WAREHOUSE
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.ADMIN,
            User.Role.MANAGER,
            User.Role.WAREHOUSE
        ]


# ============================================================================
# PERMISOS: FACTURACIÓN (billing)
# ============================================================================

class CanManageBilling(BasePermission):
    """
    Gestión de facturas, notas de crédito/débito
    - ADMIN, MANAGER: Acceso total
    - BILLING: Puede crear, leer y actualizar
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role in [User.Role.ADMIN, User.Role.MANAGER]:
            return True

        if request.user.role == User.Role.BILLING:
            return request.method in ['GET', 'POST', 'PUT', 'PATCH']

        return False


class CanViewBilling(BasePermission):
    """Ver facturas - ADMIN, MANAGER, BILLING, SALES, READONLY"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.ADMIN,
            User.Role.MANAGER,
            User.Role.BILLING,
            User.Role.SALES,
            User.Role.READONLY
        ]


# ============================================================================
# PERMISOS: REMITOS (delivery_notes)
# ============================================================================

class CanManageDeliveryNotes(BasePermission):
    """
    Gestión de remitos
    - ADMIN, MANAGER: Acceso total
    - WAREHOUSE: Puede crear y actualizar
    - BILLING: Solo lectura
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role in [User.Role.ADMIN, User.Role.MANAGER]:
            return True

        if request.user.role == User.Role.WAREHOUSE:
            return request.method in ['GET', 'POST', 'PUT', 'PATCH']

        if request.user.role == User.Role.BILLING:
            return request.method == 'GET'

        return False


# ============================================================================
# PERMISOS: STOCK (stocks, inventory_adjustments)
# ============================================================================

class CanManageStock(BasePermission):
    """
    Gestión de stock (movimientos, ajustes)
    - ADMIN, MANAGER: Acceso total
    - WAREHOUSE: Puede ver y actualizar stock
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role in [User.Role.ADMIN, User.Role.MANAGER]:
            return True

        if request.user.role == User.Role.WAREHOUSE:
            return request.method in ['GET', 'PUT', 'PATCH']

        return False


class CanMakeInventoryAdjustments(BasePermission):
    """
    Crear ajustes de inventario (inventory_adjustments)
    - ADMIN, MANAGER: Pueden crear ajustes
    - WAREHOUSE: Puede crear ajustes (con aprobación posterior)
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.ADMIN,
            User.Role.MANAGER,
            User.Role.WAREHOUSE
        ]


class CanViewStockHistory(BasePermission):
    """
    Ver histórico de movimientos de stock
    - Todos excepto TRAVELER pueden ver
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.ADMIN,
            User.Role.MANAGER,
            User.Role.SALES,
            User.Role.BILLING,
            User.Role.OPERATOR,
            User.Role.WAREHOUSE,
            User.Role.READONLY
        ]


# ============================================================================
# PERMISOS: MANUFACTURA (manufacturing, manufacturing_pro)
# ============================================================================

class CanManageManufacturing(BasePermission):
    """
    Gestión de órdenes de manufactura, BOM, work orders
    - ADMIN, MANAGER: Acceso total
    - OPERATOR: Puede ver y actualizar estado de órdenes
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role in [User.Role.ADMIN, User.Role.MANAGER]:
            return True

        if request.user.role == User.Role.OPERATOR:
            return request.method in ['GET', 'PUT', 'PATCH']

        return False


class CanManageExternalProcesses(BasePermission):
    """
    Gestión de procesos externos (galvanizado, pintura, etc.)
    - ADMIN, MANAGER: Acceso total
    - OPERATOR: Puede ver y registrar recepciones
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role in [User.Role.ADMIN, User.Role.MANAGER]:
            return True

        if request.user.role == User.Role.OPERATOR:
            return request.method in ['GET', 'POST', 'PUT', 'PATCH']

        return False


class CanManageSupplies(BasePermission):
    """
    Gestión de insumos (manufacturing_pro)
    - ADMIN, MANAGER: Acceso total
    - WAREHOUSE: Puede ver y actualizar stock
    - OPERATOR: Solo lectura
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role in [User.Role.ADMIN, User.Role.MANAGER]:
            return True

        if request.user.role == User.Role.WAREHOUSE:
            return request.method in ['GET', 'PUT', 'PATCH']

        if request.user.role == User.Role.OPERATOR:
            return request.method == 'GET'

        return False


# ============================================================================
# PERMISOS: ÓRDENES DE CORTE (cuts)
# ============================================================================

class CanManageCuttingOrders(BasePermission):
    """
    Gestión de órdenes de corte
    - ADMIN, MANAGER: Acceso total
    - OPERATOR: Puede ver y actualizar estado
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role in [User.Role.ADMIN, User.Role.MANAGER]:
            return True

        if request.user.role == User.Role.OPERATOR:
            return request.method in ['GET', 'PUT', 'PATCH']

        return False


# ============================================================================
# PERMISOS: GASTOS (expenses)
# ============================================================================

class CanManageExpenses(BasePermission):
    """
    Gestión de gastos
    - ADMIN, MANAGER: Acceso total
    - BILLING: Puede crear y ver
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role in [User.Role.ADMIN, User.Role.MANAGER]:
            return True

        if request.user.role == User.Role.BILLING:
            return request.method in ['GET', 'POST']

        return False


# ============================================================================
# PERMISOS: TESORERÍA (treasury)
# ============================================================================

class CanManageTreasury(BasePermission):
    """
    Gestión de bancos, recibos, pagos, cobranzas
    - ADMIN, MANAGER: Acceso total
    - BILLING: Puede ver y crear recibos
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role in [User.Role.ADMIN, User.Role.MANAGER]:
            return True

        if request.user.role == User.Role.BILLING:
            return request.method in ['GET', 'POST']

        return False


# ============================================================================
# PERMISOS: CONTABILIDAD (accounting, financial)
# ============================================================================

class CanManageAccounting(BasePermission):
    """
    Gestión de asientos contables y libro mayor
    - ADMIN, MANAGER: Acceso total
    - BILLING: Solo lectura
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role in [User.Role.ADMIN, User.Role.MANAGER]:
            return True

        if request.user.role == User.Role.BILLING:
            return request.method == 'GET'

        return False


# ============================================================================
# PERMISOS: REPORTES Y MÉTRICAS
# ============================================================================

class CanViewReports(BasePermission):
    """
    Ver reportes y métricas
    - ADMIN, MANAGER, BILLING: Acceso completo
    - SALES, WAREHOUSE: Reportes de su área
    - READONLY: Solo lectura de todo
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.ADMIN,
            User.Role.MANAGER,
            User.Role.BILLING,
            User.Role.SALES,
            User.Role.WAREHOUSE,
            User.Role.READONLY
        ]


class CanViewFinancialReports(BasePermission):
    """
    Ver reportes financieros (P&L, balance, flujo de caja)
    - ADMIN, MANAGER: Acceso completo
    - BILLING: Solo lectura
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.ADMIN,
            User.Role.MANAGER,
            User.Role.BILLING
        ]


# ============================================================================
# HELPER: Verificar permisos por acción y módulo
# ============================================================================

def user_can(user, module: str, action: str) -> bool:
    """
    Verifica si un usuario puede realizar una acción en un módulo específico.

    Args:
        user: Instancia de User
        module: Nombre del módulo ('sales', 'products', 'manufacturing', etc.)
        action: Acción ('create', 'read', 'update', 'delete', 'approve', etc.)

    Returns:
        bool: True si el usuario tiene permiso, False en caso contrario

    Ejemplo:
        if user_can(request.user, 'sales', 'create'):
            # Permitir crear pedido de venta
            ...
    """
    # Mapa de permisos por módulo y acción
    PERMISSION_MAP = {
        'users': {
            'create': [User.Role.ADMIN],
            'read': [User.Role.ADMIN, User.Role.MANAGER, User.Role.READONLY],
            'update': [User.Role.ADMIN],
            'delete': [User.Role.ADMIN],
        },
        'products': {
            'create': [User.Role.ADMIN, User.Role.MANAGER],
            'read': [User.Role.ADMIN, User.Role.MANAGER, User.Role.SALES, User.Role.BILLING,
                     User.Role.TRAVELER, User.Role.OPERATOR, User.Role.WAREHOUSE, User.Role.READONLY],
            'update': [User.Role.ADMIN, User.Role.MANAGER, User.Role.WAREHOUSE],
            'delete': [User.Role.ADMIN, User.Role.MANAGER],
        },
        'customers': {
            'create': [User.Role.ADMIN, User.Role.MANAGER, User.Role.SALES],
            'read': [User.Role.ADMIN, User.Role.MANAGER, User.Role.SALES, User.Role.BILLING,
                     User.Role.TRAVELER, User.Role.WAREHOUSE, User.Role.READONLY],
            'update': [User.Role.ADMIN, User.Role.MANAGER, User.Role.SALES, User.Role.TRAVELER],
            'delete': [User.Role.ADMIN, User.Role.MANAGER],
        },
        'suppliers': {
            'create': [User.Role.ADMIN, User.Role.MANAGER],
            'read': [User.Role.ADMIN, User.Role.MANAGER, User.Role.WAREHOUSE, User.Role.READONLY],
            'update': [User.Role.ADMIN, User.Role.MANAGER, User.Role.WAREHOUSE],
            'delete': [User.Role.ADMIN, User.Role.MANAGER],
        },
        'sales': {
            'create': [User.Role.ADMIN, User.Role.MANAGER, User.Role.SALES, User.Role.TRAVELER],
            'read': [User.Role.ADMIN, User.Role.MANAGER, User.Role.SALES, User.Role.TRAVELER,
                     User.Role.BILLING, User.Role.READONLY],
            'update': [User.Role.ADMIN, User.Role.MANAGER, User.Role.SALES, User.Role.TRAVELER],
            'delete': [User.Role.ADMIN, User.Role.MANAGER],
            'approve': [User.Role.ADMIN, User.Role.MANAGER],
        },
        'purchases': {
            'create': [User.Role.ADMIN, User.Role.MANAGER, User.Role.WAREHOUSE],
            'read': [User.Role.ADMIN, User.Role.MANAGER, User.Role.WAREHOUSE, User.Role.READONLY],
            'update': [User.Role.ADMIN, User.Role.MANAGER, User.Role.WAREHOUSE],
            'delete': [User.Role.ADMIN, User.Role.MANAGER],
        },
        'billing': {
            'create': [User.Role.ADMIN, User.Role.MANAGER, User.Role.BILLING],
            'read': [User.Role.ADMIN, User.Role.MANAGER, User.Role.BILLING, User.Role.SALES, User.Role.READONLY],
            'update': [User.Role.ADMIN, User.Role.MANAGER, User.Role.BILLING],
            'delete': [User.Role.ADMIN, User.Role.MANAGER],
        },
        'delivery_notes': {
            'create': [User.Role.ADMIN, User.Role.MANAGER, User.Role.WAREHOUSE],
            'read': [User.Role.ADMIN, User.Role.MANAGER, User.Role.WAREHOUSE, User.Role.BILLING, User.Role.READONLY],
            'update': [User.Role.ADMIN, User.Role.MANAGER, User.Role.WAREHOUSE],
            'delete': [User.Role.ADMIN, User.Role.MANAGER],
        },
        'stocks': {
            'create': [User.Role.ADMIN, User.Role.MANAGER, User.Role.WAREHOUSE],
            'read': [User.Role.ADMIN, User.Role.MANAGER, User.Role.SALES, User.Role.BILLING,
                     User.Role.OPERATOR, User.Role.WAREHOUSE, User.Role.READONLY],
            'update': [User.Role.ADMIN, User.Role.MANAGER, User.Role.WAREHOUSE],
            'delete': [User.Role.ADMIN, User.Role.MANAGER],
        },
        'inventory_adjustments': {
            'create': [User.Role.ADMIN, User.Role.MANAGER, User.Role.WAREHOUSE],
            'read': [User.Role.ADMIN, User.Role.MANAGER, User.Role.WAREHOUSE, User.Role.READONLY],
            'update': [User.Role.ADMIN, User.Role.MANAGER],
            'delete': [User.Role.ADMIN],
        },
        'manufacturing': {
            'create': [User.Role.ADMIN, User.Role.MANAGER],
            'read': [User.Role.ADMIN, User.Role.MANAGER, User.Role.OPERATOR, User.Role.WAREHOUSE, User.Role.READONLY],
            'update': [User.Role.ADMIN, User.Role.MANAGER, User.Role.OPERATOR],
            'delete': [User.Role.ADMIN, User.Role.MANAGER],
        },
        'external_processes': {
            'create': [User.Role.ADMIN, User.Role.MANAGER, User.Role.OPERATOR],
            'read': [User.Role.ADMIN, User.Role.MANAGER, User.Role.OPERATOR, User.Role.WAREHOUSE, User.Role.READONLY],
            'update': [User.Role.ADMIN, User.Role.MANAGER, User.Role.OPERATOR],
            'delete': [User.Role.ADMIN, User.Role.MANAGER],
        },
        'supplies': {
            'create': [User.Role.ADMIN, User.Role.MANAGER],
            'read': [User.Role.ADMIN, User.Role.MANAGER, User.Role.OPERATOR, User.Role.WAREHOUSE, User.Role.READONLY],
            'update': [User.Role.ADMIN, User.Role.MANAGER, User.Role.WAREHOUSE],
            'delete': [User.Role.ADMIN, User.Role.MANAGER],
        },
        'cuts': {
            'create': [User.Role.ADMIN, User.Role.MANAGER],
            'read': [User.Role.ADMIN, User.Role.MANAGER, User.Role.OPERATOR, User.Role.READONLY],
            'update': [User.Role.ADMIN, User.Role.MANAGER, User.Role.OPERATOR],
            'delete': [User.Role.ADMIN, User.Role.MANAGER],
        },
        'expenses': {
            'create': [User.Role.ADMIN, User.Role.MANAGER, User.Role.BILLING],
            'read': [User.Role.ADMIN, User.Role.MANAGER, User.Role.BILLING, User.Role.READONLY],
            'update': [User.Role.ADMIN, User.Role.MANAGER],
            'delete': [User.Role.ADMIN, User.Role.MANAGER],
        },
        'treasury': {
            'create': [User.Role.ADMIN, User.Role.MANAGER, User.Role.BILLING],
            'read': [User.Role.ADMIN, User.Role.MANAGER, User.Role.BILLING, User.Role.READONLY],
            'update': [User.Role.ADMIN, User.Role.MANAGER],
            'delete': [User.Role.ADMIN, User.Role.MANAGER],
        },
        'accounting': {
            'create': [User.Role.ADMIN, User.Role.MANAGER],
            'read': [User.Role.ADMIN, User.Role.MANAGER, User.Role.BILLING, User.Role.READONLY],
            'update': [User.Role.ADMIN, User.Role.MANAGER],
            'delete': [User.Role.ADMIN],
        },
    }

    if module not in PERMISSION_MAP:
        return False

    if action not in PERMISSION_MAP[module]:
        return False

    return user.role in PERMISSION_MAP[module][action]
