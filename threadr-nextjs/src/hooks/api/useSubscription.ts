import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { 
  subscriptionsApi,
  SubscriptionStatus,
  PaymentMethod,
  BillingHistory,
  UsageDetails,
  CreateSubscriptionRequest,
  UpdateSubscriptionRequest,
  CreatePaymentIntentRequest
} from '@/lib/api/subscriptions';
import { paymentsApi, PremiumStatusResponse, UsageStatsResponse, CreateCheckoutSessionRequest } from '@/lib/api/payments';
import { SubscriptionPlan, PaymentIntent } from '@/types';

// Query keys for subscription-related data
export const subscriptionKeys = {
  all: ['subscriptions'] as const,
  plans: () => [...subscriptionKeys.all, 'plans'] as const,
  plan: (id: string) => [...subscriptionKeys.plans(), id] as const,
  current: () => [...subscriptionKeys.all, 'current'] as const,
  status: () => [...subscriptionKeys.all, 'status'] as const,
  paymentMethods: () => [...subscriptionKeys.all, 'payment-methods'] as const,
  billingHistory: (page: number, limit: number) => [...subscriptionKeys.all, 'billing-history', { page, limit }] as const,
  usage: () => [...subscriptionKeys.all, 'usage'] as const,
  premiumStatus: () => [...subscriptionKeys.all, 'premium-status'] as const,
  invoice: (id: string) => [...subscriptionKeys.all, 'invoice', id] as const,
} as const;

// Subscription Plans
export function useSubscriptionPlans() {
  return useQuery({
    queryKey: subscriptionKeys.plans(),
    queryFn: subscriptionsApi.getPlans,
    staleTime: 30 * 60 * 1000, // 30 minutes
    gcTime: 60 * 60 * 1000, // 1 hour
  });
}

export function useSubscriptionPlan(planId: string, enabled = true) {
  return useQuery({
    queryKey: subscriptionKeys.plan(planId),
    queryFn: () => subscriptionsApi.getPlan(planId),
    enabled: !!planId && enabled,
    staleTime: 30 * 60 * 1000,
  });
}

// Current Subscription
export function useCurrentSubscription() {
  return useQuery({
    queryKey: subscriptionKeys.current(),
    queryFn: subscriptionsApi.getCurrentSubscription,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: (failureCount, error: any) => {
      // Don't retry on 404 (no subscription)
      if (error?.status === 404) return false;
      return failureCount < 3;
    },
  });
}

// Premium Status (using real payment API)
export function usePremiumStatus() {
  return useQuery({
    queryKey: subscriptionKeys.premiumStatus(),
    queryFn: paymentsApi.getPremiumStatus,
    staleTime: 5 * 60 * 1000,
    refetchInterval: 10 * 60 * 1000, // Refetch every 10 minutes
  });
}

// Create Subscription
export function useCreateSubscription() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (request: CreateSubscriptionRequest) => 
      subscriptionsApi.createSubscription(request),
    onSuccess: (subscription: SubscriptionStatus) => {
      // Update subscription cache
      queryClient.setQueryData(subscriptionKeys.current(), subscription);
      
      // Invalidate premium status
      queryClient.invalidateQueries({ queryKey: subscriptionKeys.premiumStatus() });
      
      // Invalidate usage data
      queryClient.invalidateQueries({ queryKey: subscriptionKeys.usage() });
      
      // Invalidate user profile (premium status might change)
      queryClient.invalidateQueries({ queryKey: ['auth', 'profile'] });
    },
    onError: (error) => {
      console.error('Failed to create subscription:', error);
    },
  });
}

// Update Subscription
export function useUpdateSubscription() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (request: UpdateSubscriptionRequest) =>
      subscriptionsApi.updateSubscription(request),
    onSuccess: (subscription: SubscriptionStatus) => {
      // Update subscription cache
      queryClient.setQueryData(subscriptionKeys.current(), subscription);
      
      // Invalidate premium status
      queryClient.invalidateQueries({ queryKey: subscriptionKeys.premiumStatus() });
    },
  });
}

// Cancel Subscription
export function useCancelSubscription() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (immediate?: boolean) => subscriptionsApi.cancelSubscription(immediate ?? false),
    onSuccess: (subscription: SubscriptionStatus) => {
      // Update subscription cache
      queryClient.setQueryData(subscriptionKeys.current(), subscription);
      
      // Invalidate premium status
      queryClient.invalidateQueries({ queryKey: subscriptionKeys.premiumStatus() });
      
      // If immediate cancellation, update user profile
      if (subscription.status === 'canceled') {
        queryClient.invalidateQueries({ queryKey: ['auth', 'profile'] });
      }
    },
  });
}

