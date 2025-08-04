'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';
import { UpgradeModal } from '@/components/ui';
import { useFeatureAccess, useSubscriptionStatus } from '@/hooks/api/useSubscription';
import { 
  Crown, 
  Zap, 
  Clock, 
  TrendingUp,
  AlertCircle
} from 'lucide-react';

interface UsageIndicatorProps {
  onUpgrade?: () => void;
  className?: string;
}

export const UsageIndicator: React.FC<UsageIndicatorProps> = ({
  onUpgrade,
  className = ''
}) => {
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const { isPremium, expiresAt } = useSubscriptionStatus();
  const { 
    remainingThreadsDaily, 
    remainingThreadsMonthly, 
    dailyUsage, 
    monthlyUsage, 
    dailyLimit, 
    monthlyLimit,
    hasUnlimitedAccess 
  } = useFeatureAccess();

  const dailyUsed = dailyUsage;
  const monthlyUsed = monthlyUsage;
  const premiumExpiresAt = expiresAt;

  const dailyPercentage = Math.min((dailyUsed / dailyLimit) * 100, 100);
  const monthlyPercentage = Math.min((monthlyUsed / monthlyLimit) * 100, 100);
  
  const isNearDailyLimit = dailyPercentage >= 80;
  const isNearMonthlyLimit = monthlyPercentage >= 80;
  const isAtLimit = dailyUsed >= dailyLimit || monthlyUsed >= monthlyLimit;

  const getDaysUntilExpiry = () => {
    if (!premiumExpiresAt) return null;
    const expiryDate = new Date(premiumExpiresAt);
    const now = new Date();
    const diffTime = expiryDate.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const daysUntilExpiry = getDaysUntilExpiry();

  const handleUpgradeClick = () => {
    if (onUpgrade) {
      onUpgrade();
    } else {
      setShowUpgradeModal(true);
    }
  };

  if (isPremium || hasUnlimitedAccess) {
    return (
      <div className={cn(
        "bg-gradient-to-r from-amber-500/20 to-yellow-500/20 rounded-2xl p-4 border border-amber-500/30",
        className
      )}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-amber-500 to-yellow-500 rounded-full flex items-center justify-center">
              <Crown className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-white font-semibold">Premium Active</span>
                <div className="px-2 py-1 bg-amber-500/20 rounded-full">
                  <span className="text-amber-400 text-xs font-medium">UNLIMITED</span>
                </div>
              </div>
              <div className="text-[#8899ac] text-sm">
                {daysUntilExpiry !== null && daysUntilExpiry > 0 ? (
                  `${daysUntilExpiry} day${daysUntilExpiry !== 1 ? 's' : ''} remaining`
                ) : daysUntilExpiry === 0 ? (
                  'Expires today'
                ) : (
                  'Expired - Please renew'
                )}
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-amber-400" />
            <span className="text-amber-400 font-medium">Unlimited</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn(
      "bg-[#15202b] rounded-2xl p-4 border border-[#38444d]",
      (isNearDailyLimit || isNearMonthlyLimit) && "border-yellow-500/30",
      isAtLimit && "border-red-500/30",
      className
    )}>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-[#1d9bf0]" />
            <span className="text-white font-medium">Usage Limits</span>
          </div>
          {isAtLimit && (
            <div className="flex items-center space-x-1 text-red-400">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm font-medium">Limit Reached</span>
            </div>
          )}
        </div>

        {/* Daily Usage */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-[#8899ac] text-sm">Daily</span>
            <span className={cn(
              "text-sm font-medium",
              isNearDailyLimit ? "text-yellow-400" : "text-white",
              dailyUsed >= dailyLimit && "text-red-400"
            )}>
              {dailyUsed}/{dailyLimit}
            </span>
          </div>
          <div className="w-full bg-[#000000] rounded-full h-2">
            <div
              className={cn(
                "h-2 rounded-full transition-all duration-300",
                dailyPercentage >= 100 ? "bg-red-500" :
                dailyPercentage >= 80 ? "bg-yellow-500" :
                "bg-[#1d9bf0]"
              )}
              style={{ width: `${Math.min(dailyPercentage, 100)}%` }}
            />
          </div>
        </div>

        {/* Monthly Usage */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-[#8899ac] text-sm">Monthly</span>
            <span className={cn(
              "text-sm font-medium",
              isNearMonthlyLimit ? "text-yellow-400" : "text-white",
              monthlyUsed >= monthlyLimit && "text-red-400"
            )}>
              {monthlyUsed}/{monthlyLimit}
            </span>
          </div>
          <div className="w-full bg-[#000000] rounded-full h-2">
            <div
              className={cn(
                "h-2 rounded-full transition-all duration-300",
                monthlyPercentage >= 100 ? "bg-red-500" :
                monthlyPercentage >= 80 ? "bg-yellow-500" :
                "bg-[#1d9bf0]"
              )}
              style={{ width: `${Math.min(monthlyPercentage, 100)}%` }}
            />
          </div>
        </div>

        {/* Upgrade CTA */}
        {(isNearDailyLimit || isNearMonthlyLimit || isAtLimit) && (
          <div className="pt-3 border-t border-[#38444d]">
            <div className="flex items-center justify-between">
              <div className="text-sm text-[#8899ac]">
                {isAtLimit ? 'Upgrade for unlimited access' : 'Running low? Upgrade now'}
              </div>
              <Button
                variant="primary"
                size="sm"
                onClick={handleUpgradeClick}
                className={cn(
                  "bg-gradient-to-r from-[#1d9bf0] to-[#1a8cd8] hover:from-[#1a8cd8] hover:to-[#1976c2]",
                  "text-white font-medium px-4 py-2 text-sm"
                )}
              >
                <Crown className="w-4 h-4 mr-1" />
                Upgrade
              </Button>
            </div>
          </div>
        )}

        {/* Reset Info */}
        <div className="text-xs text-[#8899ac] flex items-center space-x-1">
          <Clock className="w-3 h-3" />
          <span>Daily limit resets at midnight UTC</span>
        </div>
      </div>
      
      {/* Upgrade Modal */}
      <UpgradeModal
        isOpen={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
        trigger="rate_limit"
        title="You've reached your free limit"
        description={`You've used ${dailyUsed}/${dailyLimit} daily threads and ${monthlyUsed}/${monthlyLimit} monthly threads.`}
      />
    </div>
  );
};