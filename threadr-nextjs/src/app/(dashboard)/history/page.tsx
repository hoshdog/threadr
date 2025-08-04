'use client';

import React, { useState, useMemo } from 'react';
import { useDebounce } from '@/hooks/useDebounce';
import { useThreads, useDeleteThread } from '@/hooks/api/useThreads';
import { ThreadHistoryList } from '@/components/thread/ThreadHistoryList';
import { ThreadHistoryFilters } from '@/components/thread/ThreadHistoryFilters';
import { ThreadHistoryEmpty } from '@/components/thread/ThreadHistoryEmpty';
import { 
  ThreadHistorySkeleton, 
  ThreadHistoryFilterSkeleton, 
  ThreadHistoryStatsSkeleton 
} from '@/components/thread/ThreadHistorySkeleton';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { Button } from '@/components/ui/Button';
import { RefreshCw, Plus, Archive, Star } from 'lucide-react';

export type DateFilter = 'all' | 'today' | 'week' | 'month';
export type StatusFilter = 'all' | 'draft' | 'published' | 'archived';
export type SortOption = 'newest' | 'oldest' | 'title' | 'most_tweets';

export interface HistoryFilters {
  search: string;
  dateFilter: DateFilter;
  statusFilter: StatusFilter;
  sortBy: SortOption;
  showFavorites: boolean;
}

