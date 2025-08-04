import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { analyticsApi } from '@/lib/api/analytics';
import { AnalyticsDashboard } from '@/types';

// Additional types for analytics
export interface UsageMetrics {
  period: 'day' | 'week' | 'month' | 'year';
  threadsCreated: number;
  templatesUsed: number;
  apiCalls: number;
  averageThreadLength: number;
  totalCharacters: number;
  uniqueDomains: number;
  timestamp: string;
}

export interface PerformanceMetrics {
  responseTime: number;
  successRate: number;
  errorRate: number;
  mostUsedFeatures: Array<{
    feature: string;
    usage: number;
    percentage: number;
  }>;
  peakUsageHours: Array<{
    hour: number;
    usage: number;
  }>;
}

export interface ContentAnalysis {
  popularTopics: Array<{
    topic: string;
    count: number;
    trend: 'up' | 'down' | 'stable';
  }>;
  averageEngagement: number;
  bestPerformingLength: {
    min: number;
    max: number;
    average: number;
  };
  contentSources: Array<{
    domain: string;
    count: number;
    successRate: number;
  }>;
}

export interface EngagementData {
  totalViews: number;
  totalClicks: number;
  clickThroughRate: number;
  avgTimeSpent: number;
  bounceRate: number;
  conversionRate: number;
  topPerformingThreads: Array<{
    id: string;
    title: string;
    engagement: number;
    createdAt: string;
  }>;
}

export interface RevenueAnalytics {
  totalRevenue: number;
  mrr: number; // Monthly Recurring Revenue
  arr: number; // Annual Recurring Revenue
  conversionRate: number;
  averageRevenuePerUser: number;
  churnRate: number;
  customerLifetimeValue: number;
  revenueByPlan: Array<{
    planName: string;
    revenue: number;
    subscribers: number;
  }>;
}

export interface UserBehaviorAnalytics {
  sessionDuration: number;
  pagesPerSession: number;
  featureAdoptionRate: Record<string, number>;
  userJourney: Array<{
    step: string;
    completionRate: number;
    dropOffRate: number;
  }>;
  retentionRate: {
    day1: number;
    day7: number;
    day30: number;
  };
}

// Query keys for analytics data
export const analyticsKeys = {
  all: ['analytics'] as const,
  dashboard: () => [...analyticsKeys.all, 'dashboard'] as const,
  usage: (period: string) => [...analyticsKeys.all, 'usage', period] as const,
  performance: (period: string) => [...analyticsKeys.all, 'performance', period] as const,
  threadStats: (threadId: string) => [...analyticsKeys.all, 'thread-stats', threadId] as const,
  topThreads: (limit: number, period: string) => [...analyticsKeys.all, 'top-threads', limit, period] as const,
  content: (period: string) => [...analyticsKeys.all, 'content', period] as const,
  engagement: (period: string) => [...analyticsKeys.all, 'engagement', period] as const,
  revenue: (period: string) => [...analyticsKeys.all, 'revenue', period] as const,
  userBehavior: (period: string) => [...analyticsKeys.all, 'user-behavior', period] as const,
  exports: () => [...analyticsKeys.all, 'exports'] as const,
  realtime: () => [...analyticsKeys.all, 'realtime'] as const,
  goals: () => [...analyticsKeys.all, 'goals'] as const,
  alerts: () => [...analyticsKeys.all, 'alerts'] as const,
} as const;

// Get comprehensive analytics dashboard
export function useAnalyticsDashboard(period: 'day' | 'week' | 'month' | 'year' = 'month') {
  return useQuery({
    queryKey: analyticsKeys.dashboard(),
    queryFn: () => analyticsApi.getDashboard(period),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 10 * 60 * 1000, // Refetch every 10 minutes
    retry: 3,
  });
}

// Get detailed usage statistics with historical data
export function useUsageStats(period: 'day' | 'week' | 'month' | 'year' = 'month') {
  return useQuery({
    queryKey: analyticsKeys.usage(period),
    queryFn: () => analyticsApi.getUsageStats(period),
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
    retry: 3,
  });
}

// Get performance metrics
export function usePerformanceMetrics(period: 'day' | 'week' | 'month' | 'year' = 'month') {
  return useQuery({
    queryKey: analyticsKeys.performance(period),
    queryFn: () => analyticsApi.getPerformanceMetrics(period),
    staleTime: 5 * 60 * 1000,
    refetchInterval: 15 * 60 * 1000, // Refetch every 15 minutes
  });
}

