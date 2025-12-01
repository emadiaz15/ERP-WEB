/**
 * LoginPage
 * Página de inicio de sesión
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button, Input } from '@/shared/ui'
import { useAuth } from '../context'
import { ROUTES } from '@/shared/constants/routes'

export function LoginPage() {
  const navigate = useNavigate()
  const { login, isLoading } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    try {
      await login({ username, password })
      // Redirigir al dashboard después del login exitoso
      navigate(ROUTES.DASHBOARD.HOME)
    } catch (err) {
      console.error('Error al iniciar sesión:', err)
      setError('Usuario o contraseña incorrectos. Por favor, intenta de nuevo.')
    }
  }

  return (
    <div>
      <div className="mb-6 text-center">
        <h2 className="text-2xl font-semibold text-gray-900">
          Iniciar Sesión
        </h2>
        <p className="mt-2 text-sm text-gray-600">
          Ingresa tus credenciales para acceder al sistema
        </p>
      </div>

      {error && (
        <div className="mb-4 rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Usuario o Email"
          type="text"
          placeholder="usuario@ejemplo.com"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          disabled={isLoading}
        />

        <Input
          label="Contraseña"
          type="password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          disabled={isLoading}
        />

        <div className="flex items-center justify-between">
          <label className="flex items-center">
            <input
              type="checkbox"
              className="h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500"
              disabled={isLoading}
            />
            <span className="ml-2 text-sm text-gray-700">Recordarme</span>
          </label>

          <a
            href="#"
            className="text-sm font-medium text-brand-500 hover:text-brand-600"
          >
            ¿Olvidaste tu contraseña?
          </a>
        </div>

        <Button type="submit" fullWidth size="lg" disabled={isLoading}>
          {isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
        </Button>
      </form>

      <div className="mt-6 text-center">
        <p className="text-sm text-gray-600">
          Sistema de Gestión Empresarial
        </p>
      </div>
    </div>
  )
}

export default LoginPage
