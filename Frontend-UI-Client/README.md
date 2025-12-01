# ERP Frontend Client

Frontend moderno para sistema ERP construido con React 19, TypeScript, Vite y TailwindCSS v4.

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
cd Frontend-UI-Client
npm install
```

### 2. Configurar Variables de Entorno

```bash
cp .env.example .env.development
```

### 3. Iniciar Servidor de Desarrollo

```bash
npm run dev
```

El frontend estará disponible en `http://localhost:5173`

## 📦 Stack Tecnológico

- **React 19** - Biblioteca UI
- **TypeScript 5.9** - Type safety
- **Vite 7** - Build tool
- **TailwindCSS 4** - Utility-first CSS
- **React Router 7** - Routing
- **TanStack Query 5** - Data fetching
- **Zustand** - State management
- **React Hook Form + Yup** - Forms
- **Axios** - HTTP client
- **Socket.io Client** - WebSocket
- **date-fns** - Fechas
- **Sonner** - Notifications
- **Headless UI** - Componentes
- **Heroicons** - Iconos

## 📁 Estructura

```
src/
├── app/           # Configuración app
├── shared/        # Código compartido
│   ├── ui/       # Design System
│   ├── layouts/  # Layouts
│   ├── hooks/    # Hooks globales
│   ├── lib/      # Configs (api, query, ws)
│   ├── utils/    # Utilidades
│   ├── types/    # Types globales
│   └── constants/# Constantes
├── features/      # Módulos por dominio
│   ├── auth/
│   ├── products/
│   ├── stocks/
│   └── ...
```

## 📜 Scripts

```bash
npm run dev          # Desarrollo
npm run build        # Build producción
npm run preview      # Preview build
npm run lint         # Linting
npm run type-check   # Type checking
```

## 🎨 Design System

Componentes base con `class-variance-authority`:

- Button, Input, Select, Modal
- Table, Card, Badge, Alert
- Avatar, Dropdown

## 🌐 Integración Backend

### API REST
```typescript
// Proxy en desarrollo: /api → http://localhost:8000
```

### WebSocket
```typescript
// Proxy en desarrollo: /ws → ws://localhost:8000/ws
```

## 📝 Convenciones

```typescript
// Components: PascalCase
ProductForm.tsx

// Hooks: camelCase + 'use'
useProducts.ts

// Types: PascalCase
type User = { ... }

// Constants: UPPER_SNAKE_CASE
const API_BASE_URL = '...'
```

## 📝 Estado

### ✅ Completado
- [x] Configuración base
- [x] Path aliases
- [x] TailwindCSS v4

### 🚧 En Desarrollo
- [ ] Design System
- [ ] Auth feature
- [ ] Layouts

## 📄 Licencia

Privado - Uso interno
