'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  requireAuth?: boolean;
  requirePremium?: boolean;
  redirectTo?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  fallback,
  requireAuth = true,
  requirePremium = false,
  redirectTo = '/login',
}) => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [hasChecked, setHasChecked] = useState(false);

  useEffect(() => {
    if (!isLoading) {
      setHasChecked(true);
      
      if (requireAuth && !isAuthenticated) {
        // Store the intended destination
        const currentPath = window.location.pathname + window.location.search;
        sessionStorage.setItem('redirectAfterLogin', currentPath);
        router.push(redirectTo);
        return;
      }
      
      if (requirePremium && user && !user.isPremium) {
        router.push('/upgrade');
        return;
      }
    }
  }, [isLoading, isAuthenticated, user, requireAuth, requirePremium, router, redirectTo]);

  // Show loading state while checking authentication
  if (!hasChecked || isLoading) {
    return (
      fallback || (
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      )
    );
  }

  // If auth is required but user is not authenticated, show nothing (redirect is in effect)
  if (requireAuth && !isAuthenticated) {
    return null;
  }

  // If premium is required but user doesn't have premium, show nothing (redirect is in effect)
  if (requirePremium && user && !user.isPremium) {
    return null;
  }

  return <>{children}</>;
};

export default ProtectedRoute;