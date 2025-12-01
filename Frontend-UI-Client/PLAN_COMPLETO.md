# 🚀 Plan Completo - ERP Frontend Profesional

## ✅ YA COMPLETADO

### 1. Configuración Base
- ✅ Proyecto Vite + React 19 + TypeScript
- ✅ Path aliases configurados
- ✅ TailwindCSS v4 con paleta profesional (colores del ejemplo TailAdmin)
- ✅ Estilos base CSS con componentes reutilizables
- ✅ Variables de entorno
- ✅ package.json con TODAS las dependencias necesarias

### 2. Paleta de Colores Profesional
```typescript
brand: #465fff     // Azul primario (profesional)
gray: completo    // Escala de grises moderna
success: #12b76a  // Verde para éxitos
error: #f04438    // Rojo para errores
warning: #f79009  // Naranja para warnings
info: #0ba5ec     // Azul claro para info
orange: #fb6514   // Naranja para badges
```

---

## 🎯 PRÓXIMO PASO OBLIGATORIO

**DEBES EJECUTAR:**

```bash
cd /home/emanuel-diaz/Escritorio/workspace/ERP-Web/Frontend-UI-Client
npm install
```

**Esto instalará:**
- React 19, TypeScript, Vite
- TailwindCSS 4
- React Router 7
- TanStack Query 5 (para cache)
- Zustand (state management)
- Socket.io Client (WebSocket/realtime)
- React Hook Form + Yup
- Axios, Headless UI, Heroicons
- class-variance-authority, clsx, tailwind-merge
- Y más...

---

## 📁 LO QUE VOY A CREAR DESPUÉS DE npm install

### FASE 1: Estructura de Carpetas

