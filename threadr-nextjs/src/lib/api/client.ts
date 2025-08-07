import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { ApiError, ApiResponse } from '@/types';
import { getToken, getRefreshToken, setToken, setRefreshToken, removeToken, isTokenExpired, shouldRefreshToken } from '@/lib/utils/auth';
import { getApiConfig } from './config';

// Retry configuration
interface RetryConfig {
  retries: number;
  retryDelay: number;
  retryCondition?: (error: AxiosError) => boolean;
}

class ApiClient {
  private client: AxiosInstance;
  private retryConfig: RetryConfig;
  private config = getApiConfig();
  private isRefreshing = false;
  private refreshSubscribers: Array<(token: string) => void> = [];

  constructor(retryConfig: Partial<RetryConfig> = {}) {
    const defaultRetryConfig: RetryConfig = {
      retries: this.config.RETRY.ATTEMPTS,
      retryDelay: this.config.RETRY.DELAY,
      retryCondition: (error: AxiosError) => {
        // Retry on network errors or 5xx server errors
        return !error.response || (error.response.status >= 500 && error.response.status < 600);
      },
    };
    
    this.retryConfig = { ...defaultRetryConfig, ...retryConfig };
    
    this.client = axios.create({
      baseURL: this.config.BASE_URL,
      timeout: this.config.TIMEOUT,
      headers: this.config.HEADERS,
    });

    this.setupInterceptors();
  }

  // Token refresh queue management
  private addRefreshSubscriber(callback: (token: string) => void) {
    this.refreshSubscribers.push(callback);
  }

  private onTokenRefreshed(token: string) {
    this.refreshSubscribers.forEach((callback) => callback(token));
    this.refreshSubscribers = [];
  }

  private async refreshTokenIfNeeded(): Promise<string | null> {
    const token = getToken();
    const refreshToken = getRefreshToken();

    // No tokens available - user not authenticated
    if (!token || !refreshToken) {
      return null;
    }

    // If token is still valid and doesn't need refresh, return it
    if (!isTokenExpired(token) && !shouldRefreshToken(token)) {
      return token;
    }

    // If already refreshing, wait for the current refresh to complete
    if (this.isRefreshing) {
      return new Promise((resolve) => {
        this.addRefreshSubscriber((newToken: string) => {
          resolve(newToken);
        });
      });
    }

    this.isRefreshing = true;

    try {
      const response = await axios.post(`${this.config.BASE_URL}/auth/token/refresh`, {
        refresh_token: refreshToken,
      });

      const { access_token, refresh_token: newRefreshToken } = response.data.data || response.data;

      // Store new tokens
      setToken(access_token);
      if (newRefreshToken) {
        setRefreshToken(newRefreshToken);
      }

      // Notify all subscribers
      this.onTokenRefreshed(access_token);

      return access_token;
    } catch (error) {
      console.error('Token refresh failed:', error);
      
      // Clear tokens and redirect to login
      removeToken();
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
      
      return null;
    } finally {
      this.isRefreshing = false;
    }
  }

