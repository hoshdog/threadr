'use client';

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui';
import { useUpgradeToPremium, useSubscriptionStatus, useFeatureAccess } from '@/hooks/api/useSubscription';

interface UpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  trigger: 'rate_limit' | 'premium_template' | 'premium_feature';
  title?: string;
  description?: string;
  successUrl?: string;
  cancelUrl?: string;
}

export default function UpgradeModal({ 
  isOpen, 
  onClose, 
  trigger,
  title,
  description,
  successUrl,
  cancelUrl
}: UpgradeModalProps) {
  const [isLoading, setIsLoading] = useState(false);
  const upgradeMutation = useUpgradeToPremium();
  const { premiumPrice } = useSubscriptionStatus();
  const { remainingThreadsDaily, remainingThreadsMonthly, dailyLimit, monthlyLimit } = useFeatureAccess();

  // Dynamic content based on trigger
  const getContent = () => {
    switch (trigger) {
      case 'rate_limit':
        return {
          title: 'You\'ve reached your free limit',
          description: `You've used ${dailyLimit - remainingThreadsDaily}/${dailyLimit} daily threads and ${monthlyLimit - remainingThreadsMonthly}/${monthlyLimit} monthly threads.`,
          features: [
            'Unlimited thread generations',
            'No daily or monthly limits',
            'Priority customer support',
            'Access to premium templates',
            'Advanced analytics and insights'
          ]
        };
      case 'premium_template':
        return {
          title: 'Premium Template Access',
          description: 'This template is part of our premium collection with advanced formatting and proven engagement patterns.',
          features: [
            'Access to 50+ premium templates',
            'Unlimited thread generations',
            'Advanced template customization',
            'Priority customer support',
            'Export threads in multiple formats'
          ]
        };
      case 'premium_feature':
        return {
          title: 'Premium Feature Required',
          description: 'This feature is available to premium users only.',
          features: [
            'All premium features unlocked',
            'Unlimited thread generations',
            'Advanced analytics and insights',
            'Priority customer support',
            'Custom template creation tools'
          ]
        };
      default:
        return {
          title: 'Upgrade to Premium',
          description: 'Unlock all features and unlimited thread generations.',
          features: [
            'Unlimited thread generations',
            'Access to premium templates',
            'Advanced analytics and insights',
            'Priority customer support',
            'Export threads in multiple formats'
          ]
        };
    }
  };

  const content = getContent();
  const displayTitle = title || content.title;
  const displayDescription = description || content.description;

  const handleUpgrade = async () => {
    try {
      setIsLoading(true);
      
      // Redirect to Stripe checkout
      await upgradeMutation.mutateAsync({
        success_url: successUrl || `${window.location.origin}/payment/success`,
        cancel_url: cancelUrl || window.location.href,
      });
    } catch (error) {
      console.error('Failed to start upgrade process:', error);
      setIsLoading(false);
      
      // Show error to user
      alert('Failed to start payment process. Please try again.');
    }
  };

  // Handle escape key
  useEffect(() => {
    if (!isOpen) return;
    
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Prevent background scroll
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = 'unset';
      };
    }
    return undefined;
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative w-full max-w-lg transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all animate-slide-up">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-500 to-indigo-600 px-6 py-6 text-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h2 className="text-xl font-bold">
                    {displayTitle}
                  </h2>
                  <p className="text-indigo-100 text-sm">
                    Upgrade to continue using Threadr
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                disabled={isLoading}
                className="text-white hover:text-gray-200 transition-colors p-1 rounded disabled:opacity-50"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="px-6 py-6">
            {/* Description */}
            <div className="mb-6">
              <p className="text-gray-600 text-sm leading-relaxed">
                {displayDescription}
              </p>
            </div>

            {/* Premium Features */}
            <div className="mb-6">
              <h4 className="text-md font-semibold text-gray-900 mb-3">
                Premium Features Include:
              </h4>
              <div className="space-y-2">
                {content.features.map((feature, index) => (
                  <div key={index} className="flex items-center">
                    <div className="w-5 h-5 bg-green-100 rounded-full flex items-center justify-center mr-3">
                      <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <span className="text-sm text-gray-700">{feature}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Pricing Info */}
            <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900 mb-1">
                  ${premiumPrice || 4.99}
                  <span className="text-sm font-normal text-gray-600"> for 30 days</span>
                </div>
                <p className="text-sm text-gray-600">
                  Unlimited access • No recurring charges
                </p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="px-6 py-4 bg-gray-50 flex space-x-3">
            <Button
              variant="secondary"
              onClick={onClose}
              disabled={isLoading}
              className="flex-1"
            >
              Maybe Later
            </Button>
            <Button
              variant="primary"
              onClick={handleUpgrade}
              disabled={isLoading || upgradeMutation.isPending}
              className="flex-1 bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading || upgradeMutation.isPending ? (
                <div className="flex items-center justify-center">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Processing...
                </div>
              ) : (
                'Upgrade Now'
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}