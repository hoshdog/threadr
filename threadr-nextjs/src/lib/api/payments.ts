import { apiClient } from './client';

// Payment API types
export interface CreateCheckoutSessionRequest {
  success_url?: string;
  cancel_url?: string;
  customer_email?: string;
  plan_id?: string;
  billing_frequency?: 'monthly' | 'annual';
  price_id?: string;
}

export interface CreateCheckoutSessionResponse {
  checkout_url: string;
  session_id: string;
}

export interface PremiumStatusResponse {
  has_premium: boolean;
  expires_at?: string;
  usage_status: {
    daily_usage: number;
    daily_limit: number;
    daily_remaining: number;
    monthly_usage: number;
    monthly_limit: number;
    monthly_remaining: number;
    has_premium: boolean;
    premium_expires_at?: string;
  };
  needs_payment: boolean;
  premium_price: number;
  message: string;
}

export interface UsageStatsResponse {
  daily_usage: number;
  daily_limit: number;
  daily_remaining: number;
  monthly_usage: number;
  monthly_limit: number;
  monthly_remaining: number;
  has_premium: boolean;
  premium_expires_at?: string;
  free_tier_enabled: boolean;
}

// Payment API class
class PaymentsApi {
  /**
   * Create a Stripe checkout session for premium upgrade
   */
  async createCheckoutSession(request: CreateCheckoutSessionRequest = {}): Promise<CreateCheckoutSessionResponse> {
    const defaultRequest = {
      success_url: `${window.location.origin}/payment/success`,
      cancel_url: `${window.location.origin}/payment/cancel`,
      ...request,
    };

    return apiClient.post('/api/stripe/create-checkout-session', defaultRequest);
  }

  /**
   * Check premium status and usage limits
   */
  async getPremiumStatus(): Promise<PremiumStatusResponse> {
    return apiClient.get('/api/premium-status');
  }

  /**
   * Get current usage statistics
   */
  async getUsageStats(): Promise<UsageStatsResponse> {
    return apiClient.get('/api/usage-stats');
  }

  /**
   * Redirect to Stripe checkout
   */
  async redirectToCheckout(options: CreateCheckoutSessionRequest = {}): Promise<void> {
    try {
      const { checkout_url } = await this.createCheckoutSession(options);
      
      // Redirect to Stripe checkout
      window.location.href = checkout_url;
    } catch (error) {
      console.error('Failed to redirect to checkout:', error);
      throw error;
    }
  }

  /**
   * Check if user needs to upgrade (convenience method)
   */
  async needsUpgrade(): Promise<boolean> {
    try {
      const status = await this.getPremiumStatus();
      return status.needs_payment;
    } catch (error) {
      console.error('Failed to check upgrade status:', error);
      return false;
    }
  }

  /**
   * Get remaining usage for display
   */
  async getRemainingUsage(): Promise<{
    daily_remaining: number;
    monthly_remaining: number;
    has_premium: boolean;
  }> {
    try {
      const stats = await this.getUsageStats();
      return {
        daily_remaining: stats.daily_remaining,
        monthly_remaining: stats.monthly_remaining,
        has_premium: stats.has_premium,
      };
    } catch (error) {
      console.error('Failed to get remaining usage:', error);
      return {
        daily_remaining: 0,
        monthly_remaining: 0,
        has_premium: false,
      };
    }
  }
}

export const paymentsApi = new PaymentsApi();
export default paymentsApi;

// Hook for easy usage in components
export const usePayments = () => {
  return {
    createCheckoutSession: paymentsApi.createCheckoutSession.bind(paymentsApi),
    getPremiumStatus: paymentsApi.getPremiumStatus.bind(paymentsApi),
    getUsageStats: paymentsApi.getUsageStats.bind(paymentsApi),
    redirectToCheckout: paymentsApi.redirectToCheckout.bind(paymentsApi),
    needsUpgrade: paymentsApi.needsUpgrade.bind(paymentsApi),
    getRemainingUsage: paymentsApi.getRemainingUsage.bind(paymentsApi),
  };
};