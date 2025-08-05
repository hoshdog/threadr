// Export all API modules
export { apiClient, default as client } from './client';
export { authApi } from './auth';
export { threadsApi } from './threads';
export { analyticsApi } from './analytics';
export { templatesApi } from './templates';
export { subscriptionsApi } from './subscriptions';

// Export React Query hooks
export * from './hooks';

// Re-export types for convenience
export type { ApiResponse, ApiError } from '@/types';
export type { Template, TemplateCategory, CreateTemplateRequest, GenerateFromTemplateRequest } from './templates';
export type { 
  SubscriptionStatus, 
  PaymentMethod, 
  Invoice, 
  BillingHistory, 
  UsageDetails, 
  CreateSubscriptionRequest, 
  UpdateSubscriptionRequest, 
  CreatePaymentIntentRequest 
} from './subscriptions';