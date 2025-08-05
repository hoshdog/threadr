import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '../analytics';

// Query keys
export const analyticsKeys = {
  all: ['analytics'] as const,
  dashboard: () => [...analyticsKeys.all, 'dashboard'] as const,
  usage: (period: string) => [...analyticsKeys.all, 'usage', period] as const,
  threadStats: (threadId: string) => [...analyticsKeys.all, 'thread-stats', threadId] as const,
  topThreads: (limit: number) => [...analyticsKeys.all, 'top-threads', limit] as const,
  content: () => [...analyticsKeys.all, 'content'] as const,
  engagement: (period: string) => [...analyticsKeys.all, 'engagement', period] as const,
} as const;

// Get analytics dashboard
export function useAnalyticsDashboard(period?: 'day' | 'week' | 'month' | 'year') {
  return useQuery({
    queryKey: analyticsKeys.dashboard(),
    queryFn: () => analyticsApi.getDashboard(period),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 10 * 60 * 1000, // Refetch every 10 minutes
  });
}

// Get usage statistics
export function useUsageStats(period: 'day' | 'week' | 'month' | 'year' = 'month') {
  return useQuery({
    queryKey: analyticsKeys.usage(period),
    queryFn: () => analyticsApi.getUsageStats(period),
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });
}

// Get thread statistics
export function useThreadStats(threadId: string, enabled = true) {
  return useQuery({
    queryKey: analyticsKeys.threadStats(threadId),
    queryFn: () => analyticsApi.getThreadStats(threadId),
    enabled: !!threadId && enabled,
    staleTime: 5 * 60 * 1000,
    refetchInterval: 15 * 60 * 1000, // Refetch every 15 minutes
  });
}

// Get top performing threads
export function useTopPerformingThreads(limit = 10) {
  return useQuery({
    queryKey: analyticsKeys.topThreads(limit),
    queryFn: () => analyticsApi.getTopPerformingThreads(limit),
    staleTime: 10 * 60 * 1000, // 10 minutes
    refetchInterval: 30 * 60 * 1000, // Refetch every 30 minutes
  });
}

// Get content analysis
export function useContentAnalysis(period?: 'day' | 'week' | 'month' | 'year') {
  return useQuery({
    queryKey: analyticsKeys.content(),
    queryFn: () => analyticsApi.getContentAnalysis(period),
    staleTime: 15 * 60 * 1000, // 15 minutes
    refetchInterval: 60 * 60 * 1000, // Refetch every hour
  });
}

// Get engagement metrics
export function useEngagementMetrics(period: 'day' | 'week' | 'month' | 'year' = 'month') {
  return useQuery({
    queryKey: analyticsKeys.engagement(period),
    queryFn: () => analyticsApi.getEngagementMetrics(period),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 15 * 60 * 1000, // Refetch every 15 minutes
  });
}

// Combined analytics hook for dashboard
export function useDashboardAnalytics(period: 'day' | 'week' | 'month' | 'year' = 'month') {
  const dashboard = useAnalyticsDashboard();
  const usage = useUsageStats(period);
  const topThreads = useTopPerformingThreads(5);
  const content = useContentAnalysis();
  const engagement = useEngagementMetrics(period);

  return {
    dashboard,
    usage,
    topThreads,
    content,
    engagement,
    isLoading: dashboard.isLoading || usage.isLoading || topThreads.isLoading || content.isLoading || engagement.isLoading,
    isError: dashboard.isError || usage.isError || topThreads.isError || content.isError || engagement.isError,
    error: dashboard.error || usage.error || topThreads.error || content.error || engagement.error,
  };
}