```
src/
├── app/                    # Configuración de la aplicación
│   ├── App.tsx
│   ├── main.tsx
│   ├── router.tsx         # React Router 7
│   └── providers.tsx      # Query, Zustand, WebSocket providers
│
├── shared/                # Código compartido entre features
│   │
│   ├── ui/               # 🎨 DESIGN SYSTEM COMPLETO
│   │   ├── button/
│   │   │   ├── Button.tsx
│   │   │   └── index.ts
│   │   ├── input/
│   │   │   ├── Input.tsx
│   │   │   ├── TextArea.tsx
│   │   │   └── index.ts
│   │   ├── select/
│   │   │   ├── Select.tsx
│   │   │   ├── MultiSelect.tsx
│   │   │   └── index.ts
│   │   ├── modal/
│   │   │   ├── Modal.tsx
│   │   │   ├── ConfirmModal.tsx
│   │   │   └── index.ts
│   │   ├── table/
│   │   │   ├── Table.tsx
│   │   │   ├── TableHeader.tsx
│   │   │   ├── TableRow.tsx
│   │   │   ├── TablePagination.tsx
│   │   │   └── index.ts
│   │   ├── card/
│   │   │   ├── Card.tsx
│   │   │   ├── StatsCard.tsx
│   │   │   └── index.ts
│   │   ├── badge/
│   │   │   ├── Badge.tsx
│   │   │   ├── StatusBadge.tsx
│   │   │   └── index.ts
│   │   ├── alert/
│   │   │   ├── Alert.tsx
│   │   │   └── index.ts
│   │   ├── avatar/
│   │   │   ├── Avatar.tsx
│   │   │   └── index.ts
│   │   ├── dropdown/
│   │   │   ├── Dropdown.tsx
│   │   │   ├── DropdownMenu.tsx
│   │   │   └── index.ts
│   │   ├── spinner/
│   │   │   ├── Spinner.tsx
│   │   │   └── index.ts
│   │   └── index.ts      # Barrel export
│   │
│   ├── layouts/          # Layouts del sistema
│   │   ├── AppLayout/
│   │   │   ├── AppLayout.tsx
│   │   │   ├── AppHeader.tsx
│   │   │   ├── AppSidebar.tsx
│   │   │   ├── SidebarMenu.tsx
│   │   │   ├── UserDropdown.tsx
│   │   │   └── NotificationBell.tsx
│   │   ├── AuthLayout/
│   │   │   └── AuthLayout.tsx
│   │   └── index.ts
│   │
│   ├── lib/              # ⚡ CONFIGURACIONES CORE
│   │   ├── api/
│   │   │   ├── client.ts        # Axios configurado
│   │   │   ├── endpoints.ts     # URLs de API
│   │   │   ├── interceptors.ts  # JWT interceptor
│   │   │   └── index.ts
│   │   │
│   │   ├── query/
│   │   │   ├── queryClient.ts   # TanStack Query config
│   │   │   ├── mutations.ts     # Mutation helpers
│   │   │   └── index.ts
│   │   │
│   │   └── websocket/
│   │       ├── wsClient.ts      # Socket.io config
│   │       ├── wsEvents.ts      # Event handlers
│   │       ├── useWebSocket.ts  # Hook para WS
│   │       └── index.ts
│   │
│   ├── hooks/            # Hooks globales
│   │   ├── useAuth.ts
│   │   ├── useModal.ts
│   │   ├── useDebounce.ts
│   │   ├── useRealtime.ts       # Sincronización realtime
│   │   ├── useCacheSync.ts      # Sincronización cache
│   │   └── index.ts
│   │
│   ├── utils/            # Utilidades
│   │   ├── date.ts
│   │   ├── format.ts
│   │   ├── validation.ts
│   │   ├── storage.ts
│   │   └── index.ts
│   │
│   ├── types/            # Types globales
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   ├── common.ts
│   │   ├── websocket.ts
│   │   └── index.ts
│   │
│   └── constants/        # Constantes
│       ├── api.ts
│       ├── routes.ts
│       ├── permissions.ts
│       ├── events.ts        # WebSocket events
│       └── index.ts
│
└── features/            # 🎯 TODOS LOS MÓDULOS DEL ERP
    │
    ├── auth/            # Autenticación
    │   ├── api/
    │   │   ├── authApi.ts
    │   │   └── authQueries.ts
    │   ├── components/
    │   │   ├── LoginForm.tsx
    │   │   └── PasswordResetForm.tsx
    │   ├── hooks/
    │   │   ├── useAuth.ts
    │   │   └── useLogin.ts
    │   ├── pages/
    │   │   ├── LoginPage.tsx
    │   │   └── PasswordResetPage.tsx
    │   ├── store/
    │   │   └── authStore.ts
    │   ├── types/
    │   │   └── auth.types.ts
    │   └── index.ts
    │
    ├── dashboard/       # Dashboard principal
    │   ├── components/
    │   │   ├── StatCards.tsx
    │   │   ├── SalesChart.tsx
    │   │   ├── RecentOrders.tsx
    │   │   └── TopProducts.tsx
    │   ├── hooks/
    │   ├── pages/
    │   │   └── DashboardPage.tsx
    │   └── index.ts
    │
    ├── products/        # Productos
    │   ├── api/
    │   │   ├── productsApi.ts
    │   │   ├── productsQueries.ts
    │   │   └── productsMutations.ts
    │   ├── components/
    │   │   ├── ProductTable.tsx
    │   │   ├── ProductForm.tsx
    │   │   ├── ProductCard.tsx
    │   │   ├── ProductFilters.tsx
    │   │   └── ProductSearch.tsx
    │   ├── hooks/
    │   │   ├── useProducts.ts
    │   │   ├── useProductForm.ts
    │   │   └── useProductSync.ts    # Realtime sync
    │   ├── pages/
    │   │   ├── ProductsListPage.tsx
    │   │   ├── ProductDetailPage.tsx
    │   │   └── ProductCreatePage.tsx
    │   ├── store/
    │   │   └── productsStore.ts
    │   ├── types/
    │   │   └── product.types.ts
    │   └── index.ts
    │
    ├── categories/      # Categorías
    ├── stocks/          # Stock/Inventario
    ├── users/           # Usuarios
    ├── customers/       # Clientes
    ├── suppliers/       # Proveedores
    ├── orders/          # Pedidos (ORDERS - modificables)
    ├── sales/           # Ventas (SALES - inmutables)
    ├── purchases/       # Compras
    ├── billing/         # Facturación
    ├── delivery-notes/  # Remitos
    ├── cutting-orders/  # Órdenes de corte
    ├── manufacturing/   # Manufactura
    ├── expenses/        # Gastos
    ├── treasury/        # Tesorería
    ├── accounting/      # Contabilidad
    ├── reports/         # Reportes
    └── notifications/   # Notificaciones
```

