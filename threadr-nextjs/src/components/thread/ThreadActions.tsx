'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';
import { 
  Copy, 
  RefreshCw, 
  Save, 
  Check,
  Twitter,
  Share
} from 'lucide-react';

interface ThreadActionsProps {
  onCopyAll: () => void;
  onRegenerate: () => void;
  onSaveThread?: () => void;
  isRegenerating?: boolean;
  canSave?: boolean;
  tweetCount: number;
  className?: string;
}

export const ThreadActions: React.FC<ThreadActionsProps> = ({
  onCopyAll,
  onRegenerate,
  onSaveThread,
  isRegenerating = false,
  canSave = false,
  tweetCount,
  className = ''
}) => {
  const [copied, setCopied] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleCopyAll = async () => {
    try {
      await onCopyAll();
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy thread:', err);
    }
  };

  const handleSave = async () => {
    if (onSaveThread) {
      try {
        await onSaveThread();
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
      } catch (err) {
        console.error('Failed to save thread:', err);
      }
    }
  };

  return (
    <div className={cn(
      "bg-[#15202b] rounded-2xl p-6 border border-[#38444d]",
      className
    )}>
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* Thread Info */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Twitter className="w-5 h-5 text-[#1d9bf0]" />
            <span className="text-white font-medium">
              {tweetCount} Tweet{tweetCount !== 1 ? 's' : ''} Generated
            </span>
          </div>
          <div className="text-[#8899ac] text-sm">
            Ready to post as a thread
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-3">
          {/* Save Thread Button */}
          {canSave && onSaveThread && (
            <Button
              variant="secondary"
              onClick={handleSave}
              disabled={saved}
              className={cn(
                "text-[#8899ac] border-[#38444d] hover:text-white hover:bg-[#1d2d3a]",
                "hover:border-[#1d9bf0]/50 transition-all duration-200",
                saved && "text-green-400 border-green-400/50"
              )}
            >
              {saved ? (
                <>
                  <Check className="w-4 h-4 mr-2" />
                  Saved
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Save Thread
                </>
              )}
            </Button>
          )}

          {/* Copy All Button */}
          <Button
            variant="secondary"
            onClick={handleCopyAll}
            disabled={copied}
            className={cn(
              "bg-[#15202b] text-white border border-[#38444d]",
              "hover:bg-[#1d2d3a] hover:border-[#1d9bf0]/50",
              "transition-all duration-200",
              copied && "text-green-400 border-green-400/50"
            )}
          >
            {copied ? (
              <>
                <Check className="w-4 h-4 mr-2" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="w-4 h-4 mr-2" />
                Copy All
              </>
            )}
          </Button>

          {/* Regenerate Button */}
          <Button
            variant="secondary"
            onClick={onRegenerate}
            disabled={isRegenerating}
            loading={isRegenerating}
            className={cn(
              "text-[#8899ac] border-[#38444d] hover:text-white",
              "hover:bg-[#1d2d3a] hover:border-[#1d9bf0]/50",
              "transition-all duration-200"
            )}
          >
            <RefreshCw className={cn(
              "w-4 h-4 mr-2",
              isRegenerating && "animate-spin"
            )} />
            {isRegenerating ? 'Regenerating...' : 'Regenerate'}
          </Button>

          {/* Share/Post Button */}
          <Button
            variant="primary"
            onClick={() => {
              // Open Twitter with intent to post
              const twitterUrl = 'https://twitter.com/intent/tweet';
              window.open(twitterUrl, '_blank');
            }}
            className="bg-[#1d9bf0] hover:bg-[#1a8cd8] text-white"
          >
            <Share className="w-4 h-4 mr-2" />
            Post to X
          </Button>
        </div>
      </div>

      {/* Pro Tip */}
      <div className="mt-4 pt-4 border-t border-[#38444d]">
        <div className="flex items-start space-x-2 text-sm text-[#8899ac]">
          <div className="w-2 h-2 bg-[#1d9bf0] rounded-full mt-2 flex-shrink-0"></div>
          <div>
            <span className="font-medium text-white">Pro tip:</span> Copy the entire thread, 
            then paste tweets one by one on Twitter/X. Use the reply feature to create the thread chain.
          </div>
        </div>
      </div>
    </div>
  );
};