import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@/types';
import { UserResponse } from '@/types/api';
import { authApi } from '@/lib/api';

// Helper function to transform API UserResponse to frontend User
const transformUserResponse = (userResponse: UserResponse): User => ({
  id: userResponse.user_id,
  email: userResponse.email,
  username: undefined, // Not provided in API response
  isPremium: userResponse.is_premium,
  premiumExpiresAt: userResponse.premium_expires_at || undefined,
  emailVerified: undefined, // Not provided in API response
  hasCompletedOnboarding: undefined, // Not provided in API response
  createdAt: userResponse.created_at,
  updatedAt: userResponse.created_at, // Use created_at as fallback for updatedAt
});
import { 
  setToken, 
  setRefreshToken, 
  setStoredUser, 
  removeToken,
  clearStoredUser,
  getToken,
  getStoredUser,
  isTokenExpired
} from '@/lib/utils/auth';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, username?: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  updateProfile: (updates: Partial<User>) => Promise<void>;
  clearError: () => void;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await authApi.login({ email, password });
          
          // Store tokens and user data
          setToken(response.access_token);
          if (response.refresh_token) {
            setRefreshToken(response.refresh_token);
          }
          const transformedUser = transformUserResponse(response.user);
          setStoredUser(transformedUser);
          
          set({ 
            user: transformedUser, 
            isAuthenticated: true, 
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          set({ 
            user: null, 
            isAuthenticated: false, 
            isLoading: false,
            error: error.message || 'Login failed'
          });
          throw error;
        }
      },

      register: async (email: string, password: string, username?: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await authApi.register({ email, password, username });
          
          // Store tokens and user data
          setToken(response.access_token);
          if (response.refresh_token) {
            setRefreshToken(response.refresh_token);
          }
          const transformedUser = transformUserResponse(response.user);
          setStoredUser(transformedUser);
          
          set({ 
            user: transformedUser, 
            isAuthenticated: true, 
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          set({ 
            user: null, 
            isAuthenticated: false, 
            isLoading: false,
            error: error.message || 'Registration failed'
          });
          throw error;
        }
      },

      logout: async () => {
        set({ isLoading: true });
        
        try {
          await authApi.logout();
        } catch (error) {
          // Continue with logout even if API call fails
          console.error('Logout API call failed:', error);
        } finally {
          // Clear all stored data
          removeToken();
          clearStoredUser();
          
          set({ 
            user: null, 
            isAuthenticated: false, 
            isLoading: false,
            error: null
          });
        }
      },

      checkAuth: async () => {
        const token = getToken();
        const storedUser = getStoredUser();
        
        // If no token, user is not authenticated
        if (!token) {
          set({ user: null, isAuthenticated: false, isLoading: false });
          return;
        }
        
        // If token is expired, clear auth state
        if (isTokenExpired(token)) {
          removeToken();
          clearStoredUser();
          set({ user: null, isAuthenticated: false, isLoading: false });
          return;
        }
        
        // If we have a stored user, use it immediately
        if (storedUser) {
          set({ user: storedUser, isAuthenticated: true, isLoading: false });
        }
        
        // Verify token with server and update user data
        try {
          set({ isLoading: true });
          const user = await authApi.getProfile();
          setStoredUser(user);
          set({ user, isAuthenticated: true, isLoading: false, error: null });
        } catch (error: any) {
          // If verification fails, clear auth state
          removeToken();
          clearStoredUser();
          set({ 
            user: null, 
            isAuthenticated: false, 
            isLoading: false,
            error: error.message || 'Authentication verification failed'
          });
        }
      },

      updateProfile: async (updates: Partial<User>) => {
        const currentUser = get().user;
        if (!currentUser) return;
        
        set({ isLoading: true, error: null });
        
        try {
          const updatedUser = await authApi.updateProfile(updates);
          setStoredUser(updatedUser);
          set({ user: updatedUser, isLoading: false, error: null });
        } catch (error: any) {
          set({ 
            isLoading: false,
            error: error.message || 'Profile update failed'
          });
          throw error;
        }
      },

      clearError: () => {
        set({ error: null });
      },

      setUser: (user: User) => {
        setStoredUser(user);
        set({ user, isAuthenticated: true });
      },
    }),
    {
      name: 'threadr-auth',
      partialize: (state) => ({ 
        user: state.user, 
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
);