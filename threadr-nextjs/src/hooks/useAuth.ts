import { useEffect } from 'react';
import { useAuthStore } from '@/lib/stores';

export const useAuth = () => {
  const {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    checkAuth,
    updateProfile,
    clearError,
  } = useAuthStore();

  useEffect(() => {
    // Check authentication status on mount
    checkAuth();
  }, [checkAuth]);

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    updateProfile,
    clearError,
    // Computed properties
    isPremium: user?.isPremium || false,
    userId: user?.id,
    userEmail: user?.email,
  };
};