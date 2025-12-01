/**
 * Auth Types
 */

// Roles de usuario disponibles en el sistema
export type UserRole =
  | 'ADMIN'
  | 'MANAGER'
  | 'SALES'
  | 'BILLING'
  | 'TRAVELER'
  | 'OPERATOR'
  | 'WAREHOUSE'
  | 'READONLY'

export interface User {
  id: number
  username: string
  email: string
  name: string
  last_name: string
  role: UserRole
  status: boolean
  is_active: boolean
  image?: string | null
  image_url?: string | null
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  password_confirm: string
  name?: string
  last_name?: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  user: User
}

export interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
}
