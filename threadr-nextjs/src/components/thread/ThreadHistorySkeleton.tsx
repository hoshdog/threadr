'use client';

import React from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { cn } from '@/lib/utils';

interface ThreadHistorySkeletonProps {
  count?: number;
  className?: string;
}

export const ThreadHistorySkeleton: React.FC<ThreadHistorySkeletonProps> = ({
  count = 3,
  className,
}) => {
  return (
    <div className={cn('space-y-4 sm:space-y-6', className)}>
      {Array.from({ length: count }).map((_, index) => (
        <Card key={index} className="animate-pulse">
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                {/* Title skeleton */}
                <div className="h-6 bg-muted rounded-md w-3/4 mb-3"></div>

                {/* Metadata skeleton */}
                <div className="flex flex-wrap items-center gap-3 mb-3">
                  <div className="h-4 bg-muted rounded w-20"></div>
                  <div className="h-4 bg-muted rounded w-16"></div>
                  <div className="h-4 bg-muted rounded w-24"></div>
                  <div className="h-5 bg-muted rounded-full w-16"></div>
                </div>

                {/* Preview text skeleton */}
                <div className="space-y-2 mb-3">
                  <div className="h-4 bg-muted rounded w-full"></div>
                  <div className="h-4 bg-muted rounded w-2/3"></div>
                </div>

                {/* Stats skeleton */}
                <div className="flex items-center gap-4">
                  <div className="h-3 bg-muted rounded w-12"></div>
                  <div className="h-3 bg-muted rounded w-14"></div>
                  <div className="h-3 bg-muted rounded w-16"></div>
                </div>
              </div>

              {/* Action buttons skeleton */}
              <div className="flex items-center gap-1">
                <div className="h-8 w-8 bg-muted rounded"></div>
                <div className="h-8 w-8 bg-muted rounded"></div>
                <div className="h-8 w-8 bg-muted rounded"></div>
              </div>
            </div>
          </CardHeader>
        </Card>
      ))}
    </div>
  );
};

interface ThreadHistoryFilterSkeletonProps {
  className?: string;
}

export const ThreadHistoryFilterSkeleton: React.FC<ThreadHistoryFilterSkeletonProps> = ({
  className,
}) => {
  return (
    <Card className={cn('animate-pulse', className)}>
      <CardContent className="p-4">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search input skeleton */}
          <div className="flex-1">
            <div className="h-10 bg-muted rounded-lg"></div>
          </div>

          {/* Filter buttons skeleton */}
          <div className="flex items-center gap-2 flex-wrap">
            <div className="h-8 w-24 bg-muted rounded"></div>
            <div className="h-8 w-20 bg-muted rounded"></div>
            <div className="h-8 w-20 bg-muted rounded"></div>
            <div className="h-8 w-16 bg-muted rounded"></div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

interface ThreadHistoryStatsSkeletonProps {
  className?: string;
}

export const ThreadHistoryStatsSkeleton: React.FC<ThreadHistoryStatsSkeletonProps> = ({
  className,
}) => {
  return (
    <div className={cn('grid grid-cols-2 sm:grid-cols-4 gap-4 animate-pulse', className)}>
      {Array.from({ length: 4 }).map((_, index) => (
        <div key={index} className="bg-background border border-border rounded-lg p-4">
          <div className="h-8 bg-muted rounded w-12 mb-2"></div>
          <div className="h-4 bg-muted rounded w-20"></div>
        </div>
      ))}
    </div>
  );
};

interface ThreadHistoryPageSkeletonProps {
  className?: string;
}

export const ThreadHistoryPageSkeleton: React.FC<ThreadHistoryPageSkeletonProps> = ({
  className,
}) => {
  return (
    <div className={cn('space-y-6', className)}>
      {/* Header skeleton */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="animate-pulse">
          <div className="h-8 bg-muted rounded w-48 mb-2"></div>
          <div className="h-4 bg-muted rounded w-64"></div>
        </div>

        <div className="flex items-center gap-3 animate-pulse">
          <div className="h-8 w-20 bg-muted rounded"></div>
          <div className="h-8 w-28 bg-muted rounded"></div>
        </div>
      </div>

      {/* Stats skeleton */}
      <ThreadHistoryStatsSkeleton />

      {/* Filters skeleton */}
      <ThreadHistoryFilterSkeleton />

      {/* Content skeleton */}
      <ThreadHistorySkeleton count={5} />

      {/* Pagination skeleton */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-6 border-t border-border animate-pulse">
        <div className="h-4 bg-muted rounded w-32"></div>
        
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 bg-muted rounded"></div>
          <div className="h-8 w-20 bg-muted rounded"></div>
          <div className="hidden sm:flex items-center gap-1">
            {Array.from({ length: 5 }).map((_, index) => (
              <div key={index} className="h-8 w-8 bg-muted rounded"></div>
            ))}
          </div>
          <div className="h-8 w-16 bg-muted rounded"></div>
          <div className="h-8 w-8 bg-muted rounded"></div>
        </div>
      </div>
    </div>
  );
};