  private setupInterceptors() {
    // Request interceptor to add auth token and handle token refresh
    this.client.interceptors.request.use(
      async (config) => {
        // Define public endpoints that don't need authentication
        const publicEndpoints = [
          '/auth/login',
          '/auth/register', 
          '/auth/forgot-password',
          '/auth/reset-password',
          '/subscriptions/plans',  // Public pricing plans
          '/health',
          '/readiness'
        ];
        
        // Check if this is a public endpoint - more robust matching
        const isPublicEndpoint = publicEndpoints.some(endpoint => {
          // Handle exact match or endpoint at end of URL
          return config.url === endpoint || config.url?.endsWith(endpoint);
        });
        
        if (isPublicEndpoint) {
          // Log public endpoint access in development
          if (this.config.FEATURES.ENABLE_REQUEST_LOGGING) {
            console.log(`🔓 Public endpoint: ${config.method?.toUpperCase()} ${config.url} (no auth required)`);
          }
          return config;
        }

        // Try to refresh token if needed for protected endpoints
        const token = await this.refreshTokenIfNeeded();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
          
          // Log authenticated request in development
          if (this.config.FEATURES.ENABLE_REQUEST_LOGGING) {
            console.log(`🔒 Protected endpoint: ${config.method?.toUpperCase()} ${config.url} (auth added)`);
          }
        } else {
          // No valid token for protected endpoint - still send request but backend will reject
          if (this.config.FEATURES.ENABLE_REQUEST_LOGGING) {
            console.log(`⚠️ Protected endpoint without auth: ${config.method?.toUpperCase()} ${config.url} (will likely fail)`);
          }
        }
        
        // Log requests in development
        if (this.config.FEATURES.ENABLE_REQUEST_LOGGING) {
          console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
            data: config.data,
            params: config.params,
          });
        }
        
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle errors, retries, and logging
    this.client.interceptors.response.use(
      (response: AxiosResponse<ApiResponse>) => {
        // Log successful responses in development
        if (this.config.FEATURES.ENABLE_RESPONSE_LOGGING) {
          console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`, {
            status: response.status,
            data: response.data,
          });
        }
        return response;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config as any;
        
        // Handle 401 errors
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          // Try to refresh token
          const newToken = await this.refreshTokenIfNeeded();
          if (newToken) {
            // Retry the original request with new token
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return this.client.request(originalRequest);
          } else {
            // Refresh failed, redirect to login
            removeToken();
            if (typeof window !== 'undefined') {
              window.location.href = '/login';
            }
            return Promise.reject(error);
          }
        }

        // Retry logic
        if (
          this.retryConfig.retryCondition?.(error) &&
          originalRequest &&
          !originalRequest._retry &&
          (originalRequest._retryCount || 0) < this.retryConfig.retries
        ) {
          originalRequest._retry = true;
          originalRequest._retryCount = (originalRequest._retryCount || 0) + 1;
          
          // Exponential backoff with max delay
          const delay = Math.min(
            this.retryConfig.retryDelay * Math.pow(2, originalRequest._retryCount - 1),
            this.config.RETRY.MAX_DELAY
          );
          await new Promise(resolve => setTimeout(resolve, delay));
          
          return this.client.request(originalRequest);
        }

        // Log errors in development
        if (this.config.FEATURES.ENABLE_RESPONSE_LOGGING) {
          const errorData = error.response?.data as any;
          console.error(`❌ API Error: ${error.config?.method?.toUpperCase()} ${error.config?.url}`, {
            status: error.response?.status,
            message: errorData?.error || error.message,
            data: error.response?.data,
          });
        }

        const errorData = error.response?.data as any;
        const message = errorData?.error || error.message || 'An error occurred';
        const status = error.response?.status || 500;
        const code = errorData?.code;

        throw new ApiError(message, status, code);
      }
    );
  }

  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<ApiResponse<T>>(url, config);
    if (!response.data.success) {
      throw new ApiError(response.data.error || 'Request failed', response.status);
    }
    return response.data.data as T;
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<ApiResponse<T>>(url, data, config);
    if (!response.data.success) {
      throw new ApiError(response.data.error || 'Request failed', response.status);
    }
    return response.data.data as T;
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<ApiResponse<T>>(url, data, config);
    if (!response.data.success) {
      throw new ApiError(response.data.error || 'Request failed', response.status);
    }
    return response.data.data as T;
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<ApiResponse<T>>(url, config);
    if (!response.data.success) {
      throw new ApiError(response.data.error || 'Request failed', response.status);
    }
    return response.data.data as T;
  }

  // Raw methods for special cases
  async getRaw<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.get<T>(url, config);
  }

  async postRaw<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.post<T>(url, data, config);
  }

  // Health check method
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    try {
      const response = await this.getRaw<{ status: string; timestamp: string }>('/health');
      return response.data;
    } catch (error) {
      throw new ApiError('Health check failed', 503);
    }
  }

  // Method to update retry configuration
  updateRetryConfig(config: Partial<RetryConfig>): void {
    this.retryConfig = { ...this.retryConfig, ...config };
  }

  // Method to get current base URL
  getBaseURL(): string {
    return this.client.defaults.baseURL || '';
  }
}

export const apiClient = new ApiClient();
export default apiClient;