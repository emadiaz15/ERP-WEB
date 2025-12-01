/**
 * useDisclosure Hook
 * Maneja estados open/close (modales, dropdowns, etc.)
 */

import { useCallback, useState } from 'react'

interface UseDisclosureReturn {
  isOpen: boolean
  open: () => void
  close: () => void
  toggle: () => void
}

export function useDisclosure(defaultIsOpen: boolean = false): UseDisclosureReturn {
  const [isOpen, setIsOpen] = useState(defaultIsOpen)

  const open = useCallback(() => setIsOpen(true), [])
  const close = useCallback(() => setIsOpen(false), [])
  const toggle = useCallback(() => setIsOpen((prev) => !prev), [])

  return { isOpen, open, close, toggle }
}

export default useDisclosure
