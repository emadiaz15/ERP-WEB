/**
 * Badge Component
 * Componente de badge para estados y etiquetas
 */

import { type HTMLAttributes, forwardRef } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/shared/utils/cn'

const badgeVariants = cva(
  'badge inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
  {
    variants: {
      variant: {
        success: 'badge-success bg-success-50 text-success-700',
        error: 'badge-error bg-error-50 text-error-700',
        warning: 'badge-warning bg-warning-50 text-warning-700',
        info: 'badge-info bg-info-50 text-info-700',
        default: 'bg-gray-100 text-gray-700',
        brand: 'bg-brand-50 text-brand-700',
      },
      size: {
        sm: 'px-2 py-0.5 text-xs',
        md: 'px-2.5 py-0.5 text-xs',
        lg: 'px-3 py-1 text-sm',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
    },
  },
)

export interface BadgeProps
  extends HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {
  dot?: boolean
}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant, size, dot, children, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={cn(badgeVariants({ variant, size, className }))}
        {...props}
      >
        {dot && (
          <span
            className={cn(
              'mr-1.5 inline-block h-1.5 w-1.5 rounded-full',
              variant === 'success' && 'bg-success-500',
              variant === 'error' && 'bg-error-500',
              variant === 'warning' && 'bg-warning-500',
              variant === 'info' && 'bg-info-500',
              variant === 'brand' && 'bg-brand-500',
              variant === 'default' && 'bg-gray-500',
            )}
          />
        )}
        {children}
      </span>
    )
  },
)

Badge.displayName = 'Badge'

export default Badge