export default function HistoryPage() {
  // Filter state
  const [filters, setFilters] = useState<HistoryFilters>({
    search: '',
    dateFilter: 'all',
    statusFilter: 'all',
    sortBy: 'newest',
    showFavorites: false,
  });

  // Pagination state
  const [page, setPage] = useState(1);
  const [limit] = useState(20);

  // Debounce search query to avoid excessive API calls
  const debouncedSearch = useDebounce(filters.search, 300);

  // Compute API parameters from filters
  const apiParams = useMemo(() => {
    const params: any = {
      page,
      limit,
    };

    // Add search if present
    if (debouncedSearch.trim()) {
      params.search_query = debouncedSearch.trim();
    }

    // Add date filtering
    if (filters.dateFilter !== 'all') {
      const now = new Date();
      let dateFrom: Date;

      switch (filters.dateFilter) {
        case 'today':
          dateFrom = new Date(now.getFullYear(), now.getMonth(), now.getDate());
          break;
        case 'week':
          dateFrom = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          break;
        case 'month':
          dateFrom = new Date(now.getFullYear(), now.getMonth(), 1);
          break;
        default:
          dateFrom = new Date(0);
      }

      params.date_from = dateFrom.toISOString();
    }

    // Add status filtering
    if (filters.statusFilter !== 'all') {
      params.status = filters.statusFilter;
    }

    // Add favorites filtering
    if (filters.showFavorites) {
      params.is_favorite = true;
    }

    // Add sorting
    switch (filters.sortBy) {
      case 'newest':
        params.sort_by = 'created_at';
        params.sort_order = 'desc';
        break;
      case 'oldest':
        params.sort_by = 'created_at';
        params.sort_order = 'asc';
        break;
      case 'title':
        params.sort_by = 'title';
        params.sort_order = 'asc';
        break;
      case 'most_tweets':
        params.sort_by = 'tweet_count';
        params.sort_order = 'desc';
        break;
    }

    return params;
  }, [debouncedSearch, filters, page, limit]);

  // Fetch threads with current filters
  const { data: threadsData, isLoading, error, refetch, isRefetching } = useThreads(apiParams);
  const deleteThreadMutation = useDeleteThread();

  // Handle filter changes
  const handleFiltersChange = (newFilters: Partial<HistoryFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    setPage(1); // Reset to first page when filters change
  };

  // Handle refresh
  const handleRefresh = () => {
    refetch();
  };

  // Handle delete thread
  const handleDeleteThread = async (threadId: string) => {
    if (window.confirm('Are you sure you want to delete this thread? This action cannot be undone.')) {
      try {
        await deleteThreadMutation.mutateAsync(threadId);
      } catch (error) {
        console.error('Failed to delete thread:', error);
        alert('Failed to delete thread. Please try again.');
      }
    }
  };

  // Handle page navigation
  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  // Get stats for display
  const stats = useMemo(() => {
    if (!threadsData) return null;

    return {
      total: threadsData.total || 0,
      showing: threadsData.data?.length || 0,
      hasMore: threadsData.has_next || false,
      page: threadsData.page || 1,
      totalPages: Math.ceil((threadsData.total || 0) / limit),
    };
  }, [threadsData, limit]);

  // Quick stats for header
  const quickStats = useMemo(() => {
    const threads = threadsData?.data || [];
    const totalTweets = threads.reduce((acc, thread) => acc + (thread.tweets?.length || 0), 0);
    const drafts = 0; // Status filtering not supported by current Thread interface
    const published = threads.length; // All threads are considered published

    return {
      totalThreads: stats?.total || 0,
      totalTweets,
      drafts,
      published,
    };
  }, [threadsData, stats]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Thread History</h1>
          <p className="text-muted-foreground">
            Manage and organize your saved threads
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefetching}
            className="flex items-center gap-2"
          >
            <RefreshCw className={`h-4 w-4 ${isRefetching ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          
          <Button
            size="sm"
            onClick={() => window.location.href = '/dashboard/generate'}
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            New Thread
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      {isLoading ? (
        <ThreadHistoryStatsSkeleton />
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-background border border-border rounded-lg p-4">
            <div className="text-2xl font-bold text-foreground">{quickStats.totalThreads}</div>
            <div className="text-sm text-muted-foreground">Total Threads</div>
          </div>
          <div className="bg-background border border-border rounded-lg p-4">
            <div className="text-2xl font-bold text-foreground">{quickStats.totalTweets}</div>
            <div className="text-sm text-muted-foreground">Total Tweets</div>
          </div>
          <div className="bg-background border border-border rounded-lg p-4">
            <div className="text-2xl font-bold text-green-600">{quickStats.published}</div>
            <div className="text-sm text-muted-foreground">Published</div>
          </div>
          <div className="bg-background border border-border rounded-lg p-4">
            <div className="text-2xl font-bold text-yellow-600">{quickStats.drafts}</div>
            <div className="text-sm text-muted-foreground">Drafts</div>
          </div>
        </div>
      )}

      {/* Filters */}
      {isLoading ? (
        <ThreadHistoryFilterSkeleton />
      ) : (
        <ThreadHistoryFilters
          filters={filters}
          onFiltersChange={handleFiltersChange}
          resultsCount={stats?.total || 0}
          isLoading={isLoading}
        />
      )}

      {/* Content */}
      <div className="min-h-[400px]">
        {error ? (
          <div className="flex flex-col items-center justify-center py-12 space-y-4">
            <div className="text-destructive text-center">
              <h3 className="text-lg font-semibold mb-2">Error Loading Threads</h3>
              <p className="text-sm text-muted-foreground mb-4">
                {error instanceof Error ? error.message : 'An unexpected error occurred'}
              </p>
              <Button onClick={handleRefresh} variant="secondary">
                Try Again
              </Button>
            </div>
          </div>
        ) : isLoading ? (
          <ThreadHistorySkeleton count={5} />
        ) : !threadsData?.data?.length ? (
          <ThreadHistoryEmpty
            hasFilters={Object.values(filters).some(val => 
              val !== '' && val !== 'all' && val !== 'newest' && val !== false
            )}
            onClearFilters={() => handleFiltersChange({
              search: '',
              dateFilter: 'all',
              statusFilter: 'all',
              sortBy: 'newest',
              showFavorites: false,
            })}
            onCreateThread={() => window.location.href = '/dashboard/generate'}
          />
        ) : (
          <ThreadHistoryList
            threads={threadsData.data}
            onDeleteThread={handleDeleteThread}
            isDeleting={deleteThreadMutation.isPending}
            pagination={{
              currentPage: stats?.page || 1,
              totalPages: stats?.totalPages || 1,
              hasNext: stats?.hasMore || false,
              hasPrevious: (stats?.page || 1) > 1,
              onPageChange: handlePageChange,
            }}
          />
        )}
      </div>

      {/* Floating Action Buttons for Mobile */}
      <div className="fixed bottom-6 right-6 sm:hidden flex flex-col gap-3">
        <Button
          size="sm"
          variant="secondary"
          onClick={handleRefresh}
          disabled={isRefetching}
          className="h-12 w-12 rounded-full shadow-lg"
        >
          <RefreshCw className={`h-5 w-5 ${isRefetching ? 'animate-spin' : ''}`} />
        </Button>
        <Button
          size="sm"
          onClick={() => window.location.href = '/dashboard/generate'}
          className="h-12 w-12 rounded-full shadow-lg"
        >
          <Plus className="h-5 w-5" />
        </Button>
      </div>
    </div>
  );
}