// Reactivate Subscription
export function useReactivateSubscription() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: subscriptionsApi.reactivateSubscription,
    onSuccess: (subscription: SubscriptionStatus) => {
      // Update subscription cache
      queryClient.setQueryData(subscriptionKeys.current(), subscription);
      
      // Invalidate premium status
      queryClient.invalidateQueries({ queryKey: subscriptionKeys.premiumStatus() });
    },
  });
}

// Upgrade Plan
export function useUpgradePlan() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ planId, immediate = false }: { planId: string; immediate?: boolean }) =>
      subscriptionsApi.upgradePlan(planId, immediate),
    onSuccess: (subscription: SubscriptionStatus) => {
      queryClient.setQueryData(subscriptionKeys.current(), subscription);
      queryClient.invalidateQueries({ queryKey: subscriptionKeys.premiumStatus() });
      queryClient.invalidateQueries({ queryKey: subscriptionKeys.usage() });
    },
  });
}

// Downgrade Plan
export function useDowngradePlan() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (planId: string) => subscriptionsApi.downgradePlan(planId),
    onSuccess: (subscription: SubscriptionStatus) => {
      queryClient.setQueryData(subscriptionKeys.current(), subscription);
      queryClient.invalidateQueries({ queryKey: subscriptionKeys.premiumStatus() });
      queryClient.invalidateQueries({ queryKey: subscriptionKeys.usage() });
    },
  });
}

// Payment Methods
export function usePaymentMethods() {
  return useQuery({
    queryKey: subscriptionKeys.paymentMethods(),
    queryFn: subscriptionsApi.getPaymentMethods,
    staleTime: 5 * 60 * 1000,
  });
}

export function useAddPaymentMethod() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ paymentMethodId, makeDefault = false }: { paymentMethodId: string; makeDefault?: boolean }) =>
      subscriptionsApi.addPaymentMethod(paymentMethodId, makeDefault),
    onSuccess: () => {
      // Refetch payment methods
      queryClient.invalidateQueries({ queryKey: subscriptionKeys.paymentMethods() });
    },
  });
}

export function useRemovePaymentMethod() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (paymentMethodId: string) => subscriptionsApi.removePaymentMethod(paymentMethodId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: subscriptionKeys.paymentMethods() });
    },
  });
}

export function useSetDefaultPaymentMethod() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (paymentMethodId: string) => subscriptionsApi.setDefaultPaymentMethod(paymentMethodId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: subscriptionKeys.paymentMethods() });
    },
  });
}

// Payment Intents (for one-time payments)
export function useCreatePaymentIntent() {
  return useMutation({
    mutationFn: (request: CreatePaymentIntentRequest) => 
      subscriptionsApi.createPaymentIntent(request),
  });
}

// Billing History
export function useBillingHistory(page = 1, limit = 10) {
  return useQuery({
    queryKey: subscriptionKeys.billingHistory(page, limit),
    queryFn: () => subscriptionsApi.getBillingHistory(page, limit),
    staleTime: 5 * 60 * 1000,
  });
}

export function useInvoice(invoiceId: string, enabled = true) {
  return useQuery({
    queryKey: subscriptionKeys.invoice(invoiceId),
    queryFn: () => subscriptionsApi.getInvoice(invoiceId),
    enabled: !!invoiceId && enabled,
    staleTime: 10 * 60 * 1000,
  });
}

