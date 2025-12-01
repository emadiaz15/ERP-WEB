/**
 * API Types
 */

export interface RequestConfig {
  headers?: Record<string, string>
  params?: Record<string, unknown>
  timeout?: number
}

export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
}

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
