'use client';

import React from 'react';
import { TweetCard } from './TweetCard';
import { ThreadActions } from './ThreadActions';

interface Tweet {
  content: string;
  character_count: number;
  number: number;
  total: number;
}

interface TweetListProps {
  tweets: Tweet[];
  onUpdateTweet: (index: number, text: string) => void;
  onCopyTweet: (text: string) => void;
  onCopyAll: () => void;
  onRegenerate: () => void;
  onSaveThread?: () => void;
  isRegenerating?: boolean;
  canSave?: boolean;
  className?: string;
}

export const TweetList: React.FC<TweetListProps> = ({
  tweets,
  onUpdateTweet,
  onCopyTweet,
  onCopyAll,
  onRegenerate,
  onSaveThread,
  isRegenerating = false,
  canSave = false,
  className = ''
}) => {
  if (tweets.length === 0) {
    return null;
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Thread Actions */}
      <ThreadActions
        onCopyAll={onCopyAll}
        onRegenerate={onRegenerate}
        onSaveThread={onSaveThread}
        isRegenerating={isRegenerating}
        canSave={canSave}
        tweetCount={tweets.length}
      />

      {/* Tweet Cards */}
      <div className="space-y-4">
        {tweets.map((tweet, index) => (
          <TweetCard
            key={index}
            tweet={tweet}
            index={index}
            totalTweets={tweets.length}
            onUpdate={(idx, text) => onUpdateTweet(idx, text)}
            onCopy={onCopyTweet}
          />
        ))}
      </div>

      {/* Bottom Actions (duplicate for convenience) */}
      <ThreadActions
        onCopyAll={onCopyAll}
        onRegenerate={onRegenerate}
        onSaveThread={onSaveThread}
        isRegenerating={isRegenerating}
        canSave={canSave}
        tweetCount={tweets.length}
      />
    </div>
  );
};