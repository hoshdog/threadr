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

    // Backend expects: content (required), url (optional)
    // If type is 'url', pass input as both content AND url
    // If type is 'text', pass input as content only
    const request: GenerateThreadRequest = {
      content: input,
      ...(type === 'url' && { url: input })
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
          onUpgrade={onUpgrade}
        />
      )}

      {/* Premium Upgrade CTA */}
      {shouldShowUpgrade && (
        <div className="bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 rounded-2xl p-8 border border-purple-400/30 shadow-2xl">
          <div className="text-center space-y-6">
            <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-2xl font-bold text-white">Unlock Unlimited Power</h3>
            <p className="text-white/90 text-lg leading-relaxed max-w-md mx-auto">
              {needsPayment 
                ? "You've reached your free limit. Join thousands of creators generating unlimited viral threads."
                : "Generate unlimited threads, access premium templates, and boost your engagement 300%."
              }
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                onClick={onUpgrade}
                variant="primary"
                size="lg"
                className="bg-white text-indigo-600 hover:bg-gray-100 shadow-lg font-bold"
              >
                Upgrade to Pro - $9.99/month
              </Button>
              <Button
                variant="ghost"
                size="lg"
                className="text-white border-white/30 hover:bg-white/10"
              >
                View All Plans
              </Button>
            </div>
            <div className="flex items-center justify-center gap-6 text-sm text-white/80">
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Unlimited threads</span>
              </div>
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Premium templates</span>
              </div>
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span>Analytics</span>
              </div>
            </div>
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