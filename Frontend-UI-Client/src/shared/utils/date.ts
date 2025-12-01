/**
 * Date Utilities usando date-fns
 */

import {
  format as dateFnsFormat,
  formatDistance,
  formatRelative,
  parseISO,
  isValid,
  differenceInDays,
  differenceInHours,
  differenceInMinutes,
  startOfDay,
  endOfDay,
  startOfMonth,
  endOfMonth,
  addDays,
  subDays,
} from 'date-fns'
import { es } from 'date-fns/locale'

/**
 * Formatear fecha
 */
export function formatDate(
  date: string | Date,
  formatStr: string = 'dd/MM/yyyy',
): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date
  if (!isValid(dateObj)) return 'Fecha inválida'
  return dateFnsFormat(dateObj, formatStr, { locale: es })
}

/**
 * Formatear fecha y hora
 */
export function formatDateTime(
  date: string | Date,
  formatStr: string = 'dd/MM/yyyy HH:mm',
): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date
  if (!isValid(dateObj)) return 'Fecha inválida'
  return dateFnsFormat(dateObj, formatStr, { locale: es })
}

/**
 * Formatear fecha relativa (hace X tiempo)
 */
export function formatRelativeDate(date: string | Date): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date
  if (!isValid(dateObj)) return 'Fecha inválida'
  return formatDistance(dateObj, new Date(), { addSuffix: true, locale: es })
}

/**
 * Formatear fecha relativa con contexto
 */
export function formatRelativeDateWithContext(date: string | Date): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date
  if (!isValid(dateObj)) return 'Fecha inválida'
  return formatRelative(dateObj, new Date(), { locale: es })
}

/**
 * Obtener rango de fechas para hoy
 */
export function getTodayRange(): { start: Date; end: Date } {
  const now = new Date()
  return {
    start: startOfDay(now),
    end: endOfDay(now),
  }
}

/**
 * Obtener rango de fechas para el mes actual
 */
export function getCurrentMonthRange(): { start: Date; end: Date } {
  const now = new Date()
  return {
    start: startOfMonth(now),
    end: endOfMonth(now),
  }
}

/**
 * Verificar si una fecha está en el pasado
 */
export function isPast(date: string | Date): boolean {
  const dateObj = typeof date === 'string' ? parseISO(date) : date
  if (!isValid(dateObj)) return false
  return dateObj < new Date()
}

/**
 * Verificar si una fecha está en el futuro
 */
export function isFuture(date: string | Date): boolean {
  const dateObj = typeof date === 'string' ? parseISO(date) : date
  if (!isValid(dateObj)) return false
  return dateObj > new Date()
}

/**
 * Calcular días de diferencia
 */
export function daysBetween(date1: string | Date, date2: string | Date): number {
  const dateObj1 = typeof date1 === 'string' ? parseISO(date1) : date1
  const dateObj2 = typeof date2 === 'string' ? parseISO(date2) : date2
  return differenceInDays(dateObj2, dateObj1)
}

/**
 * Formatear duración en texto legible
 */
export function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} min`
  }
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return mins > 0 ? `${hours}h ${mins}min` : `${hours}h`
}

export {
  parseISO,
  isValid,
  addDays,
  subDays,
  startOfDay,
  endOfDay,
  startOfMonth,
  endOfMonth,
}
