# ANÁLISIS COMPLETO: App `users`

## ✅ LO QUE YA ESTÁ IMPLEMENTADO

### Modelo `User` (`apps/users/models/user_model.py`)

**Características**:
- ✅ Hereda de `AbstractBaseUser` y `PermissionsMixin`
- ✅ Custom `UserManager` con `create_user` y `create_superuser`
- ✅ Campos principales:
  - `username` (unique, indexed)
  - `email` (unique, indexed)
  - `name`, `last_name`
  - `phone`, `dni` (unique, indexed, optional)
  - `image` (ruta S3/MinIO para foto de perfil)
  - `is_active`, `is_staff`, `is_deleted` (soft delete)
  - `role` (TextChoices con 8 roles)
- ✅ **Roles disponibles**:
  - ADMIN (Administrador)
  - MANAGER (Gerente)
  - SALES (Vendedor)
  - BILLING (Facturación)
  - TRAVELER (Viajante)
  - OPERATOR (Operario)
  - WAREHOUSE (Depósito/Logística)
  - READONLY (Solo lectura)
- ✅ `HistoricalRecords` habilitado (django-simple-history)
- ✅ `created_at` timestamp

**USERNAME_FIELD**: `username`
**REQUIRED_FIELDS**: `email`, `name`, `last_name`

### API Completa (`apps/users/api/`)

#### **Views Implementadas**:

**Autenticación** (`views/auth.py`):
- ✅ `POST /api/v1/users/login/` - Login con JWT (CustomTokenObtainPairView)
- ✅ `POST /api/v1/users/logout/` - Logout con blacklist de refresh token

**Gestión de Usuarios** (`views/user.py`):
- ✅ `GET /api/v1/users/profile/` - Perfil del usuario autenticado
- ✅ `GET /api/v1/users/list/` - Listar usuarios (Admin only, paginado, filtrado, **cacheado**)
- ✅ `POST /api/v1/users/register/` - Crear usuario (Admin only)
- ✅ `GET /api/v1/users/<id>/` - Detalle de usuario (Admin o self)
- ✅ `PUT /api/v1/users/<id>/` - Actualizar usuario (Admin o self con restricciones)
- ✅ `DELETE /api/v1/users/<id>/` - Soft delete de usuario (Admin only)
- ✅ `GET /api/v1/users/lookup/?q=nombre` - Búsqueda ligera (case/accent insensitive)

**Gestión de Imágenes** (`views/user.py`):
- ✅ `PUT /api/v1/users/image/<file_id>/replace/` - Reemplazar imagen de perfil
- ✅ `DELETE /api/v1/users/image/<file_id>/delete/` - Eliminar imagen de perfil
- ✅ `DELETE /api/v1/users/image/delete/?file_path=...` - Eliminar por query param

**Password Reset** (`views/reset_password.py`):
- ✅ `POST /api/v1/users/password-reset/confirm/<uidb64>/<token>/` - Confirmar reset de contraseña

#### **Serializers Organizados**:
- ✅ `UserBaseSerializer` - Campos base
- ✅ `UserDetailSerializer` - Detalle completo con URL de imagen presignada
- ✅ `UserCreateSerializer` - Creación con validaciones
- ✅ `UserUpdateSerializer` - Actualización parcial
- ✅ `CustomTokenObtainPairSerializer` - JWT con claims custom
- ✅ `PasswordResetSerializer` - Reset de contraseña

#### **Repository Pattern**:
- ✅ `UserRepository` (`api/repositories/user_repository.py`)
  - `get_all_active_users()` - Optimizado con select_related
  - `get_by_id(pk)` - Obtener usuario activo por ID
  - `soft_delete(user)` - Marcar como deleted sin borrar

#### **Filtros**:
- ✅ `UserFilter` (`filters.py`) - django-filter para búsquedas avanzadas

