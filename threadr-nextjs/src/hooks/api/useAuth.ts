import React from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api/auth';
import { User, LoginRequest, RegisterRequest, AuthResponse } from '@/types';
import { TokenResponse } from '@/types/api';
import { setToken, setRefreshToken, removeToken, getToken, getRefreshToken } from '@/lib/utils/auth';

// Query keys for authentication
export const authKeys = {
  all: ['auth'] as const,
  profile: () => [...authKeys.all, 'profile'] as const,
  refreshToken: () => [...authKeys.all, 'refresh'] as const,
  sessions: () => [...authKeys.all, 'sessions'] as const,
  devices: () => [...authKeys.all, 'devices'] as const,
} as const;

// Get current user profile
export function useProfile() {
  return useQuery({
    queryKey: authKeys.profile(),
    queryFn: authApi.getProfile,
    retry: (failureCount, error: any) => {
      // Don't retry on 401 (unauthorized)
      if (error?.status === 401) return false;
      return failureCount < 3;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Check if user is authenticated
export function useIsAuthenticated() {
  const { data: user, isLoading } = useProfile();
  const token = getToken();
  
  return {
    isAuthenticated: !!user && !!token,
    user,
    isLoading,
  };
}

// Login mutation
export function useLogin() {
  const queryClient = useQueryClient();
  const router = useRouter();
  
  return useMutation({
    mutationFn: (credentials: LoginRequest) => authApi.login(credentials),
    onSuccess: (data: TokenResponse) => {
      // Store tokens
      setToken(data.access_token);
      if (data.refresh_token) {
        setRefreshToken(data.refresh_token);
      }
      
      // Update user in cache
      queryClient.setQueryData(authKeys.profile(), data.user);
      
      // Invalidate all queries to refetch with new auth
      queryClient.invalidateQueries();
      
      // Redirect to dashboard after successful login
      router.push('/dashboard');
    },
    onError: (error) => {
      // Clear any existing auth data on login failure
      removeToken();
      queryClient.removeQueries({ queryKey: authKeys.profile() });
      console.error('Login failed:', error);
    },
  });
}

// Register mutation
export function useRegister() {
  const queryClient = useQueryClient();
  const router = useRouter();
  
  return useMutation({
    mutationFn: (userData: RegisterRequest) => authApi.register(userData),
    onSuccess: (data: TokenResponse) => {
      // Store tokens
      setToken(data.access_token);
      if (data.refresh_token) {
        setRefreshToken(data.refresh_token);
      }
      
      // Update user in cache
      queryClient.setQueryData(authKeys.profile(), data.user);
      
      // Invalidate all queries to refetch with new auth
      queryClient.invalidateQueries();
      
      // Redirect to dashboard after successful registration
      router.push('/dashboard');
    },
    onError: (error) => {
      console.error('Registration failed:', error);
    },
  });
}

// Logout mutation
export function useLogout() {
  const queryClient = useQueryClient();
  const router = useRouter();
  
  return useMutation({
    mutationFn: authApi.logout,
    onSuccess: () => {
      // Clear all tokens
      removeToken();
      
      // Clear all cached data
      queryClient.clear();
      
      // Redirect to login
      router.push('/login');
    },
    onError: (error) => {
      // Even if logout fails on server, clear local data
      console.error('Logout error (clearing local data anyway):', error);
      removeToken();
      queryClient.clear();
      
      // Redirect to login even on error
      router.push('/login');
    },
  });
}

// Update profile mutation with optimistic updates
export function useUpdateProfile() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (userData: Partial<User>) => authApi.updateProfile(userData),
    onMutate: async (newUserData) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: authKeys.profile() });
      
      // Snapshot the previous value
      const previousUser = queryClient.getQueryData<User>(authKeys.profile());
      
      // Optimistically update to the new value
      if (previousUser) {
        queryClient.setQueryData<User>(authKeys.profile(), {
          ...previousUser,
          ...newUserData,
        });
      }
      
      // Return a context object with the snapshotted value
      return { previousUser };
    },
    onError: (error, newUserData, context) => {
      // If the mutation fails, use the context returned from onMutate to roll back
      queryClient.setQueryData(authKeys.profile(), context?.previousUser);
      console.error('Profile update failed:', error);
    },
    onSuccess: (updatedUser: User) => {
      // Update user in cache with server response
      queryClient.setQueryData(authKeys.profile(), updatedUser);
    },
    onSettled: () => {
      // Always refetch after error or success to ensure we have the latest data
      queryClient.invalidateQueries({ queryKey: authKeys.profile() });
    },
  });
}

// Refresh token mutation
export function useRefreshToken() {
  const queryClient = useQueryClient();
  const router = useRouter();
  
  return useMutation({
    mutationFn: (refreshToken: string) => authApi.refreshToken(refreshToken),
    onSuccess: (data: TokenResponse) => {
      // Update tokens
      setToken(data.access_token);
      if (data.refresh_token) {
        setRefreshToken(data.refresh_token);
      }
      
      // Update user in cache if provided
      if (data.user) {
        queryClient.setQueryData(authKeys.profile(), data.user);
      }
      
      // Invalidate profile to refetch with new token
      queryClient.invalidateQueries({ queryKey: authKeys.profile() });
    },
    onError: (error) => {
      // If refresh fails, logout user
      console.error('Token refresh failed:', error);
      removeToken();
      queryClient.clear();
      
      // Redirect to login
      router.push('/login');
    },
  });
}

