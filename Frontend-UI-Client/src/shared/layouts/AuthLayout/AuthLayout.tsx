/**
 * AuthLayout
 * Layout para páginas de autenticación (login, register)
 */

import { Outlet } from 'react-router'

export function AuthLayout() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md">
        {/* Logo del ERP */}
        <div className="mb-8 text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-xl bg-brand-500 shadow-theme-lg">
            <svg
              className="h-10 w-10 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            Sistema ERP
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Gestión empresarial integral
          </p>
        </div>

        {/* Contenido de la página (login, register, etc.) */}
        <div className="rounded-xl border border-gray-200 bg-white p-8 shadow-theme-md">
          <Outlet />
        </div>

        {/* Footer */}
        <p className="mt-8 text-center text-sm text-gray-500">
          © 2025 Sistema ERP. Todos los derechos reservados.
        </p>
      </div>
    </div>
  )
}

export default AuthLayout
