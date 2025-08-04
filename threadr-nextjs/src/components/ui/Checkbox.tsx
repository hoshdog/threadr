'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, label, error, helperText, id, children, ...props }, ref) => {
    const checkboxId = id || `checkbox-${Math.random().toString(36).substring(2, 15)}`;

    return (
      <div className="w-full">
        <div className="flex items-start">
          <input
            type="checkbox"
            id={checkboxId}
            className={cn(
              'mt-1 h-4 w-4 rounded border-border bg-background',
              'text-accent focus:ring-2 focus:ring-accent focus:ring-offset-2',
              'disabled:cursor-not-allowed disabled:opacity-50',
              error && 'border-destructive focus:ring-destructive',
              className
            )}
            ref={ref}
            {...props}
          />
          {(label || children) && (
            <label
              htmlFor={checkboxId}
              className="ml-2 text-sm text-foreground cursor-pointer leading-5"
            >
              {label || children}
            </label>
          )}
        </div>
        {(error || helperText) && (
          <p
            className={cn(
              'mt-1 ml-6 text-sm',
              error ? 'text-destructive' : 'text-muted-foreground'
            )}
          >
            {error || helperText}
          </p>
        )}
      </div>
    );
  }
);

Checkbox.displayName = 'Checkbox';

export { Checkbox };