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

  // For now, always use mock data to ensure type compatibility
  // TODO: Map plansData from API to PricingTier format when backend is ready
  const plans: PricingTier[] = mockPlans;
  const effectiveCurrentTier = currentTier || currentPlan?.id || 'free';

  if (error) {
    console.error('Failed to load pricing plans:', error);
  }

  return (
    <div className="py-20">
      {showHeader && (
        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center px-4 py-2 rounded-full bg-blue-50 text-blue-700 text-sm font-medium mb-6">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Trusted by 10,000+ creators
          </div>
          <h2 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Choose Your 
            <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent block mt-2">
              Growth Plan
            </span>
          </h2>
          <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
            From individual creators to enterprise teams, we have the perfect plan to amplify your content reach and engagement.
          </p>
        </div>
      )}

      {showBillingToggle && (
        <div className="flex justify-center mb-16">
          <div className="bg-gray-100 dark:bg-gray-800 rounded-xl p-2 inline-flex shadow-lg">
            <Button
              onClick={() => setBillingFrequency('monthly')}
              variant="ghost"
              className={`px-8 py-3 rounded-lg font-semibold transition-all ${
                billingFrequency === 'monthly'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-md'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Monthly
            </Button>
            <Button
              onClick={() => setBillingFrequency('annual')}
              variant="ghost"
              className={`px-8 py-3 rounded-lg font-semibold transition-all relative ${
                billingFrequency === 'annual'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-md'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Annual
              <span className="absolute -top-1 -right-1 bg-gradient-to-r from-green-500 to-emerald-500 text-white text-xs px-2 py-1 rounded-full font-bold shadow-lg">
                Save 20%
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