export function useDownloadInvoice() {
  return useMutation({
    mutationFn: (invoiceId: string) => subscriptionsApi.downloadInvoice(invoiceId),
    onSuccess: (blob: Blob, invoiceId: string) => {
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `invoice-${invoiceId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    },
  });
}

// Usage Details (using real payment API)
export function useUsageDetails() {
  return useQuery({
    queryKey: subscriptionKeys.usage(),
    queryFn: paymentsApi.getUsageStats,
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });
}

// Coupon Validation
export function useValidateCoupon() {
  return useMutation({
    mutationFn: ({ couponCode, planId }: { couponCode: string; planId?: string }) =>
      subscriptionsApi.validateCoupon(couponCode, planId),
  });
}

// Customer Portal
export function useCreatePortalSession() {
  return useMutation({
    mutationFn: (returnUrl?: string) => subscriptionsApi.createPortalSession(returnUrl),
    onSuccess: (data) => {
      // Redirect to Stripe Customer Portal
      window.location.href = data.url;
    },
  });
}

// Create Checkout Session and Redirect to Stripe
export function useCreateCheckoutSession() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (request: CreateCheckoutSessionRequest = {}) => 
      paymentsApi.createCheckoutSession(request),
    onSuccess: (data) => {
      // Track the payment attempt
      console.log('Redirecting to Stripe checkout:', data.session_id);
      
      // Redirect to Stripe checkout
      window.location.href = data.checkout_url;
    },
    onError: (error) => {
      console.error('Failed to create checkout session:', error);
    },
  });
}

// Quick upgrade hook (convenience method)
export function useUpgradeToPremium() {
  const createCheckout = useCreateCheckoutSession();
  
  return useMutation({
    mutationFn: (options: CreateCheckoutSessionRequest = {}) => {
      const defaultOptions = {
        success_url: `${window.location.origin}/payment/success`,
        cancel_url: `${window.location.origin}/payment/cancel`,
        ...options,
      };
      
      return createCheckout.mutateAsync(defaultOptions);
    },
    onError: (error) => {
      console.error('Failed to upgrade to premium:', error);
    },
  });
}

// Refresh Subscription Data
export function useRefreshSubscription() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: subscriptionsApi.refreshSubscriptionData,
    onSuccess: (subscription) => {
      // Update all subscription-related cache
      queryClient.setQueryData(subscriptionKeys.current(), subscription);
      queryClient.invalidateQueries({ queryKey: subscriptionKeys.premiumStatus() });
      queryClient.invalidateQueries({ queryKey: subscriptionKeys.usage() });
      queryClient.invalidateQueries({ queryKey: ['auth', 'profile'] });
    },
  });
}

// Combined hook for subscription overview
export function useSubscriptionOverview() {
  const subscription = useCurrentSubscription();
  const premiumStatus = usePremiumStatus();
  const usage = useUsageDetails();
  const plans = useSubscriptionPlans();

  return {
    subscription,
    premiumStatus,
    usage,
    plans,
    isLoading: subscription.isLoading || premiumStatus.isLoading || usage.isLoading || plans.isLoading,
    isError: subscription.isError || premiumStatus.isError || usage.isError || plans.isError,
    error: subscription.error || premiumStatus.error || usage.error || plans.error,
  };
}

// Utility hooks for common subscription states
export function useIsSubscribed() {
  const { data: subscription } = useCurrentSubscription();
  return subscription?.status === 'active' || subscription?.status === 'trialing';
}

export function useSubscriptionStatus() {
  const { data: subscription } = useCurrentSubscription();
  const { data: premiumStatus } = usePremiumStatus();
  
  return {
    isSubscribed: subscription?.status === 'active' || subscription?.status === 'trialing',
    isPremium: premiumStatus?.has_premium || false,
    isTrialing: subscription?.status === 'trialing',
    isCanceled: subscription?.cancelAtPeriodEnd || false,
    isPastDue: subscription?.status === 'past_due',
    plan: subscription?.plan,
    expiresAt: subscription?.currentPeriodEnd || premiumStatus?.expires_at,
    trialEndsAt: subscription?.trialEnd,
    needsPayment: premiumStatus?.needs_payment || false,
    premiumPrice: premiumStatus?.premium_price || 4.99,
  };
}

// Hook for checking feature access
export function useFeatureAccess() {
  const { data: usage } = useUsageDetails();
  const { isPremium } = useSubscriptionStatus();
  
  const hasUnlimitedAccess = isPremium;
  
  return {
    canCreateThreads: hasUnlimitedAccess || (usage && usage.daily_remaining > 0 && usage.monthly_remaining > 0),
    canUseTemplates: hasUnlimitedAccess,
    canAccessPremiumFeatures: hasUnlimitedAccess,
    remainingThreadsDaily: usage?.daily_remaining || 0,
    remainingThreadsMonthly: usage?.monthly_remaining || 0,
    dailyUsage: usage?.daily_usage || 0,
    monthlyUsage: usage?.monthly_usage || 0,
    dailyLimit: usage?.daily_limit || 5,
    monthlyLimit: usage?.monthly_limit || 20,
    usage,
    hasUnlimitedAccess,
  };
}