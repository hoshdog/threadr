'use client';

import React from 'react';
import { UseFormReturn } from 'react-hook-form';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Checkbox } from '@/components/ui/Checkbox';
import { PasswordStrengthIndicator } from './PasswordStrengthIndicator';
import { cn } from '@/lib/utils';

interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
  username?: string;
  acceptTerms: boolean;
}

interface RegisterFormProps {
  form: UseFormReturn<RegisterFormData>;
  onSubmit: (data: RegisterFormData) => Promise<void>;
  isLoading: boolean;
  className?: string;
}

export function RegisterForm({ form, onSubmit, isLoading, className }: RegisterFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = form;

  const password = watch('password');

  return (
    <form 
      onSubmit={handleSubmit(onSubmit)} 
      className={cn('space-y-4', className)}
    >
      {/* Username Field (Optional) */}
      <div>
        <Input
          {...register('username')}
          type="text"
          label="Username (optional)"
          placeholder="Choose a username"
          error={errors.username?.message}
          disabled={isLoading}
          autoComplete="username"
        />
      </div>

      {/* Email Field */}
      <div>
        <Input
          {...register('email')}
          type="email"
          label="Email address"
          placeholder="Enter your email"
          error={errors.email?.message}
          disabled={isLoading}
          required
          autoComplete="email"
        />
      </div>

      {/* Password Field */}
      <div>
        <Input
          {...register('password')}
          type="password"
          label="Password"
          placeholder="Create a password"
          error={errors.password?.message}
          disabled={isLoading}
          required
          autoComplete="new-password"
        />
        {/* Password Strength Indicator */}
        {password && (
          <div className="mt-2">
            <PasswordStrengthIndicator password={password} />
          </div>
        )}
      </div>

      {/* Confirm Password Field */}
      <div>
        <Input
          {...register('confirmPassword')}
          type="password"
          label="Confirm password"
          placeholder="Confirm your password"
          error={errors.confirmPassword?.message}
          disabled={isLoading}
          required
          autoComplete="new-password"
        />
      </div>

      {/* Terms and Conditions Checkbox */}
      <div>
        <Checkbox
          {...register('acceptTerms')}
          id="acceptTerms"
          error={errors.acceptTerms?.message}
          disabled={isLoading}
        >
          I agree to the{' '}
          <Link 
            href="/terms" 
            className="text-accent hover:text-accent/80 underline"
            target="_blank"
          >
            Terms of Service
          </Link>{' '}
          and{' '}
          <Link 
            href="/privacy" 
            className="text-accent hover:text-accent/80 underline"
            target="_blank"
          >
            Privacy Policy
          </Link>
        </Checkbox>
      </div>

      {/* Submit Button */}
      <Button
        type="submit"
        variant="primary"
        size="lg"
        loading={isLoading}
        disabled={isLoading}
        className="w-full"
      >
        {isLoading ? 'Creating account...' : 'Create account'}
      </Button>
    </form>
  );
}