---

## ⚡ CARACTERÍSTICAS CORE

### 1. Sistema de Cache Inteligente (TanStack Query)

```typescript
// shared/lib/query/queryClient.ts
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutos
      gcTime: 1000 * 60 * 30,   // 30 minutos
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

// Hook de ejemplo
export function useProducts() {
  return useQuery({
    queryKey: ['products'],
    queryFn: () => productsApi.getAll(),
    // Cache automático + revalidación
  })
}
```

### 2. WebSocket para Sincronización en Tiempo Real

```typescript
// shared/lib/websocket/wsClient.ts
import { io } from 'socket.io-client'

export const socket = io(import.meta.env.VITE_WS_URL, {
  autoConnect: false,
  auth: {
    token: () => localStorage.getItem('access_token'),
  },
})

// Eventos CRUD
socket.on('product:created', (data) => {
  queryClient.invalidateQueries({ queryKey: ['products'] })
  // Actualiza cache automáticamente
})

socket.on('product:updated', (data) => {
  queryClient.setQueryData(['product', data.id], data)
  // Actualiza en todos los usuarios
})

socket.on('product:deleted', (data) => {
  queryClient.invalidateQueries({ queryKey: ['products'] })
})
```

### 3. Hook de Sincronización Realtime

```typescript
// features/products/hooks/useProductSync.ts
export function useProductSync() {
  const queryClient = useQueryClient()

  useEffect(() => {
    // Escuchar eventos WebSocket
    socket.on('product:created', handleProductCreated)
    socket.on('product:updated', handleProductUpdated)
    socket.on('product:deleted', handleProductDeleted)

    return () => {
      socket.off('product:created')
      socket.off('product:updated')
      socket.off('product:deleted')
    }
  }, [])

  // Cuando un usuario crea/actualiza/elimina
  // TODOS los demás usuarios ven el cambio AL INSTANTE
}
```

### 4. Notificaciones en Tiempo Real

```typescript
// features/notifications/hooks/useNotifications.ts
export function useNotifications() {
  const [notifications, setNotifications] = useState([])

  useEffect(() => {
    socket.on('notification', (notification) => {
      setNotifications(prev => [notification, ...prev])
      // Mostrar toast
      toast.success(notification.message)
    })
  }, [])

  return { notifications }
}
```

---

## 🎨 DESIGN SYSTEM

Componentes con `class-variance-authority`:

```typescript
// Ejemplo: Button Component
import { cva, type VariantProps } from 'class-variance-authority'

const buttonVariants = cva(
  'btn-base',
  {
    variants: {
      variant: {
        primary: 'btn-primary',
        secondary: 'btn-secondary',
        danger: 'btn-danger',
        ghost: 'hover:bg-gray-100',
      },
      size: {
        sm: 'h-9 px-3 text-sm',
        md: 'h-11 px-4 text-base',
        lg: 'h-12 px-6 text-lg',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
)

export function Button({ variant, size, ...props }) {
  return (
    <button className={buttonVariants({ variant, size })} {...props} />
  )
}
```

---

## 🏠 LAYOUTS

### AppLayout (Layout principal con Header + Sidebar)

