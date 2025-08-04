'use client';

import React, { useState, useCallback } from 'react';
import { GenerateThreadRequest } from '@/types/api';
import { useThreadGeneration } from '@/lib/api/hooks/useThreadGeneration';
import { useUsageStats } from '@/lib/api/hooks/useUsageStats';
import { ThreadInput } from './ThreadInput';
import { TweetCard } from './TweetCard';
import { ThreadActions } from './ThreadActions';
import { UsageIndicator } from './UsageIndicator';
import { Button } from '../ui/Button';
import { cn } from '@/lib/utils';

interface ThreadGeneratorProps {
  onUpgrade?: () => void;
  onLogin?: () => void;
  className?: string;
}

export const ThreadGenerator: React.FC<ThreadGeneratorProps> = ({
  onUpgrade,
  onLogin,
  className = ''
}) => {
  const [viewMode, setViewMode] = useState<'edit' | 'preview'>('edit');
  const [showNumbers, setShowNumbers] = useState(true);
  
  const {
    loading,
    error,
    tweets,
    needsPayment,
    generateThread,
    copyTweet,
    copyAllTweets,
    updateTweet,
    clearError,
    reset
  } = useThreadGeneration();

  const {
    usageStatus,
    loading: usageLoading,
    canGenerate,
    needsUpgrade,
    premium
  } = useUsageStats();

  const handleGenerate = useCallback(async (input: string, type: 'url' | 'text') => {
    clearError();
    
    if (!canGenerate && !premium.hasAccess) {
      if (onUpgrade) {
        onUpgrade();
        return;
      }
    }

    const request: GenerateThreadRequest = {
      [type]: input
    };

    await generateThread(request);
  }, [canGenerate, premium.hasAccess, generateThread, clearError, onUpgrade]);

  const handleCopyAll = useCallback(async () => {
    await copyAllTweets();
  }, [copyAllTweets]);

  const handleTweetUpdate = useCallback((index: number, text: string) => {
    if (index >= 0 && index < tweets.length) {
      updateTweet(index, text);
    }
  }, [tweets, updateTweet]);

  const handleTweetCopy = useCallback(async (text: string) => {
    // Individual tweet copy is handled by the TweetCard component
    // This callback is for analytics/tracking if needed
  }, []);

  const shouldShowUpgrade = needsPayment || needsUpgrade || (!premium.hasAccess && !canGenerate);

  return (
    <div className={cn("max-w-4xl mx-auto space-y-6", className)}>
      {/* Usage Indicator */}
      {usageStatus && !premium.hasAccess && (
        <UsageIndicator
          usage={{
            dailyUsed: usageStatus.daily_usage,
            dailyLimit: usageStatus.daily_limit,
            monthlyUsed: usageStatus.monthly_usage,
            monthlyLimit: usageStatus.monthly_limit,
            isPremium: usageStatus.has_premium,
            premiumExpiresAt: usageStatus.premium_expires_at || undefined
          }}
          onUpgrade={onUpgrade}
        />
      )}

      {/* Premium Upgrade CTA */}
      {shouldShowUpgrade && (
        <div className="bg-gradient-to-r from-twitter-blue/20 to-twitter-blue/30 rounded-2xl p-6 border border-twitter-blue/30">
          <div className="text-center space-y-4">
            <h3 className="text-xl font-bold text-white">Upgrade to Continue</h3>
            <p className="text-twitter-gray">
              {needsPayment 
                ? "You've reached your daily limit. Upgrade to premium for unlimited thread generation."
                : "Get unlimited access to thread generation and premium features."
              }
            </p>
            <Button
              onClick={onUpgrade}
              className="bg-twitter-blue hover:bg-twitter-hover text-white px-8 py-3 rounded-full font-semibold transition-colors"
            >
              Upgrade to Premium - $4.99
            </Button>
          </div>
        </div>
      )}

      {/* Thread Input */}
      <ThreadInput
        onGenerate={handleGenerate}
        loading={loading}
        disabled={shouldShowUpgrade}
      />

      {/* Error Display */}
      {error && (
        <div className="bg-red-900/30 border border-red-500/50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.728-.833-2.598 0L4.196 15.5c-.77.833.19 2.5 1.732 2.5z" />
              </svg>
              <span className="text-red-400 font-medium">Error</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearError}
              className="text-red-400 hover:text-red-300"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </Button>
          </div>
          <p className="text-red-300 mt-2">{error}</p>
        </div>
      )}

      {/* Tweet Results */}
      {tweets.length > 0 && (
        <div className="space-y-6">
          {/* View Mode Toggle */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h2 className="text-xl font-bold text-white">Your Thread</h2>
              <span className="text-twitter-gray">({tweets.length} tweets)</span>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Number Toggle */}
              <label className="flex items-center space-x-2 text-sm">
                <input
                  type="checkbox"
                  checked={showNumbers}
                  onChange={(e) => setShowNumbers(e.target.checked)}
                  className="rounded border-twitter-border text-twitter-blue focus:ring-twitter-blue focus:ring-offset-0 bg-twitter-dark"
                />
                <span className="text-twitter-gray">Show numbers</span>
              </label>
              
              {/* View Mode Toggle */}
              <div className="inline-flex rounded-lg bg-twitter-dark border border-twitter-border p-1">
                <button
                  onClick={() => setViewMode('edit')}
                  className={cn(
                    'px-3 py-1 rounded-md text-sm font-medium transition-all',
                    viewMode === 'edit'
                      ? 'bg-twitter-blue text-white shadow-sm'
                      : 'text-twitter-gray hover:text-white hover:bg-twitter-border'
                  )}
                >
                  Edit
                </button>
                <button
                  onClick={() => setViewMode('preview')}
                  className={cn(
                    'px-3 py-1 rounded-md text-sm font-medium transition-all',
                    viewMode === 'preview'
                      ? 'bg-twitter-blue text-white shadow-sm'
                      : 'text-twitter-gray hover:text-white hover:bg-twitter-border'
                  )}
                >
                  Preview
                </button>
              </div>
            </div>
          </div>

          {/* Tweet List */}
          <div className="space-y-4">
            {tweets.map((tweet, index) => (
              <TweetCard
                key={index}
                tweet={tweet}
                index={index}
                totalTweets={tweets.length}
                onUpdate={handleTweetUpdate}
                onCopy={handleTweetCopy}
              />
            ))}
          </div>

          {/* Thread Actions */}
          <ThreadActions
            onCopyAll={handleCopyAll}
            onRegenerate={() => {
              // You might want to store the last request to regenerate
              reset();
            }}
            onSaveThread={() => {
              // Implement save functionality
              console.log('Save thread functionality to be implemented');
            }}
            isRegenerating={loading}
            canSave={true} // You can make this conditional based on auth state
            tweetCount={tweets.length}
          />
        </div>
      )}

      {/* Empty State */}
      {!loading && tweets.length === 0 && !error && (
        <div className="text-center py-12">
          <div className="w-20 h-20 mx-auto mb-4 bg-twitter-dark rounded-full flex items-center justify-center">
            <svg className="w-10 h-10 text-twitter-gray" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-white mb-2">Ready to Generate Your Thread</h3>
          <p className="text-twitter-gray">
            Paste an article URL or your content above, then click "Generate Thread" to get started.
          </p>
        </div>
      )}
    </div>
  );
};