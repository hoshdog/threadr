// API Configuration
export const API_CONFIG = {
  // Base URL - use production by default, fallback to localhost for development
  BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 
           (process.env.NEXT_PUBLIC_API_URL ? process.env.NEXT_PUBLIC_API_URL + '/api' : null) || 
           'https://threadr-production.up.railway.app/api',
  
  // Timeouts
  TIMEOUT: 30000, // 30 seconds
  
  // Retry configuration
  RETRY: {
    ATTEMPTS: 3,
    DELAY: 1000, // Base delay in milliseconds
    MAX_DELAY: 30000, // Maximum delay for exponential backoff
  },
  
  // Cache settings (for React Query)
  CACHE: {
    STALE_TIME: 60 * 1000, // 1 minute
    GC_TIME: 5 * 60 * 1000, // 5 minutes (garbage collection time)
  },
  
  // Request headers
  HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    ...(process.env.NEXT_PUBLIC_API_KEY && { 'X-API-Key': process.env.NEXT_PUBLIC_API_KEY }),
  },
  
  // Feature flags
  FEATURES: {
    ENABLE_RETRY: true,
    ENABLE_REQUEST_LOGGING: process.env.NODE_ENV === 'development',
    ENABLE_RESPONSE_LOGGING: process.env.NODE_ENV === 'development',
    ENABLE_OFFLINE_SUPPORT: true,
  },
  
  // Endpoints
  ENDPOINTS: {
    // Authentication
    AUTH: {
      LOGIN: '/auth/login',
      REGISTER: '/auth/register',
      LOGOUT: '/auth/logout',
      PROFILE: '/auth/me',
      UPDATE_PROFILE: '/auth/profile',
      REFRESH: '/auth/refresh',
      FORGOT_PASSWORD: '/auth/forgot-password',
      RESET_PASSWORD: '/auth/reset-password',
      CHANGE_PASSWORD: '/auth/change-password',
      DELETE_ACCOUNT: '/auth/account',
    },
    
    // Threads
    THREADS: {
      GENERATE: '/generate',
      LIST: '/threads',
      DETAIL: (id: string) => `/threads/${id}`,
      CREATE: '/threads',
      UPDATE: (id: string) => `/threads/${id}`,
      DELETE: (id: string) => `/threads/${id}`,
      DUPLICATE: (id: string) => `/threads/${id}/duplicate`,
      SEARCH: '/threads/search',
      BY_TAG: (tag: string) => `/threads/tags/${encodeURIComponent(tag)}`,
      POPULAR_TAGS: '/threads/tags/popular',
    },
    
    // Templates
    TEMPLATES: {
      LIST: '/templates',
      DETAIL: (id: string) => `/templates/${id}`,
      CATEGORIES: '/templates/categories',
      POPULAR: '/templates/popular',
      FEATURED: '/templates/featured',
      BY_CATEGORY: (categoryId: string) => `/templates/category/${categoryId}`,
      GENERATE: '/templates/generate',
      CREATE: '/templates',
      UPDATE: (id: string) => `/templates/${id}`,
      DELETE: (id: string) => `/templates/${id}`,
      USER: '/templates/user',
      FAVORITE: (id: string) => `/templates/${id}/favorite`,
      FAVORITES: '/templates/favorites',
      RATE: (id: string) => `/templates/${id}/rate`,
      STATS: (id: string) => `/templates/${id}/stats`,
      SEARCH: '/templates/search',
      SUGGESTIONS: '/templates/suggestions',
    },
    
    // Analytics
    ANALYTICS: {
      DASHBOARD: '/analytics/dashboard',
      USAGE: '/analytics/usage',
      THREAD_STATS: (id: string) => `/analytics/threads/${id}/stats`,
      TOP_THREADS: '/analytics/threads/top',
      CONTENT: '/analytics/content',
      ENGAGEMENT: '/analytics/engagement',
    },
    
    // Utility
    UTILITY: {
      HEALTH: '/health',
      READINESS: '/readiness',
      USAGE_STATS: '/usage-stats',
      PREMIUM_STATUS: '/premium-status',
      CAPTURE_EMAIL: '/capture-email',
    },
  },
};

// Environment-specific overrides
export const getApiConfig = () => {
  const config = {
    ...API_CONFIG,
    RETRY: { ...API_CONFIG.RETRY },
    CACHE: { ...API_CONFIG.CACHE },
    HEADERS: { 
      ...API_CONFIG.HEADERS,
      ...(process.env.NEXT_PUBLIC_API_KEY && { 'X-API-Key': process.env.NEXT_PUBLIC_API_KEY }),
    },
    FEATURES: { ...API_CONFIG.FEATURES },
    ENDPOINTS: { ...API_CONFIG.ENDPOINTS },
  };
  
  // Development overrides
  if (process.env.NODE_ENV === 'development') {
    config.RETRY.ATTEMPTS = 1; // Fewer retries in development
    config.TIMEOUT = 10000; // Shorter timeout
  }
  
  // Production optimizations
  if (process.env.NODE_ENV === 'production') {
    config.FEATURES.ENABLE_REQUEST_LOGGING = false;
    config.FEATURES.ENABLE_RESPONSE_LOGGING = false;
  }
  
  // Test environment
  if (process.env.NODE_ENV === 'test') {
    config.BASE_URL = 'http://localhost:8001/api';
    config.TIMEOUT = 5000;
    config.RETRY.ATTEMPTS = 0; // No retries in tests
  }
  
  return config;
};

// Type for the configuration
export type ApiConfig = typeof API_CONFIG;