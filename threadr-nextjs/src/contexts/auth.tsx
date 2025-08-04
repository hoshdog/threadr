'use client';

import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { User, LoginRequest, RegisterRequest } from '@/types';
import { TokenResponse, UserResponse } from '@/types/api';
import { authApi } from '@/lib/api';
import {
  getToken,
  getRefreshToken,
  setToken,
  setRefreshToken,
  setStoredUser,
  removeToken,
  clearStoredUser,
  getStoredUser,
  isTokenExpired,
  shouldRefreshToken,
  getUserFromToken,
} from '@/lib/utils/auth';

// Helper function to transform UserResponse to User
function transformUserResponse(userResponse: UserResponse): User {
  return {
    id: userResponse.user_id,
    email: userResponse.email,
    isPremium: userResponse.is_premium,
    premiumExpiresAt: userResponse.premium_expires_at || undefined,
    createdAt: userResponse.created_at,
    updatedAt: userResponse.created_at, // Use created_at as fallback since backend doesn't have updated_at
    emailVerified: true, // Assume verified if user exists
    hasCompletedOnboarding: true, // Assume completed if user exists
  };
}

interface AuthContextType {
  // State
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshTokens: () => Promise<void>;
  checkAuth: () => Promise<void>;
  updateProfile: (updates: Partial<User>) => Promise<void>;
  clearError: () => void;
  
  // Utilities
  isTokenValid: () => boolean;
  getAuthHeaders: () => { Authorization: string } | {};
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const router = useRouter();
  const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isRefreshingRef = useRef(false);
  
