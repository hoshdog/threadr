import { useState, useCallback, useEffect } from 'react';
import { UsageStatus, PremiumCheckResponse } from '@/types/api';
import { API_CONFIG } from '../config';

interface UseUsageStatsReturn {
  usageStatus: UsageStatus | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  canGenerate: boolean;
  needsUpgrade: boolean;
  premium: {
    hasAccess: boolean;
    expiresAt: string | null;
  };
}

export function useUsageStats(): UseUsageStatsReturn {
  const [usageStatus, setUsageStatus] = useState<UsageStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getAuthHeaders = useCallback(() => {
    const token = localStorage.getItem('threadr_token');
    return {
      ...API_CONFIG.HEADERS,
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }, []);

  const fetchUsageStats = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.UTILITY.USAGE_STATS}`, {
        method: 'GET',
        headers: getAuthHeaders(),
        mode: 'cors',
        credentials: 'omit',
      });

      if (!response.ok) {
        if (response.status === 401) {
          setError('Please log in to view usage statistics');
        } else {
          setError('Failed to load usage statistics');
        }
        return;
      }

      const data: UsageStatus = await response.json();
      setUsageStatus(data);
    } catch (error) {
      console.error('Failed to fetch usage stats:', error);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [getAuthHeaders]);

  const checkPremiumStatus = useCallback(async () => {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.UTILITY.PREMIUM_STATUS}`, {
        method: 'GET',
        headers: getAuthHeaders(),
        mode: 'cors',
        credentials: 'omit',
      });

      if (response.ok) {
        const data: PremiumCheckResponse = await response.json();
        setUsageStatus(data.usage_status);
      }
    } catch (error) {
      console.error('Failed to check premium status:', error);
    }
  }, [getAuthHeaders]);

  // Auto-fetch on mount and when auth changes
  useEffect(() => {
    const token = localStorage.getItem('threadr_token');
    if (token) {
      fetchUsageStats();
    }
  }, [fetchUsageStats]);

  // Computed values
  const canGenerate = usageStatus 
    ? (usageStatus.has_premium || 
       usageStatus.daily_usage < usageStatus.daily_limit ||
       usageStatus.monthly_usage < usageStatus.monthly_limit)
    : true; // Default to true if no usage data

  const needsUpgrade = usageStatus 
    ? (!usageStatus.has_premium && 
       usageStatus.daily_usage >= usageStatus.daily_limit &&
       usageStatus.monthly_usage >= usageStatus.monthly_limit)
    : false;

  const premium = {
    hasAccess: usageStatus?.has_premium || false,
    expiresAt: usageStatus?.premium_expires_at || null,
  };

  return {
    usageStatus,
    loading,
    error,
    refetch: fetchUsageStats,
    canGenerate,
    needsUpgrade,
    premium,
  };
}