/**
 * Contexto de Autenticación
 * Maneja el estado global de autenticación de la aplicación
 */

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import type { User, LoginCredentials } from '@/shared/types/auth'
import * as authService from '../services/authService'

interface AuthContextValue {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => Promise<void>
  updateUser: (user: User) => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Cargar usuario desde localStorage al montar el componente
  useEffect(() => {
    const loadUser = () => {
      const currentUser = authService.getCurrentUser()
      const isAuth = authService.isAuthenticated()

      if (currentUser && isAuth) {
        setUser(currentUser)
      }

      setIsLoading(false)
    }

    loadUser()
  }, [])

  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true)
    try {
      const response = await authService.login(credentials)
      setUser(response.user)
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    setIsLoading(true)
    try {
      await authService.logout()
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }

  const updateUser = (updatedUser: User) => {
    setUser(updatedUser)
    localStorage.setItem('erp_user', JSON.stringify(updatedUser))
  }

  const value: AuthContextValue = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    updateUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

/**
 * Hook para usar el contexto de autenticación
 */
export function useAuth() {
  const context = useContext(AuthContext)

  if (context === undefined) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider')
  }

  return context
}
