/**
 * Common Types
 */

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ApiError {
  message: string
  code?: string
  field?: string
  details?: Record<string, unknown>
}

export interface ApiResponse<T = unknown> {
  data: T
  message?: string
  success: boolean
}

export type SortDirection = 'asc' | 'desc'

export interface SortConfig {
  field: string
  direction: SortDirection
}

export interface PaginationParams {
  page?: number
  page_size?: number
  ordering?: string
  search?: string
}

export interface FilterParams {
  [key: string]: string | number | boolean | undefined | null
}

export interface QueryParams extends PaginationParams, FilterParams {}
