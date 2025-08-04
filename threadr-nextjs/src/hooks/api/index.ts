// Export all React Query hooks for Threadr API
// This is the main entry point for all API hooks

// Authentication hooks
export * from './useAuth';
export type { authKeys } from './useAuth';

// Thread management hooks
export * from './useThreads';
export type { threadKeys } from './useThreads';

// Template hooks
export * from './useTemplates';
export type { templateKeys, CreateTemplateRequest, GenerateFromTemplateRequest, TemplateStats } from './useTemplates';

// Analytics hooks
export * from './useAnalytics';
export type { 
  analyticsKeys, 
  UsageMetrics, 
  PerformanceMetrics, 
  ContentAnalysis, 
  EngagementData, 
  RevenueAnalytics, 
  UserBehaviorAnalytics 
} from './useAnalytics';

// Subscription and payment hooks
export * from './useSubscription';
export type { subscriptionKeys } from './useSubscription';

// Re-export commonly used query client utilities
export { useQueryClient, useIsFetching, useIsMutating } from '@tanstack/react-query';

// Utility hook for invalidating all user data
import { useQueryClient } from '@tanstack/react-query';
import { authKeys } from './useAuth';
import { threadKeys } from './useThreads';
import { templateKeys } from './useTemplates';
import { analyticsKeys } from './useAnalytics';
import { subscriptionKeys } from './useSubscription';

export function useInvalidateAllUserData() {
  const queryClient = useQueryClient();
  
  return () => {
    // Invalidate all user-specific data
    queryClient.invalidateQueries({ queryKey: authKeys.all });
    queryClient.invalidateQueries({ queryKey: threadKeys.all });
    queryClient.invalidateQueries({ queryKey: templateKeys.all });
    queryClient.invalidateQueries({ queryKey: analyticsKeys.all });
    queryClient.invalidateQueries({ queryKey: subscriptionKeys.all });
  };
}

// Utility hook for clearing all cached data
export function useClearAllCache() {
  const queryClient = useQueryClient();
  
  return () => {
    queryClient.clear();
  };
}

// Combined hook for app initialization data
export function useAppInitialization() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuthStatus();
  const { data: usage, isLoading: usageLoading } = useThreadUsageStats();
  const { data: premiumStatus, isLoading: premiumLoading } = useThreadPremiumStatus();
  
  return {
    user,
    isAuthenticated,
    usage,
    premiumStatus,
    isLoading: authLoading || usageLoading || premiumLoading,
    isInitialized: !authLoading && (isAuthenticated ? (!usageLoading && !premiumLoading) : true),
  };
}

// Import the individual hooks for the combined hook
import { useAuthStatus } from './useAuth';
import { useThreadUsageStats, useThreadPremiumStatus } from './useThreads';