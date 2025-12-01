/**
 * API Configuration Constants
 */

// Base URLs desde variables de entorno
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1'

export const WS_URL_CRUD_EVENTS =
  import.meta.env.VITE_WS_URL_CRUD_EVENTS || 'ws://localhost:8080/ws/crud-events/'

export const WS_URL_NOTIFICATIONS =
  import.meta.env.VITE_WS_URL_NOTIFICATIONS || 'ws://localhost:8080/ws/notifications/'

// API Timeouts
export const API_TIMEOUT = 30000 // 30 segundos
export const WS_RECONNECT_INTERVAL = 5000 // 5 segundos

// LocalStorage Keys
export const AUTH_TOKEN_KEY = 'erp_access_token'
export const REFRESH_TOKEN_KEY = 'erp_refresh_token'
export const USER_KEY = 'erp_user'

// API Endpoints
export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: '/auth/login/',
    LOGOUT: '/auth/logout/',
    REFRESH: '/auth/refresh/',
    ME: '/auth/me/',
    REGISTER: '/auth/register/',
  },
  // Productos
  PRODUCTS: {
    LIST: '/products/',
    DETAIL: (id: string | number) => `/products/${id}/`,
    CREATE: '/products/',
    UPDATE: (id: string | number) => `/products/${id}/`,
    DELETE: (id: string | number) => `/products/${id}/`,
  },
  // Categorías
  CATEGORIES: {
    LIST: '/categories/',
    DETAIL: (id: string | number) => `/categories/${id}/`,
    CREATE: '/categories/',
    UPDATE: (id: string | number) => `/categories/${id}/`,
    DELETE: (id: string | number) => `/categories/${id}/`,
  },
  // Stocks
  STOCKS: {
    LIST: '/stocks/',
    DETAIL: (id: string | number) => `/stocks/${id}/`,
    CREATE: '/stocks/',
    UPDATE: (id: string | number) => `/stocks/${id}/`,
    DELETE: (id: string | number) => `/stocks/${id}/`,
    MOVEMENTS: '/stocks/movements/',
  },
  // Usuarios
  USERS: {
    LIST: '/users/',
    DETAIL: (id: string | number) => `/users/${id}/`,
    CREATE: '/users/',
    UPDATE: (id: string | number) => `/users/${id}/`,
    DELETE: (id: string | number) => `/users/${id}/`,
  },
  // Clientes
  CUSTOMERS: {
    LIST: '/customers/',
    DETAIL: (id: string | number) => `/customers/${id}/`,
    CREATE: '/customers/',
    UPDATE: (id: string | number) => `/customers/${id}/`,
    DELETE: (id: string | number) => `/customers/${id}/`,
  },
  // Proveedores
  SUPPLIERS: {
    LIST: '/suppliers/',
    DETAIL: (id: string | number) => `/suppliers/${id}/`,
    CREATE: '/suppliers/',
    UPDATE: (id: string | number) => `/suppliers/${id}/`,
    DELETE: (id: string | number) => `/suppliers/${id}/`,
  },
  // Órdenes
  ORDERS: {
    LIST: '/orders/',
    DETAIL: (id: string | number) => `/orders/${id}/`,
    CREATE: '/orders/',
    UPDATE: (id: string | number) => `/orders/${id}/`,
    DELETE: (id: string | number) => `/orders/${id}/`,
  },
  // Ventas
  SALES: {
    LIST: '/sales/',
    DETAIL: (id: string | number) => `/sales/${id}/`,
    CREATE: '/sales/',
  },
  // Compras
  PURCHASES: {
    LIST: '/purchases/',
    DETAIL: (id: string | number) => `/purchases/${id}/`,
    CREATE: '/purchases/',
    UPDATE: (id: string | number) => `/purchases/${id}/`,
    DELETE: (id: string | number) => `/purchases/${id}/`,
  },
  // Facturación
  BILLING: {
    LIST: '/billing/',
    DETAIL: (id: string | number) => `/billing/${id}/`,
    CREATE: '/billing/',
  },
  // Notas de entrega
  DELIVERY_NOTES: {
    LIST: '/delivery-notes/',
    DETAIL: (id: string | number) => `/delivery-notes/${id}/`,
    CREATE: '/delivery-notes/',
    UPDATE: (id: string | number) => `/delivery-notes/${id}/`,
  },
  // Órdenes de corte
  CUTTING_ORDERS: {
    LIST: '/cutting-orders/',
    DETAIL: (id: string | number) => `/cutting-orders/${id}/`,
    CREATE: '/cutting-orders/',
    UPDATE: (id: string | number) => `/cutting-orders/${id}/`,
    DELETE: (id: string | number) => `/cutting-orders/${id}/`,
  },
  // Manufactura
  MANUFACTURING: {
    LIST: '/manufacturing/',
    DETAIL: (id: string | number) => `/manufacturing/${id}/`,
    CREATE: '/manufacturing/',
    UPDATE: (id: string | number) => `/manufacturing/${id}/`,
  },
  // Gastos
  EXPENSES: {
    LIST: '/expenses/',
    DETAIL: (id: string | number) => `/expenses/${id}/`,
    CREATE: '/expenses/',
    UPDATE: (id: string | number) => `/expenses/${id}/`,
    DELETE: (id: string | number) => `/expenses/${id}/`,
  },
  // Tesorería
  TREASURY: {
    LIST: '/treasury/',
    DETAIL: (id: string | number) => `/treasury/${id}/`,
    BALANCE: '/treasury/balance/',
  },
  // Contabilidad
  ACCOUNTING: {
    LIST: '/accounting/',
    DETAIL: (id: string | number) => `/accounting/${id}/`,
    BALANCE_SHEET: '/accounting/balance-sheet/',
    INCOME_STATEMENT: '/accounting/income-statement/',
  },
  // Reportes
  REPORTS: {
    SALES: '/reports/sales/',
    PURCHASES: '/reports/purchases/',
    INVENTORY: '/reports/inventory/',
    FINANCIAL: '/reports/financial/',
  },
  // Notificaciones
  NOTIFICATIONS: {
    LIST: '/notifications/',
    MARK_READ: (id: string | number) => `/notifications/${id}/read/`,
    MARK_ALL_READ: '/notifications/mark-all-read/',
  },
  // Dashboard
  DASHBOARD: {
    SUMMARY: '/dashboard/summary/',
    STATS: '/dashboard/stats/',
  },
} as const
