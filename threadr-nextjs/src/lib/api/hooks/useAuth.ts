import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authApi } from '../auth';
import { User, LoginRequest, RegisterRequest, AuthResponse } from '@/types';
import { TokenResponse } from '@/types/api';
import { setToken, removeToken } from '@/lib/utils/auth';

// Query keys
export const authKeys = {
  all: ['auth'] as const,
  profile: () => [...authKeys.all, 'profile'] as const,
  refreshToken: () => [...authKeys.all, 'refresh'] as const,
} as const;

// Custom hooks for authentication

// Get current user profile
export function useProfile() {
  return useQuery({
    queryKey: authKeys.profile(),
    queryFn: authApi.getProfile,
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Login mutation
export function useLogin() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (credentials: LoginRequest) => authApi.login(credentials),
    onSuccess: (data: TokenResponse) => {
      // Store token
      setToken(data.access_token);
      
      // Update user in cache
      queryClient.setQueryData(authKeys.profile(), data.user);
      
      // Invalidate all queries to refetch with new auth
      queryClient.invalidateQueries();
    },
    onError: () => {
      // Clear any existing auth data on login failure
      removeToken();
      queryClient.removeQueries({ queryKey: authKeys.profile() });
    },
  });
}

// Register mutation
export function useRegister() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (userData: RegisterRequest) => authApi.register(userData),
    onSuccess: (data: TokenResponse) => {
      // Store token
      setToken(data.access_token);
      
      // Update user in cache
      queryClient.setQueryData(authKeys.profile(), data.user);
      
      // Invalidate all queries to refetch with new auth
      queryClient.invalidateQueries();
    },
  });
}

// Logout mutation
export function useLogout() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: authApi.logout,
    onSuccess: () => {
      // Clear token
      removeToken();
      
      // Clear all cached data
      queryClient.clear();
      
      // Redirect to login (if in browser)
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    },
    onError: () => {
      // Even if logout fails on server, clear local data
      removeToken();
      queryClient.clear();
      
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    },
  });
}

// Update profile mutation
export function useUpdateProfile() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (userData: Partial<User>) => authApi.updateProfile(userData),
    onSuccess: (updatedUser: User) => {
      // Update user in cache
      queryClient.setQueryData(authKeys.profile(), updatedUser);
    },
  });
}

// Refresh token mutation
export function useRefreshToken() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: authApi.refreshToken,
    onSuccess: (data: TokenResponse) => {
      // Update token
      setToken(data.access_token);
      
      // Invalidate profile to refetch with new token
      queryClient.invalidateQueries({ queryKey: authKeys.profile() });
    },
    onError: () => {
      // If refresh fails, logout user
      removeToken();
      queryClient.clear();
      
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    },
  });
}

// Password reset request mutation
export function useRequestPasswordReset() {
  return useMutation({
    mutationFn: (email: string) => authApi.requestPasswordReset(email),
  });
}

// Password reset mutation
export function useResetPassword() {
  return useMutation({
    mutationFn: ({ token, password }: { token: string; password: string }) =>
      authApi.resetPassword(token, password),
  });
}

// Change password mutation
export function useChangePassword() {
  return useMutation({
    mutationFn: ({ currentPassword, newPassword }: { currentPassword: string; newPassword: string }) =>
      authApi.changePassword(currentPassword, newPassword),
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
  });
}