'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth';

interface UseAuthGuardOptions {
  requireAuth?: boolean;
  requirePremium?: boolean;
  redirectTo?: string;
  onUnauthorized?: () => void;
}

export const useAuthGuard = (options: UseAuthGuardOptions = {}) => {
  const {
    requireAuth = true,
    requirePremium = false,
    redirectTo = '/login',
    onUnauthorized,
  } = options;

  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;

    // Check authentication requirement
    if (requireAuth && !isAuthenticated) {
      if (onUnauthorized) {
        onUnauthorized();
      } else {
        // Store current path for redirect after login
        const currentPath = window.location.pathname + window.location.search;
        sessionStorage.setItem('redirectAfterLogin', currentPath);
        router.push(redirectTo);
      }
      return;
    }

    // Check premium requirement
    if (requirePremium && user && !user.isPremium) {
      if (onUnauthorized) {
        onUnauthorized();
      } else {
        router.push('/upgrade');
      }
      return;
    }
  }, [
    isLoading,
    isAuthenticated,
    user,
    requireAuth,
    requirePremium,
    redirectTo,
    onUnauthorized,
    router,
  ]);

  return {
    isAuthorized: requireAuth ? isAuthenticated : true,
    hasPremium: user?.isPremium || false,
    isLoading,
    user,
  };
};

export default useAuthGuard;