'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface CharacterCounterProps {
  count: number;
  maxCount?: number;
  showProgress?: boolean;
  className?: string;
}

const CharacterCounter: React.FC<CharacterCounterProps> = ({
  count,
  maxCount = 280,
  showProgress = true,
  className,
}) => {
  const percentage = (count / maxCount) * 100;
  const isNearLimit = percentage >= 85;
  const isOverLimit = count > maxCount;
  
  // Calculate progress circle properties
  const radius = 8;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (Math.min(percentage, 100) / 100) * circumference;

  return (
    <div className={cn("flex items-center gap-2", className)}>
      {showProgress && (
        <div className="relative w-5 h-5">
          {/* Background circle */}
          <svg 
            className="w-5 h-5 transform -rotate-90" 
            viewBox="0 0 20 20"
          >
            <circle
              cx="10"
              cy="10"
              r={radius}
              stroke="currentColor"
              strokeWidth="2"
              fill="none"
              className="text-twitter-border dark:text-twitter-border"
            />
            {/* Progress circle */}
            <circle
              cx="10"
              cy="10"
              r={radius}
              stroke="currentColor"
              strokeWidth="2"
              fill="none"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className={cn(
                "transition-all duration-300 ease-in-out",
                isOverLimit
                  ? "text-red-500"
                  : isNearLimit
                  ? "text-amber-500"
                  : "text-twitter-blue"
              )}
            />
          </svg>
          
          {/* Show number when near or over limit */}
          {isNearLimit && (
            <div className="absolute inset-0 flex items-center justify-center">
              <span 
                className={cn(
                  "text-xs font-medium",
                  isOverLimit ? "text-red-500" : "text-amber-600"
                )}
              >
                {maxCount - count}
              </span>
            </div>
          )}
        </div>
      )}
      
      <span 
        className={cn(
          "text-sm font-medium transition-colors",
          isOverLimit
            ? "text-red-500"
            : isNearLimit
            ? "text-amber-600"
            : "text-twitter-gray dark:text-twitter-gray"
        )}
      >
        <span>{count}</span>
        <span className="text-twitter-gray dark:text-twitter-gray">/{maxCount}</span>
      </span>
    </div>
  );
};

export default CharacterCounter;