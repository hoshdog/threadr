'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth';

interface AuthLayoutProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  requirePremium?: boolean;
  fallback?: React.ReactNode;
  className?: string;
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({
  children,
  requireAuth = true,
  requirePremium = false,
  fallback,
  className = '',
}) => {
  const { user, isAuthenticated, isLoading, checkAuth } = useAuth();
  const router = useRouter();

  // Check auth on mount and when relevant state changes
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // Handle redirect after login
  useEffect(() => {
    if (isAuthenticated && typeof window !== 'undefined') {
      const redirectPath = sessionStorage.getItem('redirectAfterLogin');
      if (redirectPath && redirectPath !== window.location.pathname) {
        sessionStorage.removeItem('redirectAfterLogin');
        router.push(redirectPath);
      }
    }
  }, [isAuthenticated, router]);

  // Show loading state
  if (isLoading) {
    return (
      fallback || (
        <div className={`flex items-center justify-center min-h-screen ${className}`}>
          <div className="flex flex-col items-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-twitter-blue"></div>
            <p className="text-twitter-text-gray text-sm">Loading...</p>
          </div>
        </div>
      )
    );
  }

  // Check authentication
  if (requireAuth && !isAuthenticated) {
    return (
      <div className={`flex items-center justify-center min-h-screen ${className}`}>
        <div className="max-w-md mx-auto text-center p-6">
          <div className="mb-4">
            <svg
              className="mx-auto h-12 w-12 text-twitter-gray"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              />
            </svg>
          </div>
          <h2 className="text-lg font-semibold text-gray-900 mb-2">
            Authentication Required
          </h2>
          <p className="text-twitter-text-gray mb-4">
            Please log in to access this page.
          </p>
          <button
            onClick={() => router.push('/login')}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-twitter-blue hover:bg-twitter-hover focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-twitter-blue"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  // Check premium requirement
  if (requirePremium && user && !user.isPremium) {
    return (
      <div className={`flex items-center justify-center min-h-screen ${className}`}>
        <div className="max-w-md mx-auto text-center p-6">
          <div className="mb-4">
            <svg
              className="mx-auto h-12 w-12 text-yellow-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"
              />
            </svg>
          </div>
          <h2 className="text-lg font-semibold text-gray-900 mb-2">
            Premium Required
          </h2>
          <p className="text-twitter-text-gray mb-4">
            This feature requires a premium subscription.
          </p>
          <button
            onClick={() => router.push('/upgrade')}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-yellow-600 hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
          >
            Upgrade to Premium
          </button>
        </div>
      </div>
    );
  }

  // Render children if all checks pass
  return <div className={className}>{children}</div>;
};

export default AuthLayout;