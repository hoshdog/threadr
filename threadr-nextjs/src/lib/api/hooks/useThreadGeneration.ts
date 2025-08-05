import { useState, useCallback } from 'react';
import { GenerateThreadRequest, GenerateThreadResponse as ApiGenerateThreadResponse, UsageStatus, Tweet as ApiTweet } from '@/types/api';
import { Tweet } from '@/types';
import { threadsApi } from '../threads';

interface ThreadGenerationState {
  loading: boolean;
  error: string | null;
  tweets: Tweet[];
  usageStatus: UsageStatus | null;
  needsPayment: boolean;
}

interface UseThreadGenerationReturn extends ThreadGenerationState {
  generateThread: (request: GenerateThreadRequest) => Promise<void>;
  copyTweet: (index: number) => Promise<void>;
  copyAllTweets: () => Promise<void>;
  updateTweet: (index: number, content: string) => void;
  clearError: () => void;
  reset: () => void;
}

export function useThreadGeneration(): UseThreadGenerationReturn {
  const [state, setState] = useState<ThreadGenerationState>({
    loading: false,
    error: null,
    tweets: [],
    usageStatus: null,
    needsPayment: false,
  });

  // Remove getAuthHeaders since the API client handles auth automatically

  const handleApiError = useCallback((error: any) => {
    let errorMessage = 'Failed to generate thread. Please try again.';
    
    // Handle rate limiting
    if (error.status === 429) {
      return 'Rate limit exceeded. You\'ve reached your daily limit. Please upgrade to premium for unlimited access.';
    }
    
    // Handle authentication errors
    if (error.status === 401) {
      return 'Session expired. Please log in again.';
    }
    
    // Handle server errors
    if (error.status >= 500) {
      return 'Server error. Please try again later.';
    }
    
    // Use API error message if available
    if (error.message) {
      errorMessage = error.message;
    }
    
    return errorMessage;
  }, []);

  const generateThread = useCallback(async (request: GenerateThreadRequest) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const data: ApiGenerateThreadResponse = await threadsApi.generateThread(request);

      if (!data || !data.thread || !Array.isArray(data.thread)) {
        setState(prev => ({ 
          ...prev, 
          loading: false, 
          error: 'Invalid response format from server.' 
        }));
        return;
      }

      // Transform API response to match our Tweet interface
      const tweets: Tweet[] = data.thread.map((apiTweet: ApiTweet, index) => ({
        id: `tweet-${index}`,
        content: apiTweet.content,
        order: apiTweet.number,
        characterCount: apiTweet.character_count,
      }));

      setState(prev => ({ 
        ...prev, 
        loading: false, 
        tweets,
        needsPayment: false
      }));

    } catch (error: any) {
      console.error('Thread generation error:', error);
      const errorMessage = handleApiError(error);
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: errorMessage,
        needsPayment: error.status === 429
      }));
    }
  }, [handleApiError]);

  const copyTweet = useCallback(async (index: number) => {
    if (index < 0 || index >= state.tweets.length) {
      return;
    }

    const tweet = state.tweets[index];
    if (!tweet) {
      return;
    }

    try {
      await navigator.clipboard.writeText(tweet.content);
      // Note: For UI feedback, the component should handle this
    } catch (error) {
      console.error('Failed to copy tweet:', error);
      throw new Error('Failed to copy tweet');
    }
  }, [state.tweets]);

  const copyAllTweets = useCallback(async () => {
    if (state.tweets.length === 0) {
      return;
    }

    try {
      const threadText = state.tweets
        .map((tweet, index) => `${index + 1}/${state.tweets.length}\n\n${tweet.content}`)
        .join('\n\n---\n\n');
      
      await navigator.clipboard.writeText(threadText);
    } catch (error) {
      console.error('Failed to copy thread:', error);
      throw new Error('Failed to copy thread');
    }
  }, [state.tweets]);

  const updateTweet = useCallback((index: number, content: string) => {
    if (index < 0 || index >= state.tweets.length) {
      return;
    }

    setState(prev => ({
      ...prev,
      tweets: prev.tweets.map((tweet, i) => 
        i === index 
          ? { ...tweet, content, characterCount: content.length }
          : tweet
      )
    }));
  }, [state.tweets.length]);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  const reset = useCallback(() => {
    setState({
      loading: false,
      error: null,
      tweets: [],
      usageStatus: null,
      needsPayment: false,
    });
  }, []);

  return {
    ...state,
    generateThread,
    copyTweet,
    copyAllTweets,
    updateTweet,
    clearError,
    reset,
  };
}