```typescript
export function AppLayout() {
  const { user } = useAuth()
  const { notifications } = useNotifications()

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <AppSidebar />

      {/* Main content */}
      <div className="flex flex-1 flex-col">
        {/* Header */}
        <AppHeader user={user} notifications={notifications} />

        {/* Page content */}
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
```

---

## 🔐 AUTENTICACIÓN CON JWT

```typescript
// shared/lib/api/client.ts
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Refresh token automático
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Intentar refresh
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        const { data } = await authApi.refresh(refreshToken)
        localStorage.setItem('access_token', data.access)
        // Reintentar request original
        return apiClient(error.config)
      }
    }
    return Promise.reject(error)
  }
)
```

---

## 📊 EJEMPLO DE FEATURE COMPLETA: Products

```
features/products/
├── api/
│   ├── productsApi.ts          # CRUD + buscar
│   ├── productsQueries.ts      # useProducts, useProduct
│   └── productsMutations.ts    # useCreateProduct, etc
│
├── components/
│   ├── ProductTable.tsx        # Tabla con sort/filter/pagination
│   ├── ProductForm.tsx         # Formulario create/edit
│   ├── ProductCard.tsx         # Card view
│   ├── ProductFilters.tsx      # Filtros avanzados
│   └── ProductSearch.tsx       # Búsqueda en tiempo real
│
├── hooks/
│   ├── useProducts.ts          # Hook principal
│   ├── useProductForm.ts       # Lógica de formulario
│   └── useProductSync.ts       # Sincronización WebSocket
│
├── pages/
│   ├── ProductsListPage.tsx    # /products
│   ├── ProductDetailPage.tsx   # /products/:id
│   └── ProductCreatePage.tsx   # /products/create
│
├── store/
│   └── productsStore.ts        # Zustand store (UI state)
│
├── types/
│   └── product.types.ts        # Interfaces TypeScript
│
└── index.ts                    # Public exports
```

---

## ✅ TODOS LOS MÓDULOS QUE VOY A CREAR

1. ✅ **auth** - Autenticación y autorización
2. ✅ **dashboard** - Dashboard principal con métricas
3. ✅ **products** - Catálogo de productos
4. ✅ **categories** - Categorías de productos
5. ✅ **stocks** - Gestión de inventario
6. ✅ **users** - Gestión de usuarios
7. ✅ **customers** - Clientes
8. ✅ **suppliers** - Proveedores
9. ✅ **orders** - Pedidos (modificables)
10. ✅ **sales** - Ventas (inmutables)
11. ✅ **purchases** - Compras
12. ✅ **billing** - Facturación
13. ✅ **delivery-notes** - Remitos
14. ✅ **cutting-orders** - Órdenes de corte
15. ✅ **manufacturing** - Manufactura
16. ✅ **expenses** - Gastos
17. ✅ **treasury** - Tesorería
18. ✅ **accounting** - Contabilidad
19. ✅ **reports** - Reportes y analytics
20. ✅ **notifications** - Centro de notificaciones

---

## 🎯 PRÓXIMO PASO

**EJECUTA AHORA:**

```bash
cd /home/emanuel-diaz/Escritorio/workspace/ERP-Web/Frontend-UI-Client
npm install
```

**Cuando termine, avísame y empiezo a crear TODA la estructura + componentes + features!**

**Duración estimada de creación**: ~10-15 minutos (yo creo todo)
**Resultado**: Frontend ERP completo, profesional, escalable, con cache y realtime

---

## 📝 Notas Importantes

- **Sincronización realtime**: Cuando un usuario modifica algo, TODOS ven el cambio al instante
- **Cache inteligente**: Las consultas se cachean 5 minutos, revalidación automática
- **WebSocket**: Conexión persistente para notificaciones y updates en vivo
- **UX Comercial**: Interfaz diseñada específicamente para sistema de comercio/ERP
- **Escalable**: Cada módulo es independiente, fácil de mantener
- **TypeScript**: Type safety en todo el código
- **Performante**: Cache + memoization + lazy loading

**¿Listo para ejecutar npm install?** 🚀