// Password reset request mutation
export function useRequestPasswordReset() {
  return useMutation({
    mutationFn: (email: string) => authApi.requestPasswordReset(email),
    onError: (error) => {
      console.error('Password reset request failed:', error);
    },
  });
}

// Password reset mutation
export function useResetPassword() {
  return useMutation({
    mutationFn: ({ token, password }: { token: string; password: string }) =>
      authApi.resetPassword(token, password),
    onError: (error) => {
      console.error('Password reset failed:', error);
    },
  });
}

// Change password mutation
export function useChangePassword() {
  return useMutation({
    mutationFn: ({ currentPassword, newPassword }: { currentPassword: string; newPassword: string }) =>
      authApi.changePassword(currentPassword, newPassword),
    onError: (error) => {
      console.error('Password change failed:', error);
    },
  });
}

// Delete account mutation
export function useDeleteAccount() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: authApi.deleteAccount,
    onSuccess: () => {
      // Clear all data
      removeToken();
      queryClient.clear();
      
      if (typeof window !== 'undefined') {
        window.location.href = '/';
      }
    },
    onError: (error) => {
      console.error('Account deletion failed:', error);
    },
  });
}

// Email verification mutation
export function useVerifyEmail() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (token: string) => authApi.verifyEmail(token),
    onSuccess: () => {
      // Refresh user profile to get updated verification status
      queryClient.invalidateQueries({ queryKey: authKeys.profile() });
    },
    onError: (error) => {
      console.error('Email verification failed:', error);
    },
  });
}

// Resend verification email mutation
export function useResendVerificationEmail() {
  return useMutation({
    mutationFn: () => authApi.resendVerificationEmail(),
    onError: (error) => {
      console.error('Resend verification email failed:', error);
    },
  });
}

// Get active sessions
export function useActiveSessions() {
  return useQuery({
    queryKey: authKeys.sessions(),
    queryFn: authApi.getActiveSessions,
    staleTime: 5 * 60 * 1000,
    // Only fetch if user is authenticated
    enabled: !!getToken(),
  });
}

// Revoke session mutation
export function useRevokeSession() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (sessionId: string) => authApi.revokeSession(sessionId),
    onSuccess: () => {
      // Refresh sessions list
      queryClient.invalidateQueries({ queryKey: authKeys.sessions() });
    },
    onError: (error) => {
      console.error('Session revocation failed:', error);
    },
  });
}

// Revoke all sessions mutation
export function useRevokeAllSessions() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: authApi.revokeAllSessions,
    onSuccess: () => {
      // Refresh sessions list
      queryClient.invalidateQueries({ queryKey: authKeys.sessions() });
    },
    onError: (error) => {
      console.error('Revoking all sessions failed:', error);
    },
  });
}

// Combined hook for auth status and user data
export function useAuthStatus() {
  const { data: user, isLoading, error } = useProfile();
  const token = getToken();
  
  return {
    user,
    isAuthenticated: !!user && !!token,
    isLoading,
    isError: !!error,
    error,
    isPremium: user?.isPremium || false,
    needsEmailVerification: user && !user.emailVerified,
    hasCompletedOnboarding: user?.hasCompletedOnboarding || false,
  };
}

// Hook for automatic token refresh
export function useTokenRefresh() {
  const refreshTokenMutation = useRefreshToken();
  const { user } = useAuthStatus();
  
  // Auto-refresh token when it's about to expire
  React.useEffect(() => {
    if (!user) return;
    
    const token = getToken();
    if (!token) return;
    
    try {
      // Decode JWT to check expiration (basic implementation)
      const tokenParts = token.split('.');
      if (tokenParts.length !== 3 || !tokenParts[1]) return;
      const payload = JSON.parse(atob(tokenParts[1]));
      const expiresAt = payload.exp * 1000;
      const now = Date.now();
      const timeUntilExpiry = expiresAt - now;
      
      // Refresh token 5 minutes before expiry
      const refreshTime = Math.max(0, timeUntilExpiry - 5 * 60 * 1000);
      
      const timeoutId = setTimeout(() => {
        const refreshToken = getRefreshToken();
        if (refreshToken) {
          refreshTokenMutation.mutate(refreshToken);
        }
      }, refreshTime);
      
      return () => clearTimeout(timeoutId);
    } catch (error) {
      console.error('Error parsing token for refresh:', error);
      return; // Explicit return for consistency
    }
  }, [user, refreshTokenMutation]);
  
  return refreshTokenMutation;
}

// Type guard for checking if user has specific permissions
export function useHasPermission() {
  const { user } = useAuthStatus();
  
  return (permission: string) => {
    if (!user) return false;
    // Implement your permission logic here
    // For now, just check if user is premium for premium features
    if (permission === 'premium') return user.isPremium;
    return true; // Default to allowing access
  };
}