// Get thread-specific analytics
export function useThreadStats(threadId: string, enabled = true) {
  return useQuery({
    queryKey: analyticsKeys.threadStats(threadId),
    queryFn: () => analyticsApi.getThreadStats(threadId),
    enabled: !!threadId && enabled,
    staleTime: 5 * 60 * 1000,
    refetchInterval: 15 * 60 * 1000, // Refetch every 15 minutes
    retry: (failureCount, error: any) => {
      // Don't retry on 404 (thread not found)
      if (error?.status === 404) return false;
      return failureCount < 3;
    },
  });
}

// Get top performing threads with advanced filtering
export function useTopPerformingThreads(
  limit = 10, 
  period: 'day' | 'week' | 'month' | 'year' = 'month',
  sortBy: 'engagement' | 'views' | 'clicks' | 'shares' = 'engagement'
) {
  return useQuery({
    queryKey: analyticsKeys.topThreads(limit, `${period}-${sortBy}`),
    queryFn: () => analyticsApi.getTopPerformingThreads(limit, period, sortBy),
    staleTime: 10 * 60 * 1000, // 10 minutes
    refetchInterval: 30 * 60 * 1000, // Refetch every 30 minutes
  });
}

// Get content analysis insights
export function useContentAnalysis(period: 'day' | 'week' | 'month' | 'year' = 'month') {
  return useQuery({
    queryKey: analyticsKeys.content(period),
    queryFn: () => analyticsApi.getContentAnalysis(period),
    staleTime: 15 * 60 * 1000, // 15 minutes
    refetchInterval: 60 * 60 * 1000, // Refetch every hour
  });
}

// Get engagement metrics with detailed breakdowns
export function useEngagementMetrics(period: 'day' | 'week' | 'month' | 'year' = 'month') {
  return useQuery({
    queryKey: analyticsKeys.engagement(period),
    queryFn: () => analyticsApi.getEngagementMetrics(period),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 15 * 60 * 1000, // Refetch every 15 minutes
  });
}

// Get revenue analytics (premium feature)
export function useRevenueAnalytics(period: 'day' | 'week' | 'month' | 'year' = 'month') {
  return useQuery({
    queryKey: analyticsKeys.revenue(period),
    queryFn: () => analyticsApi.getRevenueAnalytics(period),
    staleTime: 10 * 60 * 1000, // 10 minutes
    refetchInterval: 30 * 60 * 1000, // Refetch every 30 minutes
    retry: (failureCount, error: any) => {
      // Don't retry on 403 (not authorized for revenue data)
      if (error?.status === 403) return false;
      return failureCount < 3;
    },
  });
}

// Get user behavior analytics
export function useUserBehaviorAnalytics(period: 'day' | 'week' | 'month' | 'year' = 'month') {
  return useQuery({
    queryKey: analyticsKeys.userBehavior(period),
    queryFn: () => analyticsApi.getUserBehaviorAnalytics(period),
    staleTime: 15 * 60 * 1000, // 15 minutes
    refetchInterval: 60 * 60 * 1000, // Refetch every hour
  });
}

// Get real-time analytics
export function useRealtimeAnalytics() {
  return useQuery({
    queryKey: analyticsKeys.realtime(),
    queryFn: analyticsApi.getRealtimeAnalytics,
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Refetch every minute
    retry: 2,
  });
}

// Get analytics goals and KPIs
export function useAnalyticsGoals() {
  return useQuery({
    queryKey: analyticsKeys.goals(),
    queryFn: analyticsApi.getAnalyticsGoals,
    staleTime: 30 * 60 * 1000, // 30 minutes
    refetchInterval: 60 * 60 * 1000, // Refetch every hour
  });
}

// Set analytics goals
export function useSetAnalyticsGoals() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (goals: Record<string, number>) => analyticsApi.setAnalyticsGoals(goals),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: analyticsKeys.goals() });
      queryClient.invalidateQueries({ queryKey: analyticsKeys.dashboard() });
    },
    onError: (error) => {
      console.error('Failed to set analytics goals:', error);
    },
  });
}

// Get analytics alerts
export function useAnalyticsAlerts() {
  return useQuery({
    queryKey: analyticsKeys.alerts(),
    queryFn: analyticsApi.getAnalyticsAlerts,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 10 * 60 * 1000, // Refetch every 10 minutes
  });
}

// Create analytics alert
export function useCreateAnalyticsAlert() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (alert: {
      metric: string;
      condition: 'above' | 'below' | 'equals';
      threshold: number;
      frequency: 'immediate' | 'daily' | 'weekly';
    }) => analyticsApi.createAnalyticsAlert(alert),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: analyticsKeys.alerts() });
    },
    onError: (error) => {
      console.error('Failed to create analytics alert:', error);
    },
  });
}

