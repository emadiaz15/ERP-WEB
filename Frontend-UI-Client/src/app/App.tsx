/**
 * App Component
 * Componente principal de la aplicación
 */

import { useEffect } from 'react'
import { RouterProvider } from 'react-router'
import { AppProviders } from './providers'
import { router } from './router'
import { initializeWebSockets } from '@/shared/lib/websocket/wsClient'

function App() {
  // Inicializar WebSockets cuando la app se monta
  useEffect(() => {
    // Solo inicializar si hay un token (usuario autenticado)
    const token = localStorage.getItem('erp_access_token')

    if (token) {
      if (import.meta.env.VITE_DEBUG === 'true') {
        console.log('[App] Inicializando WebSockets...')
      }
      initializeWebSockets()
    }

    // Cleanup al desmontar
    return () => {
      // Los WebSockets se limpiarán automáticamente en logout
    }
  }, [])

  return (
    <AppProviders>
      <RouterProvider router={router} />
    </AppProviders>
  )
}

export default App
