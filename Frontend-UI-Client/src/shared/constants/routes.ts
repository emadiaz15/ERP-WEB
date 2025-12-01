/**
 * Frontend Routes Constants
 */

export const ROUTES = {
  // Public routes
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    FORGOT_PASSWORD: '/auth/forgot-password',
    RESET_PASSWORD: '/auth/reset-password',
  },
  // Private routes
  DASHBOARD: '/',
  PRODUCTS: {
    LIST: '/products',
    CREATE: '/products/new',
    EDIT: (id: string | number) => `/products/${id}/edit`,
    DETAIL: (id: string | number) => `/products/${id}`,
  },
  CATEGORIES: {
    LIST: '/categories',
    CREATE: '/categories/new',
    EDIT: (id: string | number) => `/categories/${id}/edit`,
  },
  STOCKS: {
    LIST: '/stocks',
    MOVEMENTS: '/stocks/movements',
    DETAIL: (id: string | number) => `/stocks/${id}`,
  },
  USERS: {
    LIST: '/users',
    CREATE: '/users/new',
    EDIT: (id: string | number) => `/users/${id}/edit`,
    DETAIL: (id: string | number) => `/users/${id}`,
  },
  CUSTOMERS: {
    LIST: '/customers',
    CREATE: '/customers/new',
    EDIT: (id: string | number) => `/customers/${id}/edit`,
    DETAIL: (id: string | number) => `/customers/${id}`,
  },
  SUPPLIERS: {
    LIST: '/suppliers',
    CREATE: '/suppliers/new',
    EDIT: (id: string | number) => `/suppliers/${id}/edit`,
    DETAIL: (id: string | number) => `/suppliers/${id}`,
  },
  ORDERS: {
    LIST: '/orders',
    CREATE: '/orders/new',
    EDIT: (id: string | number) => `/orders/${id}/edit`,
    DETAIL: (id: string | number) => `/orders/${id}`,
  },
  SALES: {
    LIST: '/sales',
    CREATE: '/sales/new',
    DETAIL: (id: string | number) => `/sales/${id}`,
  },
  PURCHASES: {
    LIST: '/purchases',
    CREATE: '/purchases/new',
    EDIT: (id: string | number) => `/purchases/${id}/edit`,
    DETAIL: (id: string | number) => `/purchases/${id}`,
  },
  BILLING: {
    LIST: '/billing',
    CREATE: '/billing/new',
    DETAIL: (id: string | number) => `/billing/${id}`,
  },
  DELIVERY_NOTES: {
    LIST: '/delivery-notes',
    CREATE: '/delivery-notes/new',
    EDIT: (id: string | number) => `/delivery-notes/${id}/edit`,
    DETAIL: (id: string | number) => `/delivery-notes/${id}`,
  },
  CUTTING_ORDERS: {
    LIST: '/cutting-orders',
    CREATE: '/cutting-orders/new',
    EDIT: (id: string | number) => `/cutting-orders/${id}/edit`,
    DETAIL: (id: string | number) => `/cutting-orders/${id}`,
  },
  MANUFACTURING: {
    LIST: '/manufacturing',
    CREATE: '/manufacturing/new',
    EDIT: (id: string | number) => `/manufacturing/${id}/edit`,
    DETAIL: (id: string | number) => `/manufacturing/${id}`,
  },
  EXPENSES: {
    LIST: '/expenses',
    CREATE: '/expenses/new',
    EDIT: (id: string | number) => `/expenses/${id}/edit`,
    DETAIL: (id: string | number) => `/expenses/${id}`,
  },
  TREASURY: {
    OVERVIEW: '/treasury',
    DETAIL: (id: string | number) => `/treasury/${id}`,
  },
  ACCOUNTING: {
    OVERVIEW: '/accounting',
    BALANCE_SHEET: '/accounting/balance-sheet',
    INCOME_STATEMENT: '/accounting/income-statement',
  },
  REPORTS: {
    SALES: '/reports/sales',
    PURCHASES: '/reports/purchases',
    INVENTORY: '/reports/inventory',
    FINANCIAL: '/reports/financial',
  },
  NOTIFICATIONS: '/notifications',
  PROFILE: '/profile',
  SETTINGS: '/settings',
} as const
