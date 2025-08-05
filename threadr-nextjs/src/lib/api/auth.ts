import { apiClient } from './client';
import {
  User,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
} from '@/types';
import { TokenResponse, UserResponse, UserLoginRequest, UserRegistrationRequest } from '@/types/api';

// Transform frontend types to backend API types
const transformLoginRequest = (credentials: LoginRequest): UserLoginRequest => ({
  email: credentials.email,
  password: credentials.password,
  remember_me: false, // Default to false since frontend doesn't have this field
});

const transformRegisterRequest = (userData: RegisterRequest): UserRegistrationRequest => ({
  email: userData.email,
  password: userData.password,
  confirm_password: userData.password, // Use same password for confirmation
});

// Transform backend user response to frontend user type
const transformUserResponse = (userResponse: UserResponse): User => ({
  id: userResponse.user_id,
  email: userResponse.email,
  username: undefined, // Not provided in API response
  isPremium: userResponse.is_premium,
  premiumExpiresAt: userResponse.premium_expires_at || undefined,
  emailVerified: undefined, // Not provided in API response  
  hasCompletedOnboarding: undefined, // Not provided in API response
  createdAt: userResponse.created_at,
  updatedAt: userResponse.created_at, // Use created_at as fallback
});

export const authApi = {
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const apiRequest = transformLoginRequest(credentials);
    const response = await apiClient.post<TokenResponse>('/auth/login', apiRequest);
    
    // Transform user data in response
    if (response.user) {
      const transformedUser = transformUserResponse(response.user);
      return {
        ...response,
        user: transformedUser as any, // Cast to match TokenResponse type
      };
    }
    
    return response;
  },

  async register(userData: RegisterRequest): Promise<TokenResponse> {
    const apiRequest = transformRegisterRequest(userData);
    const response = await apiClient.post<TokenResponse>('/auth/register', apiRequest);
    
    // Transform user data in response
    if (response.user) {
      const transformedUser = transformUserResponse(response.user);
      return {
        ...response,
        user: transformedUser as any, // Cast to match TokenResponse type
      };
    }
    
    return response;
  },

  async logout(): Promise<void> {
    return apiClient.post('/auth/logout');
  },

  async getProfile(): Promise<User> {
    const userResponse = await apiClient.get<UserResponse>('/auth/me');
    return transformUserResponse(userResponse);
  },

  async updateProfile(userData: Partial<User>): Promise<User> {
    // Transform frontend user updates to backend format
    const apiUpdates: any = {};
    if (userData.email) apiUpdates.email = userData.email;
    // Add other fields as needed based on backend API
    
    const userResponse = await apiClient.put<UserResponse>('/auth/profile', apiUpdates);
    return transformUserResponse(userResponse);
  },

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/auth/token/refresh', { 
      refresh_token: refreshToken 
    });
    
    // Transform user data in response if present
    if (response.user) {
      const transformedUser = transformUserResponse(response.user);
      return {
        ...response,
        user: transformedUser as any,
      };
    }
    
    return response;
  },

  async requestPasswordReset(email: string): Promise<{ message: string }> {
    return apiClient.post('/auth/forgot-password', { email });
  },

  async resetPassword(token: string, password: string): Promise<{ message: string }> {
    return apiClient.post('/auth/reset-password', { token, password });
  },

  async changePassword(currentPassword: string, newPassword: string): Promise<{ message: string }> {
    return apiClient.post('/auth/change-password', {
      currentPassword,
      newPassword,
    });
  },

  async deleteAccount(): Promise<{ message: string }> {
    return apiClient.delete('/auth/account');
  },

  async verifyEmail(token: string): Promise<{ message: string }> {
    return apiClient.post('/auth/verify-email', { token });
  },

  async resendVerificationEmail(): Promise<{ message: string }> {
    return apiClient.post('/auth/resend-verification');
  },

  async getActiveSessions(): Promise<Array<{
    id: string;
    deviceInfo: string;
    ipAddress: string;
    location: string;
    lastActive: string;
    isCurrent: boolean;
  }>> {
    return apiClient.get('/auth/sessions');
  },

  async revokeSession(sessionId: string): Promise<{ message: string }> {
    return apiClient.delete(`/auth/sessions/${sessionId}`);
  },

  async revokeAllSessions(): Promise<{ message: string }> {
    return apiClient.delete('/auth/sessions');
  },
};