#### **Cache System** (`utils/`):
- ✅ `cache_decorators.py` - Decorators `@list_cache`, `@detail_cache`
- ✅ `cache_keys.py` - Generación de claves de cache
- ✅ `cache_invalidation.py` - `invalidate_user_cache(user_id)`

#### **Documentación**:
- ✅ `docs/user_doc.py` - Documentación drf-spectacular para cada endpoint

### Características Avanzadas

**1. Integración con MinIO/S3**:
- Upload de imágenes de perfil con URLs presignadas
- Replace de imagen existente
- Delete de imagen con cleanup automático

**2. WebSocket Events**:
- Emite eventos CRUD vía `broadcast_crud_event` en:
  - Creación de usuario
  - Actualización de usuario
  - Eliminación de usuario

**3. Permisos Granulares**:
- Admin puede hacer todo
- Usuario puede ver/editar solo su perfil
- Usuario no-admin tiene campos restringidos (no puede cambiar `role`, `is_staff`, etc.)

**4. Cache Estratégico**:
- Lista de usuarios cacheada (reduce queries en listados frecuentes)
- Invalidación automática en create/update/delete
- Headers `X-Invalidate-Users-Cache` para señalizar al frontend

**5. Búsqueda Inteligente**:
- `user_lookup_view` soporta búsqueda case-insensitive y accent-insensitive
- Detecta si Postgres tiene extension `unaccent` habilitada
- Fallback a normalización NFD si no hay unaccent

**6. Seguridad**:
- JWT con blacklist (djangorestframework-simplejwt)
- Soft delete en lugar de hard delete
- Validación de permisos en cada operación
- Logs de operaciones sospechosas

## ⚠️ LO QUE FALTA O SE PUEDE MEJORAR

### 1. Campo `legacy_id` para Migración VFP9

**Agregar al modelo User**:
```python
legacy_id = models.IntegerField(
    null=True,
    blank=True,
    db_index=True,
    unique=True,
    verbose_name="ID usuario VFP9"
)
```

**Razón**: Mapear usuarios del sistema VFP9 (`usuarios` table con `usu_codi`) a Django.

### 2. Services Layer

**Crear** `apps/users/services/user_service.py`:
```python
class UserService:
    @staticmethod
    def create_user_with_validations(data, created_by):
        # Validar DNI único
        # Validar email corporativo si es obligatorio
        # Asignar permisos default por rol
        # Enviar email de bienvenida
        # Crear audit log
        pass

    @staticmethod
    def change_user_role(user, new_role, changed_by):
        # Validar que changed_by tiene permisos
        # Log de cambio de rol (crítico para auditoría)
        # Notificar al usuario
        # Broadcast WebSocket
        pass

    @staticmethod
    def deactivate_user(user, deactivated_by, reason):
        # Marcar como inactivo
        # Revocar tokens activos
        # Log de desactivación
        # Notificar
        pass
```

**Razón**: Centralizar lógica de negocio compleja fuera de las views.

### 3. Permisos Custom por Rol

**Crear** `apps/users/permissions.py`:
```python
from rest_framework.permissions import BasePermission

class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['ADMIN', 'MANAGER']

class CanManageUsers(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'ADMIN'

class CanViewReports(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['ADMIN', 'MANAGER', 'BILLING']
```

**Usar en views**:
```python
@permission_classes([IsAuthenticated, IsAdminOrManager])
def some_view(request):
    ...
```

### 4. Audit Log de Cambios Críticos

**Crear** `apps/users/models/user_activity_log.py`:
```python
class UserActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activities_performed')
    action = models.CharField(max_length=50)  # LOGIN, LOGOUT, ROLE_CHANGE, PROFILE_UPDATE, etc.
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
```

**Registrar en views**:
```python
# En login
UserActivityLog.objects.create(
    user=user,
    performed_by=user,
    action='LOGIN',
    ip_address=get_client_ip(request),
    user_agent=request.META.get('HTTP_USER_AGENT', '')
)

# En cambio de rol
UserActivityLog.objects.create(
    user=target_user,
    performed_by=request.user,
    action='ROLE_CHANGE',
    details={'old_role': old_role, 'new_role': new_role}
)
```

