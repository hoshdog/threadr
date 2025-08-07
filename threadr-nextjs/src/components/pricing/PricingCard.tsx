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
        <div key={index} className="flex items-center">
          <div className="w-5 h-5 bg-green-100 rounded-full flex items-center justify-center mr-3">
            <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          </div>
          <span className="text-sm text-gray-700">{displayName}</span>
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
    <Card className={`relative ${tier.popular ? 'border-purple-500 shadow-xl scale-105' : 'border-gray-200'} ${isCurrentPlan ? 'ring-2 ring-blue-500' : ''}`}>
      {tier.popular && (
        <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
          <span className="bg-gradient-to-r from-purple-500 to-indigo-600 text-white px-4 py-2 rounded-full text-sm font-semibold">
            Most Popular
          </span>
        </div>
      )}
      
      {isCurrentPlan && (
        <div className="absolute -top-4 right-4">
          <span className="bg-blue-500 text-white px-3 py-1 rounded-full text-xs font-semibold">
            Current Plan
          </span>
        </div>
      )}

      <CardHeader className="text-center pb-4">
        <CardTitle className="text-xl font-bold">{tier.name}</CardTitle>
        <CardDescription className="text-gray-600">{tier.description}</CardDescription>
        
        <div className="mt-4">
          <div className="text-4xl font-bold text-gray-900">
            {isFree ? (
              'Free'
            ) : (
              <>
                ${displayPrice.toFixed(2)}
                <span className="text-lg font-normal text-gray-600">
                  /{billingFrequency === 'monthly' ? 'month' : 'year'}
                </span>
              </>
            )}
          </div>
          
          {billingFrequency === 'annual' && monthlySavings > 0 && (
            <div className="text-sm text-green-600 mt-1">
              Save ${monthlySavings.toFixed(2)} per year
            </div>
          )}
          
          <div className="text-sm text-gray-600 mt-2">
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
            className={`w-full ${
              tier.popular 
                ? 'bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700' 
                : isCurrentPlan 
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-gray-900 hover:bg-gray-800'
            } text-white font-semibold py-2 px-4 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {isLoading || upgradeMutation.isPending ? (
              <div className="flex items-center justify-center">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Processing...
              </div>
            ) : isCurrentPlan ? (
              'Current Plan'
            ) : isFree ? (
              'Get Started'
            ) : (
              `Upgrade to ${tier.display_name}`
            )}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}