// Delete analytics alert
export function useDeleteAnalyticsAlert() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (alertId: string) => analyticsApi.deleteAnalyticsAlert(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: analyticsKeys.alerts() });
    },
    onError: (error) => {
      console.error('Failed to delete analytics alert:', error);
    },
  });
}

// Export analytics data
export function useExportAnalytics() {
  return useMutation({
    mutationFn: (params: {
      type: 'usage' | 'engagement' | 'revenue' | 'content';
      period: 'day' | 'week' | 'month' | 'year';
      format: 'csv' | 'json' | 'pdf';
      dateRange?: { start: string; end: string };
    }) => analyticsApi.exportAnalytics(params),
    onSuccess: (blob, params) => {
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `analytics-${params.type}-${params.period}.${params.format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    },
    onError: (error) => {
      console.error('Analytics export failed:', error);
    },
  });
}

// Track custom events
export function useTrackEvent() {
  return useMutation({
    mutationFn: (event: {
      name: string;
      properties?: Record<string, any>;
      userId?: string;
      timestamp?: string;
    }) => analyticsApi.trackEvent(event),
    onError: (error) => {
      console.error('Event tracking failed:', error);
    },
  });
}

// Combined analytics hook for comprehensive dashboard
export function useDashboardAnalytics(period: 'day' | 'week' | 'month' | 'year' = 'month') {
  const dashboard = useAnalyticsDashboard(period);
  const usage = useUsageStats(period);
  const performance = usePerformanceMetrics(period);
  const topThreads = useTopPerformingThreads(5, period);
  const content = useContentAnalysis(period);
  const engagement = useEngagementMetrics(period);
  const realtime = useRealtimeAnalytics();
  const goals = useAnalyticsGoals();
  const alerts = useAnalyticsAlerts();

  return {
    dashboard,
    usage,
    performance,
    topThreads,
    content,
    engagement,
    realtime,
    goals,
    alerts,
    isLoading: dashboard.isLoading || usage.isLoading || performance.isLoading || 
               topThreads.isLoading || content.isLoading || engagement.isLoading,
    isError: dashboard.isError || usage.isError || performance.isError || 
             topThreads.isError || content.isError || engagement.isError,
    error: dashboard.error || usage.error || performance.error || 
           topThreads.error || content.error || engagement.error,
  };
}

// Hook for comparing periods
export function useCompareAnalytics(
  currentPeriod: 'day' | 'week' | 'month' | 'year' = 'month',
  comparisonPeriod: 'day' | 'week' | 'month' | 'year' = 'month'
) {
  const current = useUsageStats(currentPeriod);
  const comparison = useUsageStats(comparisonPeriod);
  
  return {
    current,
    comparison,
    isLoading: current.isLoading || comparison.isLoading,
    isError: current.isError || comparison.isError,
    error: current.error || comparison.error,
    improvement: current.data && comparison.data ? {
      // TODO: Fix analytics improvement calculations based on actual data structure
      threadsCreated: 0,
      engagement: 0,
    } : null,
  };
}

// Hook for analytics insights and recommendations
export function useAnalyticsInsights(period: 'day' | 'week' | 'month' | 'year' = 'month') {
  return useQuery({
    queryKey: [...analyticsKeys.all, 'insights', period],
    queryFn: () => analyticsApi.getAnalyticsInsights(period),
    staleTime: 30 * 60 * 1000, // 30 minutes
    refetchInterval: 2 * 60 * 60 * 1000, // Refetch every 2 hours
  });
}

// Hook for A/B testing analytics
export function useABTestAnalytics(testId: string, enabled = true) {
  return useQuery({
    queryKey: [...analyticsKeys.all, 'ab-test', testId],
    queryFn: () => analyticsApi.getABTestResults(testId),
    enabled: !!testId && enabled,
    staleTime: 10 * 60 * 1000, // 10 minutes
    refetchInterval: 30 * 60 * 1000, // Refetch every 30 minutes
  });
}

// Hook for custom analytics queries
export function useCustomAnalytics(query: {
  metrics: string[];
  dimensions: string[];
  filters?: Record<string, any>;
  dateRange: { start: string; end: string };
}) {
  return useQuery({
    queryKey: [...analyticsKeys.all, 'custom', JSON.stringify(query)],
    queryFn: () => analyticsApi.getCustomAnalytics(query),
    enabled: query.metrics.length > 0 && query.dimensions.length > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
}

// Hook for analytics health checks
export function useAnalyticsHealth() {
  return useQuery({
    queryKey: [...analyticsKeys.all, 'health'],
    queryFn: analyticsApi.getAnalyticsHealth,
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
    retry: 1,
  });
}