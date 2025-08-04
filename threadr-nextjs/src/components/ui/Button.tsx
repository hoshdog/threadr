'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { LoadingSpinner } from './LoadingSpinner';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  children: React.ReactNode;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', loading = false, disabled, children, ...props }, ref) => {
    const baseClasses = cn(
      'inline-flex items-center justify-center rounded-full font-semibold transition-colors',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-twitter-blue focus-visible:ring-offset-2',
      'disabled:pointer-events-none disabled:opacity-50',
      {
        // Variants - Twitter/X style
        'bg-twitter-blue text-white hover:bg-twitter-hover': variant === 'primary',
        'border border-twitter-border bg-transparent text-twitter-blue hover:bg-twitter-blue/10': variant === 'secondary',
        'bg-transparent text-twitter-blue hover:bg-twitter-blue/10': variant === 'ghost',
        
        // Sizes - Twitter/X exact proportions
        'h-8 px-3 text-xs': size === 'sm',
        'h-9 px-4 text-base': size === 'md',
        'h-11 px-6 text-base': size === 'lg',
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