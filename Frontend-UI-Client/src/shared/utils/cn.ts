/**
 * Class Name Utility
 * Combina clsx y tailwind-merge para merge de clases Tailwind
 */

import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merge de clases CSS con soporte para Tailwind
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export default cn
