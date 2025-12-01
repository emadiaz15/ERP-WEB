/**
 * App Router
 * Configuración de rutas con React Router
 */

import { createBrowserRouter, Navigate } from 'react-router'
import { ROUTES } from '@/shared/constants/routes'
import { AuthLayout } from '@/shared/layouts/AuthLayout'
import { AppLayout } from '@/shared/layouts/AppLayout'
import { LoginPage } from '@/features/auth/pages/LoginPage'
import { DashboardPage } from '@/features/dashboard/pages/DashboardPage'

// Router configuration
export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to={ROUTES.AUTH.LOGIN} replace />,
  },
  // Auth routes (sin layout del ERP)
  {
    path: '/auth',
    element: <AuthLayout />,
    children: [
      {
        path: 'login',
        element: <LoginPage />,
      },
    ],
  },
  // App routes (con layout del ERP)
  {
    path: '/',
    element: <AppLayout />,
    children: [
      {
        index: true,
        element: <Navigate to={ROUTES.DASHBOARD} replace />,
      },
      {
        path: 'dashboard',
        element: <DashboardPage />,
      },
      // TODO: Agregar más rutas aquí
    ],
  },
  // Catch all
  {
    path: '*',
    element: <Navigate to={ROUTES.AUTH.LOGIN} replace />,
  },
])

export default router
