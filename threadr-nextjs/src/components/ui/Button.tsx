'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { LoadingSpinner } from './LoadingSpinner';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'outline' | 'premium';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  loading?: boolean;
  children: React.ReactNode;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', loading = false, disabled, children, ...props }, ref) => {
    const baseClasses = cn(
      'inline-flex items-center justify-center rounded-full font-semibold transition-all duration-200',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2',
      'disabled:pointer-events-none disabled:opacity-50 relative overflow-hidden',
      'shadow-sm hover:shadow-md transform hover:-translate-y-0.5',
      {
        // Variants - Premium SaaS style
        'bg-primary text-white hover:bg-primary/90 hover:shadow-lg': variant === 'primary',
        'border-2 border-primary bg-transparent text-primary hover:bg-primary hover:text-white': variant === 'secondary',
        'bg-transparent text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white': variant === 'ghost',
        'border-2 border-gray-300 dark:border-gray-600 bg-transparent text-gray-700 dark:text-gray-300 hover:border-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800': variant === 'outline',
        'bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white hover:from-indigo-600 hover:via-purple-600 hover:to-pink-600 shadow-lg hover:shadow-xl': variant === 'premium',
        
        // Sizes - Professional SaaS proportions with generous padding
        'h-8 px-4 text-xs min-w-[80px]': size === 'sm',
        'h-10 px-6 text-sm min-w-[100px]': size === 'md', 
        'h-12 px-8 text-base min-w-[120px]': size === 'lg',
        'h-14 px-10 text-lg min-w-[140px] font-bold': size === 'xl',
      },
      className
    );

    return (
      <button
        ref={ref}
        className={baseClasses}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <LoadingSpinner size="sm" className="mr-2" />
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button };