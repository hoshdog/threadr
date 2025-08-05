import { apiClient } from './client';
import { AnalyticsDashboard } from '@/types';

export const analyticsApi = {
  async getDashboard(period: 'day' | 'week' | 'month' | 'year' = 'month'): Promise<AnalyticsDashboard> {
    return apiClient.get<AnalyticsDashboard>(`/analytics/dashboard?period=${period}`);
  },

  async getUsageStats(period: 'day' | 'week' | 'month' | 'year' = 'month'): Promise<{
    usage: Array<{ date: string; count: number }>;
    total: number;
    period: string;
  }> {
    return apiClient.get(`/analytics/usage?period=${period}`);
  },

  async getThreadStats(threadId: string): Promise<{
    views: number;
    shares: number;
    engagement: number;
    performanceScore: number;
  }> {
    return apiClient.get(`/analytics/threads/${threadId}/stats`);
  },

  async getTopPerformingThreads(
    limit = 10, 
    period: 'day' | 'week' | 'month' | 'year' = 'month',
    sortBy: 'engagement' | 'views' | 'clicks' | 'shares' = 'engagement'
  ): Promise<Array<{
    threadId: string;
    title: string;
    score: number;
    views: number;
    shares: number;
  }>> {
    return apiClient.get(`/analytics/threads/top?limit=${limit}&period=${period}&sortBy=${sortBy}`);
  },

  async getContentAnalysis(period: 'day' | 'week' | 'month' | 'year' = 'month'): Promise<{
    averageThreadLength: number;
    mostUsedWords: Array<{ word: string; count: number }>;
    sentimentAnalysis: {
      positive: number;
      neutral: number;
      negative: number;
    };
    popularTopics: Array<{ topic: string; count: number }>;
  }> {
    return apiClient.get(`/analytics/content?period=${period}`);
  },

  async getEngagementMetrics(period: 'day' | 'week' | 'month' | 'year' = 'month'): Promise<{
    clickThroughRate: number;
    avgTimeSpent: number;
    bounceRate: number;
    conversionRate: number;
  }> {
    return apiClient.get(`/analytics/engagement?period=${period}`);
  },

  // Performance metrics
  async getPerformanceMetrics(period: 'day' | 'week' | 'month' | 'year' = 'month'): Promise<{
    responseTime: number;
    successRate: number;
    errorRate: number;
    mostUsedFeatures: Array<{ feature: string; usage: number; percentage: number }>;
    peakUsageHours: Array<{ hour: number; usage: number }>;
  }> {
    return apiClient.get(`/analytics/performance?period=${period}`);
  },

  // Revenue analytics
  async getRevenueAnalytics(period: 'day' | 'week' | 'month' | 'year' = 'month'): Promise<{
    totalRevenue: number;
    mrr: number;
    arr: number;
    conversionRate: number;
    averageRevenuePerUser: number;
    churnRate: number;
    customerLifetimeValue: number;
    revenueByPlan: Array<{ planName: string; revenue: number; subscribers: number }>;
  }> {
    return apiClient.get(`/analytics/revenue?period=${period}`);
  },

  // User behavior analytics
  async getUserBehaviorAnalytics(period: 'day' | 'week' | 'month' | 'year' = 'month'): Promise<{
    sessionDuration: number;
    pagesPerSession: number;
    featureAdoptionRate: Record<string, number>;
    userJourney: Array<{ step: string; completionRate: number; dropOffRate: number }>;
    retentionRate: { day1: number; day7: number; day30: number };
  }> {
    return apiClient.get(`/analytics/user-behavior?period=${period}`);
  },

  // Real-time analytics
  async getRealtimeAnalytics(): Promise<{
    activeUsers: number;
    threadsBeingGenerated: number;
    currentLoad: number;
    recentActivity: Array<{ timestamp: string; action: string; count: number }>;
  }> {
    return apiClient.get('/analytics/realtime');
  },

  // Goals and KPIs
  async getAnalyticsGoals(): Promise<Record<string, { target: number; current: number; progress: number }>> {
    return apiClient.get('/analytics/goals');
  },

  async setAnalyticsGoals(goals: Record<string, number>): Promise<{ success: boolean }> {
    return apiClient.post('/analytics/goals', { goals });
  },

  // Alerts
  async getAnalyticsAlerts(): Promise<Array<{
    id: string;
    metric: string;
    condition: 'above' | 'below' | 'equals';
    threshold: number;
    frequency: 'immediate' | 'daily' | 'weekly';
    isActive: boolean;
    createdAt: string;
  }>> {
    return apiClient.get('/analytics/alerts');
  },

  async createAnalyticsAlert(alert: {
    metric: string;
    condition: 'above' | 'below' | 'equals';
    threshold: number;
    frequency: 'immediate' | 'daily' | 'weekly';
  }): Promise<{ id: string }> {
    return apiClient.post('/analytics/alerts', alert);
  },

  async deleteAnalyticsAlert(alertId: string): Promise<{ success: boolean }> {
    return apiClient.delete(`/analytics/alerts/${alertId}`);
  },

  // Export functionality
  async exportAnalytics(params: {
    type: 'usage' | 'engagement' | 'revenue' | 'content';
    period: 'day' | 'week' | 'month' | 'year';
    format: 'csv' | 'json' | 'pdf';
    dateRange?: { start: string; end: string };
  }): Promise<Blob> {
    const response = await apiClient.postRaw('/analytics/export', params, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Event tracking
  async trackEvent(event: {
    name: string;
    properties?: Record<string, any>;
    userId?: string;
    timestamp?: string;
  }): Promise<{ success: boolean }> {
    return apiClient.post('/analytics/events', event);
  },

  // Insights and recommendations
  async getAnalyticsInsights(period: 'day' | 'week' | 'month' | 'year' = 'month'): Promise<{
    insights: Array<{
      type: 'improvement' | 'warning' | 'success';
      title: string;
      description: string;
      actionable: boolean;
      priority: 'high' | 'medium' | 'low';
    }>;
    recommendations: Array<{
      title: string;
      description: string;
      impact: 'high' | 'medium' | 'low';
      effort: 'high' | 'medium' | 'low';
    }>;
  }> {
    return apiClient.get(`/analytics/insights?period=${period}`);
  },

  // A/B testing
  async getABTestResults(testId: string): Promise<{
    testId: string;
    name: string;
    status: 'running' | 'completed' | 'paused';
    variants: Array<{
      name: string;
      traffic: number;
      conversions: number;
      conversionRate: number;
      significance: number;
    }>;
    winner?: string;
    confidence: number;
  }> {
    return apiClient.get(`/analytics/ab-tests/${testId}`);
  },

  // Custom analytics queries
  async getCustomAnalytics(query: {
    metrics: string[];
    dimensions: string[];
    filters?: Record<string, any>;
    dateRange: { start: string; end: string };
  }): Promise<{
    data: Array<Record<string, any>>;
    totals: Record<string, number>;
    metadata: {
      dateRange: { start: string; end: string };
      totalRows: number;
    };
  }> {
    return apiClient.post('/analytics/custom', query);
  },

  // Health check
  async getAnalyticsHealth(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    services: Record<string, { status: 'up' | 'down'; responseTime: number }>;
    lastUpdated: string;
  }> {
    return apiClient.get('/analytics/health');
  },
};