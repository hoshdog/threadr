'use client';

import { useState } from 'react';
import PricingCard, { PricingTier } from './PricingCard';
import { useSubscriptionPlans, useSubscriptionStatus } from '@/hooks/api/useSubscription';
import { Button } from '@/components/ui/Button';

interface PricingSectionProps {
  showHeader?: boolean;
  showBillingToggle?: boolean;
  currentTier?: string;
  onTierSelect?: (tierId: string) => void;
  showUpgradeButtons?: boolean;
}

export default function PricingSection({
  showHeader = true,
  showBillingToggle = true,
  currentTier,
  onTierSelect,
  showUpgradeButtons = true
}: PricingSectionProps) {
  const [billingFrequency, setBillingFrequency] = useState<'monthly' | 'annual'>('monthly');
  const { data: plansData, isLoading, error } = useSubscriptionPlans();
  const { plan: currentPlan } = useSubscriptionStatus();

  // Mock data matching the backend pricing config structure
  const mockPlans: PricingTier[] = [
    {
      id: 'free',
      name: 'Free',
      display_name: 'Free',
      monthly_price: 0,
      annual_price: 0,
      thread_limit: 5,
      daily_limit: 5,
      monthly_limit: 20,
      features: ['basic_threads'],
      description: 'Perfect for trying out Threadr',
    },
    {
      id: 'threadr_starter',
      name: 'Threadr Starter',
      display_name: 'Starter',
      monthly_price: 999, // $9.99
      annual_price: 9590, // $95.90 (20% discount)
      thread_limit: 100,
      daily_limit: -1,
      monthly_limit: 100,
      features: ['basic_threads', 'basic_analytics', 'email_support', 'premium_templates'],
      description: 'Great for individuals and small creators',
    },
    {
      id: 'threadr_pro',
      name: 'Threadr Pro',
      display_name: 'Pro',
      monthly_price: 1999, // $19.99
      annual_price: 19190, // $191.90 (20% discount)
      thread_limit: -1,
      daily_limit: -1,
      monthly_limit: -1,
      features: [
        'unlimited_threads',
        'advanced_analytics',
        'premium_templates',
        'priority_support',
        'custom_scheduling',
        'export_threads'
      ],
      description: 'Perfect for content creators and marketers',
      popular: true,
    },
    {
      id: 'threadr_team',
      name: 'Threadr Team',
      display_name: 'Team',
      monthly_price: 4999, // $49.99
      annual_price: 47990, // $479.90 (20% discount)
      thread_limit: -1,
      daily_limit: -1,
      monthly_limit: -1,
      features: [
        'unlimited_threads',
        'team_collaboration',
        'admin_dashboard',
        'dedicated_support',
        'custom_branding',
        'api_access',
        'bulk_processing',
        'analytics_export',
        'white_labeling'
      ],
      description: 'Built for teams and agencies',
    },
  ];

  // Use real data if available, otherwise use mock data
  const plans = plansData || mockPlans;
  const effectiveCurrentTier = currentTier || currentPlan?.id || 'free';

  if (error) {
    console.error('Failed to load pricing plans:', error);
  }

  return (
    <div className="py-12">
      {showHeader && (
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Choose the plan that fits your needs. Upgrade or downgrade at any time.
          </p>
        </div>
      )}

      {showBillingToggle && (
        <div className="flex justify-center mb-12">
          <div className="bg-gray-100 rounded-lg p-1">
            <Button
              onClick={() => setBillingFrequency('monthly')}
              variant={billingFrequency === 'monthly' ? 'default' : 'ghost'}
              className={`px-6 py-2 rounded-md font-medium transition-all ${
                billingFrequency === 'monthly'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Monthly
            </Button>
            <Button
              onClick={() => setBillingFrequency('annual')}
              variant={billingFrequency === 'annual' ? 'default' : 'ghost'}
              className={`px-6 py-2 rounded-md font-medium transition-all relative ${
                billingFrequency === 'annual'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Annual
              <span className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full">
                20% OFF
              </span>
            </Button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-7xl mx-auto px-4">
        {plans.map((tier) => (
          <PricingCard
            key={tier.id}
            tier={tier}
            billingFrequency={billingFrequency}
            currentTier={effectiveCurrentTier}
            onSelect={onTierSelect}
            showUpgradeButton={showUpgradeButtons}
          />
        ))}
      </div>

      {isLoading && (
        <div className="text-center mt-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
          <p className="text-gray-600 mt-2">Loading pricing plans...</p>
        </div>
      )}
    </div>
  );
}