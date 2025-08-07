import { apiClient } from './client';
import { 
  SubscriptionPlan, 
  PaymentIntent,
  User,
  ApiResponse 
} from '@/types';

// Subscription API types
export interface SubscriptionStatus {
  id: string;
  userId: string;
  planId: string;
  status: 'active' | 'canceled' | 'past_due' | 'trialing' | 'incomplete';
  currentPeriodStart: string;
  currentPeriodEnd: string;
  cancelAtPeriodEnd: boolean;
  trialStart?: string;
  trialEnd?: string;
  createdAt: string;
  updatedAt: string;
  plan: SubscriptionPlan;
}

export interface PaymentMethod {
  id: string;
  type: 'card';
  card: {
    brand: string;
    last4: string;
    expMonth: number;
    expYear: number;
  };
  isDefault: boolean;
  createdAt: string;
}

export interface Invoice {
  id: string;
  subscriptionId: string;
  amount: number;
  currency: string;
  status: 'paid' | 'pending' | 'failed';
  periodStart: string;
  periodEnd: string;
  paidAt?: string;
  dueDate: string;
  downloadUrl?: string;
  createdAt: string;
}

export interface BillingHistory {
  invoices: Invoice[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface UsageDetails {
  currentPeriodUsage: {
    threads: number;
    templates: number;
    apiCalls: number;
  };
  limits: {
    threads: number | null; // null = unlimited
    templates: number | null;
    apiCalls: number | null;
  };
  resetDate: string;
}

export interface CreateSubscriptionRequest {
  planId: string;
  paymentMethodId?: string;
  couponCode?: string;
  trialDays?: number;
}

export interface UpdateSubscriptionRequest {
  planId?: string;
  cancelAtPeriodEnd?: boolean;
  couponCode?: string;
}

export interface CreatePaymentIntentRequest {
  planId: string;
  couponCode?: string;
  paymentMethodId?: string;
}

// Subscription API class
class SubscriptionsApi {
  // Subscription Plans
  async getPlans(): Promise<SubscriptionPlan[]> {
    return apiClient.get('/subscriptions/plans');
  }

  async getPlan(planId: string): Promise<SubscriptionPlan> {
    return apiClient.get(`/subscriptions/plans/${planId}`);
  }

  // Current Subscription
  async getCurrentSubscription(): Promise<SubscriptionStatus | null> {
    try {
      return await apiClient.get('/subscriptions/current');
    } catch (error: any) {
      // Return null if no active subscription (404)
      if (error.status === 404) {
        return null;
      }
      throw error;
    }
  }

  async createSubscription(request: CreateSubscriptionRequest): Promise<SubscriptionStatus> {
    return apiClient.post('/subscriptions', request);
  }

  async updateSubscription(request: UpdateSubscriptionRequest): Promise<SubscriptionStatus> {
    return apiClient.put('/subscriptions/current', request);
  }

  async cancelSubscription(immediate = false): Promise<SubscriptionStatus> {
    return apiClient.post('/subscriptions/current/cancel', { immediate });
  }

  async reactivateSubscription(): Promise<SubscriptionStatus> {
    return apiClient.post('/subscriptions/current/reactivate');
  }

  // Payment Methods
  async getPaymentMethods(): Promise<PaymentMethod[]> {
    return apiClient.get('/subscriptions/payment-methods');
  }

  async addPaymentMethod(paymentMethodId: string, makeDefault = false): Promise<PaymentMethod> {
    return apiClient.post('/subscriptions/payment-methods', {
      paymentMethodId,
      makeDefault,
    });
  }

  async removePaymentMethod(paymentMethodId: string): Promise<void> {
    return apiClient.delete(`/subscriptions/payment-methods/${paymentMethodId}`);
  }

  async setDefaultPaymentMethod(paymentMethodId: string): Promise<PaymentMethod> {
    return apiClient.put(`/subscriptions/payment-methods/${paymentMethodId}/default`);
  }

  // Payment Intents (for one-time payments)
  async createPaymentIntent(request: CreatePaymentIntentRequest): Promise<PaymentIntent> {
    return apiClient.post('/subscriptions/payment-intents', request);
  }

  // Billing & Invoices
  async getBillingHistory(page = 1, limit = 10): Promise<BillingHistory> {
    return apiClient.get('/subscriptions/billing-history', {
      params: { page, limit },
    });
  }

  async getInvoice(invoiceId: string): Promise<Invoice> {
    return apiClient.get(`/subscriptions/invoices/${invoiceId}`);
  }

  async downloadInvoice(invoiceId: string): Promise<Blob> {
    const response = await apiClient.getRaw(`/subscriptions/invoices/${invoiceId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  }

  // Usage Tracking
  async getUsageDetails(): Promise<UsageDetails> {
    return apiClient.get('/subscriptions/usage');
  }

  // Coupons & Discounts
  async validateCoupon(couponCode: string, planId?: string): Promise<{
    valid: boolean;
    discount: {
      type: 'percent' | 'amount';
      value: number;
      currency?: string;
    } | null;
    expiresAt?: string;
  }> {
    return apiClient.post('/subscriptions/coupons/validate', {
      couponCode,
      planId,
    });
  }

  // Premium Status (for backward compatibility with existing system)
  async getPremiumStatus(): Promise<{
    isPremium: boolean;
    expiresAt?: string;
    plan?: SubscriptionPlan;
    trialEndsAt?: string;
    subscription?: SubscriptionStatus;
  }> {
    return apiClient.get('/subscriptions/premium-status');
  }

  // Subscription Management
  async upgradePlan(planId: string, immediate = false): Promise<SubscriptionStatus> {
    return apiClient.post('/subscriptions/current/upgrade', {
      planId,
      immediate,
    });
  }

  async downgradePlan(planId: string): Promise<SubscriptionStatus> {
    return apiClient.post('/subscriptions/current/downgrade', {
      planId,
    });
  }

  // Portal Session (Stripe Customer Portal)
  async createPortalSession(returnUrl?: string): Promise<{ url: string }> {
    return apiClient.post('/subscriptions/portal-session', {
      returnUrl: returnUrl || window.location.href,
    });
  }

  // Webhooks (for internal use, testing)
  async refreshSubscriptionData(): Promise<SubscriptionStatus | null> {
    return apiClient.post('/subscriptions/refresh');
  }
}

export const subscriptionsApi = new SubscriptionsApi();
export default subscriptionsApi;

// Types are exported from @/types and @/types/api