### 5. Tests Unitarios

**Crear** `apps/users/tests/`:
```
users/tests/
├── test_models.py
├── test_auth.py
├── test_user_crud.py
├── test_permissions.py
└── test_cache.py
```

**Ejemplo** (`test_auth.py`):
```python
from django.test import TestCase
from rest_framework.test import APIClient
from apps.users.models import User

class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            name='Test',
            last_name='User',
            password='testpass123'
        )

    def test_login_success(self):
        response = self.client.post('/api/v1/users/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post('/api/v1/users/login/', {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 401)
```

### 6. Endpoint de Estadísticas de Usuarios (Opcional)

**Crear** `GET /api/v1/users/stats/` (Admin only):
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def user_stats_view(request):
    total = User.objects.filter(is_active=True).count()
    by_role = User.objects.filter(is_active=True).values('role').annotate(count=Count('id'))
    recently_created = User.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).count()

    return Response({
        'total_active': total,
        'by_role': list(by_role),
        'created_last_30_days': recently_created
    })
```

### 7. Configuración de Notificaciones por Usuario (Opcional)

**Crear** `apps/users/models/user_notification_settings.py`:
```python
class UserNotificationSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    email_on_order_status_change = models.BooleanField(default=True)
    email_on_stock_alert = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
```

## 📋 CHECKLIST DE MEJORAS SUGERIDAS

### Alta Prioridad (Pre-Producción)

- [ ] Agregar campo `legacy_id` al modelo User
- [ ] Crear migración para `legacy_id`
- [ ] Implementar `UserService` con validaciones de negocio
- [ ] Crear permisos custom por rol
- [ ] Agregar tests básicos (auth, CRUD)

### Media Prioridad (Post-MVP)

- [ ] Implementar `UserActivityLog` para auditoría
- [ ] Crear endpoint de estadísticas
- [ ] Agregar tests de cache y permisos
- [ ] Documentar flujos de autenticación en CLAUDE.md

### Baja Prioridad (Features Futuras)

- [ ] Settings de notificaciones por usuario
- [ ] Export de usuarios a CSV/Excel
- [ ] Bulk operations (activar/desactivar múltiples)
- [ ] Two-factor authentication (2FA)

## 🎯 PLAN DE ACCIÓN INMEDIATO

### Paso 1: Agregar `legacy_id`
```bash
# Editar modelo
# Crear migración
python manage.py makemigrations users
python manage.py migrate users
```

### Paso 2: Crear `UserService`
```bash
mkdir -p Backend-API/apps/users/services
touch Backend-API/apps/users/services/__init__.py
touch Backend-API/apps/users/services/user_service.py
```

### Paso 3: Crear Permisos Custom
```bash
touch Backend-API/apps/users/permissions.py
```

### Paso 4: Agregar Tests
```bash
mkdir -p Backend-API/apps/users/tests
touch Backend-API/apps/users/tests/__init__.py
touch Backend-API/apps/users/tests/test_auth.py
touch Backend-API/apps/users/tests/test_user_crud.py
```

## ✅ CONCLUSIÓN

El módulo `users` está **MUY BIEN IMPLEMENTADO** con:
- ✅ CRUD completo y bien organizado
- ✅ Autenticación JWT robusta
- ✅ Cache estratégico
- ✅ Integración S3/MinIO
- ✅ WebSocket events
- ✅ Repository pattern
- ✅ Documentación drf-spectacular

**Lo mínimo necesario para producción**:
1. Campo `legacy_id` para migración VFP9
2. Tests básicos de autenticación y CRUD
3. Services layer para validaciones complejas (si aplica)

**El resto son mejoras opcionales** que se pueden implementar post-MVP.
