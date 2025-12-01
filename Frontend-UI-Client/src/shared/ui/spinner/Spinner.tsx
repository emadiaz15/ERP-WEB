/**
 * Spinner Component
 * Componente de loading spinner
 */

import { type HTMLAttributes, forwardRef } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/shared/utils/cn'

const spinnerVariants = cva('animate-spin rounded-full border-2 border-current', {
  variants: {
    size: {
      sm: 'h-4 w-4 border-2',
      md: 'h-6 w-6 border-2',
      lg: 'h-8 w-8 border-3',
      xl: 'h-12 w-12 border-4',
    },
    variant: {
      primary: 'border-brand-500 border-t-transparent',
      white: 'border-white border-t-transparent',
      gray: 'border-gray-500 border-t-transparent',
    },
  },
  defaultVariants: {
    size: 'md',
    variant: 'primary',
  },
})

export interface SpinnerProps
  extends Omit<HTMLAttributes<HTMLDivElement>, 'children'>,
    VariantProps<typeof spinnerVariants> {
  label?: string
}

export const Spinner = forwardRef<HTMLDivElement, SpinnerProps>(
  ({ className, size, variant, label, ...props }, ref) => {
    return (
      <div ref={ref} className="flex items-center justify-center" {...props}>
        <div className={cn(spinnerVariants({ size, variant, className }))} />
        {label && (
          <span className="ml-2 text-sm text-gray-600">{label}</span>
        )}
      </div>
    )
  },
)

Spinner.displayName = 'Spinner'

export default Spinner
