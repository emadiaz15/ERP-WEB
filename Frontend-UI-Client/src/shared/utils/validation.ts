/**
 * Validation Utilities
 */

/**
 * Validar email
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Validar CUIT/CUIL argentino
 */
export function isValidCUIT(cuit: string): boolean {
  const cuitClean = cuit.replace(/[-\s]/g, '')

  if (cuitClean.length !== 11 || !/^\d+$/.test(cuitClean)) {
    return false
  }

  const digits = cuitClean.split('').map(Number)
  const verifier = digits.pop()!
  const mult = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

  const sum = digits.reduce((acc, digit, index) => acc + digit * mult[index], 0)
  const remainder = sum % 11
  const calculatedVerifier = remainder === 0 ? 0 : remainder === 1 ? 9 : 11 - remainder

  return calculatedVerifier === verifier
}

/**
 * Validar teléfono (formato argentino)
 */
export function isValidPhone(phone: string): boolean {
  const phoneClean = phone.replace(/[-\s()]/g, '')
  // Acepta números de 10 dígitos (con código de área) o más
  return /^\d{10,}$/.test(phoneClean)
}

/**
 * Validar código postal argentino
 */
export function isValidPostalCode(code: string): boolean {
  // Formato argentino: 4 dígitos o letra + 4 dígitos + 3 letras
  return /^(\d{4}|[A-Z]\d{4}[A-Z]{3})$/.test(code)
}

/**
 * Validar número positivo
 */
export function isPositiveNumber(value: unknown): boolean {
  const num = Number(value)
  return !isNaN(num) && num > 0
}

/**
 * Validar rango numérico
 */
export function isInRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max
}

/**
 * Sanitizar string (remover caracteres especiales)
 */
export function sanitizeString(str: string): string {
  return str.replace(/[<>]/g, '')
}
