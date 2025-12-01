/**
 * Servicio de Autenticación
 * Maneja las operaciones de login, logout y gestión de tokens
 */

import { api } from '@/shared/lib/api/client'
import {
  API_ENDPOINTS,
  AUTH_TOKEN_KEY,
  REFRESH_TOKEN_KEY,
  USER_KEY,
} from '@/shared/constants/api'
import type {
  LoginCredentials,
  LoginResponse,
  RegisterData,
  User,
} from '@/shared/types/auth'

/**
 * Realiza el login del usuario
 */
export const login = async (
  credentials: LoginCredentials,
): Promise<LoginResponse> => {
  const response = await api.post<LoginResponse>(
    API_ENDPOINTS.AUTH.LOGIN,
    credentials,
  )

  const { access_token, refresh_token, user } = response.data

  // Guardar tokens y usuario en localStorage
  localStorage.setItem(AUTH_TOKEN_KEY, access_token)
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))

  return response.data
}

/**
 * Realiza el logout del usuario
 */
export const logout = async (): Promise<void> => {
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)

  if (refreshToken) {
    try {
      await api.post(API_ENDPOINTS.AUTH.LOGOUT, {
        refresh_token: refreshToken,
      })
    } catch (error) {
      // Continuar con el logout local incluso si el servidor falla
      console.error('Error al hacer logout en el servidor:', error)
    }
  }

  // Limpiar localStorage
  localStorage.removeItem(AUTH_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

/**
 * Registra un nuevo usuario
 */
export const register = async (data: RegisterData): Promise<User> => {
  const response = await api.post<User>(API_ENDPOINTS.AUTH.REGISTER, data)
  return response.data
}

/**
 * Obtiene el usuario actual desde localStorage
 */
export const getCurrentUser = (): User | null => {
  const userJson = localStorage.getItem(USER_KEY)
  if (!userJson) return null

  try {
    return JSON.parse(userJson) as User
  } catch (error) {
    console.error('Error al parsear usuario desde localStorage:', error)
    return null
  }
}

/**
 * Obtiene el token de acceso actual
 */
export const getAccessToken = (): string | null => {
  return localStorage.getItem(AUTH_TOKEN_KEY)
}

/**
 * Obtiene el token de refresh actual
 */
export const getRefreshToken = (): string | null => {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

/**
 * Verifica si el usuario está autenticado
 */
export const isAuthenticated = (): boolean => {
  return !!getAccessToken()
}