  // Clear any existing refresh timeout
  const clearRefreshTimeout = useCallback(() => {
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current);
      refreshTimeoutRef.current = null;
    }
  }, []);
  
  // Schedule automatic token refresh
  const scheduleTokenRefresh = useCallback((token: string) => {
    clearRefreshTimeout();
    
    try {
      const parts = token.split('.');
      if (parts.length !== 3) return;
      
      const payload = JSON.parse(atob(parts[1] || ''));
      const currentTime = Date.now() / 1000;
      const timeUntilExpiry = payload.exp - currentTime;
      
      // Schedule refresh 5 minutes before expiry, but not less than 1 minute from now
      const refreshIn = Math.max(timeUntilExpiry - 300, 60) * 1000;
      
      refreshTimeoutRef.current = setTimeout(() => {
        if (!isRefreshingRef.current) {
          refreshTokens();
        }
      }, refreshIn);
      
      console.log(`🔄 Token refresh scheduled in ${Math.round(refreshIn / 1000 / 60)} minutes`);
    } catch (error) {
      console.error('Failed to schedule token refresh:', error);
    }
  }, [clearRefreshTimeout]);
  
  // Check if current token is valid
  const isTokenValid = useCallback((): boolean => {
    const token = getToken();
    return token ? !isTokenExpired(token) : false;
  }, []);
  
  // Get auth headers for API requests
  const getAuthHeaders = useCallback(() => {
    const token = getToken();
    return token && !isTokenExpired(token) 
      ? { Authorization: `Bearer ${token}` }
      : {};
  }, []);
  
  // Refresh tokens
  const refreshTokens = useCallback(async () => {
    if (isRefreshingRef.current) {
      console.log('🔄 Token refresh already in progress, skipping...');
      return;
    }
    
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      console.log('🔄 No refresh token available, logging out...');
      await logout();
      return;
    }
    
    isRefreshingRef.current = true;
    console.log('🔄 Refreshing tokens...');
    
    try {
      // Use the refresh endpoint from your backend
      const response = await authApi.refreshToken(refreshToken);
      
      // Store new tokens
      setToken(response.access_token);
      if (response.refresh_token) {
        setRefreshToken(response.refresh_token);
      }
      
      // Update user data if provided
      if (response.user) {
        const transformedUser = transformUserResponse(response.user);
        setStoredUser(transformedUser);
        setUser(transformedUser);
        setIsAuthenticated(true);
      }
      
      // Schedule next refresh
      scheduleTokenRefresh(response.access_token);
      
      console.log('✅ Tokens refreshed successfully');
    } catch (error: any) {
      console.error('❌ Token refresh failed:', error);
      
      // If refresh fails, logout user
      await logout();
      
      // Don't show error for automatic refresh failures
      if (error.message !== 'Token refresh failed') {
        setError('Session expired. Please log in again.');
      }
    } finally {
      isRefreshingRef.current = false;
    }
  }, [scheduleTokenRefresh]);
  
  // Login function
  const login = useCallback(async (credentials: LoginRequest) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await authApi.login(credentials);
      
      // Store tokens and user data
      setToken(response.access_token);
      if (response.refresh_token) {
        setRefreshToken(response.refresh_token);
      }
      const transformedUser = transformUserResponse(response.user);
      setStoredUser(transformedUser);
      
      // Update state
      setUser(transformedUser);
      setIsAuthenticated(true);
      
      // Schedule token refresh
      scheduleTokenRefresh(response.access_token);
      
      console.log('✅ Login successful');
    } catch (error: any) {
      const errorMessage = error.message || 'Login failed';
      setError(errorMessage);
      console.error('❌ Login failed:', errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [scheduleTokenRefresh]);
  
  // Register function
  const register = useCallback(async (userData: RegisterRequest) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await authApi.register(userData);
      
      // Store tokens and user data
      setToken(response.access_token);
      if (response.refresh_token) {
        setRefreshToken(response.refresh_token);
      }
      const transformedUser = transformUserResponse(response.user);
      setStoredUser(transformedUser);
      
      // Update state
      setUser(transformedUser);
      setIsAuthenticated(true);
      
      // Schedule token refresh
      scheduleTokenRefresh(response.access_token);
      
      console.log('✅ Registration successful');
    } catch (error: any) {
      const errorMessage = error.message || 'Registration failed';
      setError(errorMessage);
      console.error('❌ Registration failed:', errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [scheduleTokenRefresh]);
  
  // Logout function
  const logout = useCallback(async () => {
    setIsLoading(true);
    clearRefreshTimeout();
    
    try {
      // Call logout API endpoint
      await authApi.logout();
    } catch (error) {
      // Continue with logout even if API call fails
      console.error('Logout API call failed:', error);
    }
    
    // Clear all stored data
    removeToken();
    clearStoredUser();
    
    // Reset state
    setUser(null);
    setIsAuthenticated(false);
    setError(null);
    setIsLoading(false);
    
    // Redirect to login page
    router.push('/login');
    
    console.log('✅ Logout successful');
  }, [router, clearRefreshTimeout]);
  
  // Check authentication status
  const checkAuth = useCallback(async () => {
    const token = getToken();
    const storedUser = getStoredUser();
    
    // If no token, user is not authenticated
    if (!token) {
      setUser(null);
      setIsAuthenticated(false);
      setIsLoading(false);
      return;
    }
    
    // If token is expired, try to refresh
    if (isTokenExpired(token)) {
      console.log('🔄 Token expired, attempting refresh...');
      await refreshTokens();
      return;
    }
    
    // If token expires soon, refresh proactively
    if (shouldRefreshToken(token)) {
      console.log('🔄 Token expires soon, refreshing proactively...');
      refreshTokens(); // Don't await - let it run in background
    }
    
    // If we have a stored user, use it immediately
    if (storedUser) {
      setUser(storedUser);
      setIsAuthenticated(true);
      scheduleTokenRefresh(token);
    }
    
    // Verify token with server and update user data
    try {
      const user = await authApi.getProfile();
      setStoredUser(user);
      setUser(user);
      setIsAuthenticated(true);
      setError(null);
      
      // Schedule token refresh
      scheduleTokenRefresh(token);
      
      console.log('✅ Authentication verified');
    } catch (error: any) {
      console.error('❌ Auth verification failed:', error);
      
      // If verification fails, try refresh
      if (getRefreshToken()) {
        await refreshTokens();
      } else {
        // Clear auth state if no refresh token
        removeToken();
        clearStoredUser();
        setUser(null);
        setIsAuthenticated(false);
        setError('Authentication verification failed');
      }
    } finally {
      setIsLoading(false);
    }
  }, [refreshTokens, scheduleTokenRefresh]);
  
  // Update profile
  const updateProfile = useCallback(async (updates: Partial<User>) => {
    if (!user) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const updatedUser = await authApi.updateProfile(updates);
      setStoredUser(updatedUser);
      setUser(updatedUser);
      console.log('✅ Profile updated successfully');
    } catch (error: any) {
      const errorMessage = error.message || 'Profile update failed';
      setError(errorMessage);
      console.error('❌ Profile update failed:', errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [user]);
  
  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);
  
  // Initialize auth on mount
  useEffect(() => {
    checkAuth();
    
    // Cleanup on unmount
    return () => {
      clearRefreshTimeout();
    };
  }, [checkAuth, clearRefreshTimeout]);
  
  // Handle page visibility changes
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && isAuthenticated) {
        // Check auth when page becomes visible
        const token = getToken();
        if (token && shouldRefreshToken(token)) {
          refreshTokens();
        }
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [isAuthenticated, refreshTokens]);
  
  // Handle online/offline events
  useEffect(() => {
    const handleOnline = () => {
      if (isAuthenticated) {
        checkAuth();
      }
    };
    
    window.addEventListener('online', handleOnline);
    return () => window.removeEventListener('online', handleOnline);
  }, [isAuthenticated, checkAuth]);
  
  const value: AuthContextType = {
    // State
    user,
    isAuthenticated,
    isLoading,
    error,
    
    // Actions
    login,
    register,
    logout,
    refreshTokens,
    checkAuth,
    updateProfile,
    clearError,
    
    // Utilities
    isTokenValid,
    getAuthHeaders,
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;