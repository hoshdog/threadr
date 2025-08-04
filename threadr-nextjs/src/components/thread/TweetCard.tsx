'use client';

import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';
import { 
  Copy, 
  Edit3, 
  Check, 
  X, 
  MessageCircle, 
  Repeat2, 
  Heart, 
  Share 
} from 'lucide-react';

interface Tweet {
  content: string;
}

interface TweetCardProps {
  tweet: Tweet;
  index: number;
  totalTweets: number;
  onUpdate: (index: number, text: string) => void;
  onCopy: (text: string) => void;
}

export const TweetCard: React.FC<TweetCardProps> = ({
  tweet,
  index,
  totalTweets,
  onUpdate,
  onCopy
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(tweet.content);
  const [copied, setCopied] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (isEditing && textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.setSelectionRange(editText.length, editText.length);
    }
  }, [isEditing, editText.length]);

  const handleSave = () => {
    if (editText.trim() && editText !== tweet.content) {
      onUpdate(index, editText.trim());
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditText(tweet.content);
    setIsEditing(false);
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(tweet.content);
      onCopy(tweet.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const characterCount = editText.length;
  const isOverLimit = characterCount > 280;

  return (
    <div className="bg-[#15202b] rounded-2xl p-6 border border-[#38444d] hover:border-[#1d9bf0]/50 transition-all duration-200">
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs text-[#8899ac] font-semibold bg-[#15202b] px-2 py-1 rounded-full border border-[#38444d]">
          {index + 1}/{totalTweets}
        </span>
        
        <div className="flex items-center space-x-2">
          {!isEditing ? (
            <>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsEditing(true)}
                className="text-[#8899ac] hover:text-white hover:bg-[#1d2d3a] p-2 h-8 w-8"
              >
                <Edit3 className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCopy}
                className={cn(
                  "text-[#8899ac] hover:text-white hover:bg-[#1d2d3a] p-2 h-8 w-8",
                  copied && "text-green-400"
                )}
              >
                {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              </Button>
            </>
          ) : (
            <>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleSave}
                disabled={isOverLimit}
                className="text-green-400 hover:text-green-300 hover:bg-[#1d2d3a] p-2 h-8 w-8"
              >
                <Check className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCancel}
                className="text-red-400 hover:text-red-300 hover:bg-[#1d2d3a] p-2 h-8 w-8"
              >
                <X className="h-4 w-4" />
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Tweet Content */}
      <div className="mb-4">
        {isEditing ? (
          <div>
            <textarea
              ref={textareaRef}
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
              className={cn(
                'w-full text-white leading-relaxed min-h-[80px] p-3 rounded-lg',
                'bg-[#000000] border border-[#38444d]',
                'focus:outline-none focus:ring-2 focus:ring-[#1d9bf0] focus:border-transparent',
                'transition-all duration-200 resize-none',
                'placeholder:text-[#8899ac]'
              )}
              placeholder="Enter your tweet text..."
            />
            <div className="flex justify-between items-center mt-2">
              <div className={cn(
                "text-sm",
                isOverLimit ? 'text-red-400' : 'text-[#8899ac]'
              )}>
                <span className={characterCount > 260 ? 'font-bold' : ''}>
                  {characterCount}/280
                </span>
              </div>
              {isOverLimit && (
                <span className="text-red-400 text-xs">
                  {characterCount - 280} characters over limit
                </span>
              )}
            </div>
          </div>
        ) : (
          /* Tweet Preview */
          <div className="relative bg-[#000000] rounded-xl p-4 border border-[#38444d]">
            {/* Twitter Header */}
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-10 h-10 bg-[#1d9bf0] rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-sm">T</span>
              </div>
              <div>
                <div className="flex items-center space-x-1">
                  <span className="text-white font-bold text-sm">Threadr</span>
                  <div className="w-4 h-4 bg-[#1d9bf0] rounded-full flex items-center justify-center">
                    <Check className="w-2.5 h-2.5 text-white" />
                  </div>
                </div>
                <span className="text-[#8899ac] text-sm">@threadr</span>
              </div>
            </div>

            {/* Tweet Text */}
            <div className="text-white text-[15px] leading-5 mb-3 whitespace-pre-wrap break-words">
              {tweet.content}
            </div>

            {/* Tweet Actions */}
            <div className="flex items-center justify-between text-[#8899ac] max-w-md">
              <button className="flex items-center space-x-2 hover:text-[#1d9bf0] transition-colors">
                <MessageCircle className="w-5 h-5" />
                <span className="text-sm">42</span>
              </button>
              <button className="flex items-center space-x-2 hover:text-green-400 transition-colors">
                <Repeat2 className="w-5 h-5" />
                <span className="text-sm">128</span>
              </button>
              <button className="flex items-center space-x-2 hover:text-red-400 transition-colors">
                <Heart className="w-5 h-5" />
                <span className="text-sm">1.2K</span>
              </button>
              <button className="flex items-center space-x-2 hover:text-[#1d9bf0] transition-colors">
                <Share className="w-5 h-5" />
              </button>
            </div>

            {/* Character count indicator */}
            <div className="absolute top-2 right-2">
              <div className={cn(
                "text-xs px-2 py-1 rounded-full",
                tweet.content.length > 280 ? 'bg-red-500/20 text-red-400' :
                tweet.content.length > 260 ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-green-500/20 text-green-400'
              )}>
                {tweet.content.length}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};