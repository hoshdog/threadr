'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { LoginForm } from '@/components/forms/LoginForm';
import { SocialLoginButtons } from '@/components/forms/SocialLoginButtons';
import { cn } from '@/lib/utils';
import Logo from '@/components/ui/Logo';
import { useAuth } from '@/contexts/auth';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  rememberMe: z.boolean(),
});

type LoginFormData = {
  email: string;
  password: string;
  rememberMe: boolean;
};

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading, error, clearError } = useAuth();
  const [localError, setLocalError] = React.useState<string | null>(null);

  const form = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false,
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    setLocalError(null);
    clearError();

    try {
      await login({
        email: data.email,
        password: data.password,
      });
      
      // Redirect to dashboard on successful login
      router.push('/dashboard');
    } catch (err: any) {
      const errorMessage = err.message || 'Invalid email or password. Please try again.';
      setLocalError(errorMessage);
      console.error('Login failed:', err);
    }
  };

  const handleSocialLogin = async (provider: 'google' | 'twitter') => {
    setLocalError(null);
    clearError();

    try {
      // TODO: Integrate with OAuth providers
      console.log(`${provider} login attempt`);
      
      // Simulate OAuth flow
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock success response
      router.push('/dashboard');
    } catch (err) {
      setLocalError(`Failed to sign in with ${provider}. Please try again.`);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        {/* Logo */}
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <Logo variant="black" size="lg" />
          </div>
          <p className="mt-2 text-sm text-muted-foreground">
            Convert your content into engaging Twitter threads
          </p>
        </div>

        <Card className="shadow-lg">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-semibold text-center">
              Sign in to your account
            </CardTitle>
            <CardDescription className="text-center">
              Welcome back! Please enter your details below.
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-6">
            {/* Error Message */}
            {(error || localError) && (
              <div className="p-3 rounded-md bg-destructive/10 border border-destructive/20">
                <p className="text-sm text-destructive text-center">{error || localError}</p>
              </div>
            )}

            {/* Social Login */}
            <SocialLoginButtons
              onGoogleLogin={() => handleSocialLogin('google')}
              onTwitterLogin={() => handleSocialLogin('twitter')}
              isLoading={isLoading}
            />

            {/* Divider */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-border" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">
                  Or continue with email
                </span>
              </div>
            </div>

            {/* Login Form */}
            <LoginForm
              form={form}
              onSubmit={onSubmit}
              isLoading={isLoading}
            />

            {/* Links */}
            <div className="flex items-center justify-between text-sm">
              <Link
                href="/forgot-password"
                className="text-accent hover:text-accent/80 transition-colors"
              >
                Forgot your password?
              </Link>
            </div>

            {/* Sign Up Link */}
            <div className="text-center text-sm">
              <span className="text-muted-foreground">Don't have an account? </span>
              <Link
                href="/register"
                className="text-accent hover:text-accent/80 font-medium transition-colors"
              >
                Sign up for free
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center text-xs text-muted-foreground">
          <p>
            By signing in, you agree to our{' '}
            <Link href="/terms" className="underline hover:text-foreground">
              Terms of Service
            </Link>{' '}
            and{' '}
            <Link href="/privacy" className="underline hover:text-foreground">
              Privacy Policy
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}