/**
 * Input Component
 * Componente de input con labels, errores y variantes
 */

import { forwardRef, type InputHTMLAttributes } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/shared/utils/cn'

const inputVariants = cva(
  'input-base w-full rounded-lg border bg-white px-4 text-sm text-gray-800 shadow-theme-xs transition-colors duration-200 placeholder:text-gray-400 focus:outline-none focus:ring-4 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-400',
  {
    variants: {
      size: {
        sm: 'h-9 text-sm',
        md: 'h-11 text-sm',
        lg: 'h-12 text-base',
      },
      state: {
        default: 'border-gray-300 focus:border-brand-500 focus:ring-brand-500/10',
        error: 'border-error-500 focus:border-error-500 focus:ring-error-500/10',
        success: 'border-success-500 focus:border-success-500 focus:ring-success-500/10',
      },
    },
    defaultVariants: {
      size: 'md',
      state: 'default',
    },
  },
)

export interface InputProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'>,
    VariantProps<typeof inputVariants> {
  label?: string
  error?: string
  helperText?: string
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      size,
      state,
      label,
      error,
      helperText,
      leftIcon,
      rightIcon,
      id,
      ...props
    },
    ref,
  ) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-')
    const computedState = error ? 'error' : state

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="mb-2 block text-sm font-medium text-gray-700"
          >
            {label}
            {props.required && <span className="ml-1 text-error-500">*</span>}
          </label>
        )}

        <div className="relative">
          {leftIcon && (
            <div className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              {leftIcon}
            </div>
          )}

          <input
            ref={ref}
            id={inputId}
            className={cn(
              inputVariants({ size, state: computedState }),
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              className,
            )}
            {...props}
          />

          {rightIcon && (
            <div className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
              {rightIcon}
            </div>
          )}
        </div>

        {(error || helperText) && (
          <p
            className={cn(
              'mt-1.5 text-sm',
              error ? 'text-error-600' : 'text-gray-500',
            )}
          >
            {error || helperText}
          </p>
        )}
      </div>
    )
  },
)

Input.displayName = 'Input'

export default Input
