'use client';

import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { useUpgradeToPremium } from '@/hooks/api/useSubscription';
import { useState } from 'react';

export interface PricingTier {
  id: string;
  name: string;
  display_name: string;
  monthly_price: number;
  annual_price: number;
  thread_limit: number;
  daily_limit: number;
  monthly_limit: number;
  features: string[];
  description: string;
  popular?: boolean;
}

interface PricingCardProps {
  tier: PricingTier;
  billingFrequency: 'monthly' | 'annual';
  currentTier?: string;
  onSelect?: (tierId: string) => void;
  showUpgradeButton?: boolean;
}

const featureDisplayNames: Record<string, string> = {
  basic_threads: 'Basic thread generation',
  unlimited_threads: 'Unlimited thread generation',
  basic_analytics: 'Basic analytics',
  advanced_analytics: 'Advanced analytics & insights',
  email_support: 'Email support',
  priority_support: 'Priority customer support',
  premium_templates: 'Premium templates',
  custom_scheduling: 'Custom scheduling',
  export_threads: 'Export threads in multiple formats',
  team_collaboration: 'Team collaboration',
  admin_dashboard: 'Admin dashboard',
  dedicated_support: 'Dedicated support',
  custom_branding: 'Custom branding',
  api_access: 'API access',
  bulk_processing: 'Bulk processing',
  analytics_export: 'Analytics export',
  white_labeling: 'White labeling',
};

export default function PricingCard({ 
  tier, 
  billingFrequency, 
  currentTier, 
  onSelect, 
  showUpgradeButton = true 
}: PricingCardProps) {
  const [isLoading, setIsLoading] = useState(false);
  const upgradeMutation = useUpgradeToPremium();

  const price = billingFrequency === 'monthly' ? tier.monthly_price : tier.annual_price;
  const displayPrice = price / 100; // Convert cents to dollars
  
  // Calculate savings for annual billing
  const monthlySavings = billingFrequency === 'annual' 
    ? ((tier.monthly_price * 12) - tier.annual_price) / 100 
    : 0;

  const isCurrentPlan = currentTier === tier.id;
  const isFree = tier.monthly_price === 0;

  const handleUpgrade = async () => {
    if (onSelect) {
      onSelect(tier.id);
      return;
    }

    if (isFree || isCurrentPlan) return;

    try {
      setIsLoading(true);
      await upgradeMutation.mutateAsync({
        plan_id: tier.id,
        billing_frequency: billingFrequency,
        success_url: `${window.location.origin}/payment/success`,
        cancel_url: window.location.href,
      });
    } catch (error) {
      console.error('Failed to start upgrade process:', error);
      setIsLoading(false);
      alert('Failed to start payment process. Please try again.');
    }
  };

  const renderFeatures = () => {
    return tier.features.map((feature, index) => {
      const displayName = featureDisplayNames[feature] || feature;
      return (
        <div key={index} className="flex items-center py-2">
          <div className="w-6 h-6 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full flex items-center justify-center mr-3 shadow-sm">
            <svg className="w-3.5 h-3.5 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          </div>
          <span className="text-sm text-gray-700 dark:text-gray-300 font-medium">{displayName}</span>
        </div>
      );
    });
  };

  const renderThreadLimits = () => {
    if (tier.thread_limit === -1) {
      return "Unlimited threads";
    }
    
    const limits = [];
    if (tier.daily_limit > 0) {
      limits.push(`${tier.daily_limit} daily`);
    }
    if (tier.monthly_limit > 0) {
      limits.push(`${tier.monthly_limit} monthly`);
    }
    
    return limits.length > 0 ? limits.join(', ') : `${tier.thread_limit} threads`;
  };

  return (
    <Card className={`relative transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl ${
      tier.popular 
        ? 'border-2 border-purple-400 shadow-2xl scale-105 bg-gradient-to-b from-purple-50 to-indigo-50 dark:from-purple-950/20 dark:to-indigo-950/20' 
        : 'border border-gray-200 dark:border-gray-700 shadow-lg hover:border-gray-300 dark:hover:border-gray-600 bg-white dark:bg-gray-800'
    } ${
      isCurrentPlan ? 'ring-2 ring-blue-400 dark:ring-blue-500' : ''
    }`}>
      {tier.popular && (
        <div className="absolute -top-10 left-1/2 transform -translate-x-1/2 z-10">
          <span className="bg-gradient-to-r from-purple-500 via-indigo-500 to-pink-500 text-white px-8 py-2 rounded-full text-sm font-bold shadow-lg animate-pulse whitespace-nowrap">
            ✨ Most Popular ✨
          </span>
        </div>
      )}
      
      {isCurrentPlan && (
        <div className="absolute -top-3 right-4">
          <span className="bg-blue-500 text-white px-3 py-1 rounded-full text-xs font-bold shadow-md">
            Current Plan
          </span>
        </div>
      )}

      <CardHeader className="text-center pb-6 pt-8">
        <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center">
          {isFree ? (
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          ) : tier.popular ? (
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          ) : tier.display_name === 'Starter' ? (
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          ) : (
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          )}
        </div>
        
        <CardTitle className="text-2xl font-bold mb-2">{tier.display_name}</CardTitle>
        <CardDescription className="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">{tier.description}</CardDescription>
        
        <div className="mb-4">
          <div className={`text-5xl font-bold mb-2 ${tier.popular ? 'text-purple-600 dark:text-purple-400' : 'text-gray-900 dark:text-gray-100'}`}>
            {isFree ? (
              'Free'
            ) : (
              <>
                ${displayPrice.toFixed(0)}
                <span className="text-xl font-normal text-gray-500 dark:text-gray-400">
                  /{billingFrequency === 'monthly' ? 'mo' : 'yr'}
                </span>
              </>
            )}
          </div>
          
          {billingFrequency === 'annual' && monthlySavings > 0 && (
            <div className="inline-block bg-green-100 text-green-700 text-sm font-semibold px-3 py-1 rounded-full mb-2">
              💰 Save ${monthlySavings.toFixed(0)}/year
            </div>
          )}
          
          <div className="text-sm text-gray-600 dark:text-gray-400 font-medium">
            {renderThreadLimits()}
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {/* Features List */}
        <div className="space-y-3 mb-6">
          {renderFeatures()}
        </div>

        {/* Action Button */}
        {showUpgradeButton && (
          <Button
            onClick={handleUpgrade}
            disabled={isLoading || upgradeMutation.isPending || isCurrentPlan}
            variant={tier.popular ? "premium" : isCurrentPlan ? "outline" : "primary"}
            size="lg"
            className={`w-full transition-all duration-200 ${
              isCurrentPlan 
                ? 'cursor-not-allowed opacity-60' 
                : 'hover:scale-105 active:scale-95'
            }`}
          >
            {isLoading || upgradeMutation.isPending ? (
              <div className="flex items-center justify-center">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Processing...
              </div>
            ) : isCurrentPlan ? (
              <div className="flex items-center justify-center">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Active Plan
              </div>
            ) : isFree ? (
              'Start Free'
            ) : (
              <>
                {tier.popular ? '🚀 ' : ''}Upgrade to {tier.display_name}
              </>
            )}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}