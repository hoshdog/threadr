import { useMutation, useQuery, useQueryClient, useInfiniteQuery } from '@tanstack/react-query';
import { threadsApi } from '@/lib/api/threads';
import { 
  Thread, 
  UsageStats,
  Tweet
} from '@/types';
import { PaginatedResponse, SavedThread, GenerateThreadRequest, GenerateThreadResponse } from '@/types/api';

// Query keys for thread-related data
export const threadKeys = {
  all: ['threads'] as const,
  lists: () => [...threadKeys.all, 'list'] as const,
  list: (filters: Record<string, any>) => [...threadKeys.lists(), { filters }] as const,
  details: () => [...threadKeys.all, 'detail'] as const,
  detail: (id: string) => [...threadKeys.details(), id] as const,
  usage: () => [...threadKeys.all, 'usage'] as const,
  premium: () => [...threadKeys.all, 'premium'] as const,
  search: (query: string) => [...threadKeys.all, 'search', query] as const,
  tags: () => [...threadKeys.all, 'tags'] as const,
  taggedThreads: (tag: string) => [...threadKeys.all, 'tag', tag] as const,
  drafts: () => [...threadKeys.all, 'drafts'] as const,
  published: () => [...threadKeys.all, 'published'] as const,
  favorites: () => [...threadKeys.all, 'favorites'] as const,
  recent: () => [...threadKeys.all, 'recent'] as const,
  analytics: (id: string) => [...threadKeys.all, 'analytics', id] as const,
} as const;

// Get paginated threads with various filters
export function useThreads(params?: {
  page?: number;
  limit?: number;
  status?: 'draft' | 'published' | 'archived';
  sortBy?: 'createdAt' | 'updatedAt' | 'title';
  sortOrder?: 'asc' | 'desc';
  tags?: string[];
}) {
  const { page = 1, limit = 10, ...filters } = params || {};
  
  return useQuery({
    queryKey: threadKeys.list({ page, limit, ...filters }),
    queryFn: () => threadsApi.getThreads(page, limit, filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
    placeholderData: { data: [], total: 0, page: 1, page_size: 10, total_pages: 0, has_next: false, has_previous: false },
  });
}

// Get infinite threads (for infinite scroll)
export function useInfiniteThreads(params?: {
  limit?: number;
  status?: 'draft' | 'published' | 'archived';
  sortBy?: 'createdAt' | 'updatedAt' | 'title';
  sortOrder?: 'asc' | 'desc';
  tags?: string[];
}) {
  const { limit = 10, ...filters } = params || {};
  
  return useInfiniteQuery<PaginatedResponse<SavedThread>, Error, PaginatedResponse<SavedThread>, readonly ["threads", "list"], number>({
    queryKey: threadKeys.lists(),
    queryFn: ({ pageParam = 1 }) => threadsApi.getThreads(pageParam, limit, filters),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      const { page, total_pages } = lastPage;
      return page < total_pages ? page + 1 : undefined;
    },
    staleTime: 2 * 60 * 1000,
    placeholderData: {
      pages: [],
      pageParams: [],
    },
  });
}

// Get specific thread with optimistic loading
export function useThread(threadId: string, enabled = true) {
  return useQuery({
    queryKey: threadKeys.detail(threadId),
    queryFn: () => threadsApi.getThread(threadId),
    enabled: !!threadId && enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: (failureCount, error: any) => {
      // Don't retry on 404 (thread not found)
      if (error?.status === 404) return false;
      return failureCount < 3;
    },
  });
}

// Generate thread mutation with optimistic updates for usage
export function useGenerateThread() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (request: GenerateThreadRequest) => threadsApi.generateThread(request),
    onMutate: async () => {
      // Optimistically update usage stats
      const currentUsage = queryClient.getQueryData<UsageStats>(threadKeys.usage());
      if (currentUsage) {
        queryClient.setQueryData<UsageStats>(threadKeys.usage(), {
          ...currentUsage,
          dailyUsage: currentUsage.dailyUsage + 1,
          monthlyUsage: currentUsage.monthlyUsage + 1,
          canGenerate: currentUsage.dailyUsage + 1 < currentUsage.dailyLimit,
        });
      }
    },
    onSuccess: (data, variables) => {
      // Invalidate usage stats and threads list
      queryClient.invalidateQueries({ queryKey: threadKeys.usage() });
      queryClient.invalidateQueries({ queryKey: threadKeys.lists() });
      
      // If thread was saved, add to cache
      if (data.saved_thread_id) {
        queryClient.invalidateQueries({ queryKey: threadKeys.detail(data.saved_thread_id) });
      }
    },
    onError: (error, variables, context) => {
      // Rollback optimistic updates
      queryClient.invalidateQueries({ queryKey: threadKeys.usage() });
      console.error('Thread generation failed:', error);
    },
  });
}

// Save thread mutation with optimistic updates
export function useSaveThread() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (thread: Omit<Thread, 'id' | 'createdAt' | 'updatedAt'>) => 
      threadsApi.saveThread(thread),
    onMutate: async (newThread) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: threadKeys.lists() });
      
      // Create optimistic thread
      const optimisticThread: Thread = {
        ...newThread,
        id: `temp-${Date.now()}`,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      
      // Optimistically add to threads list
      const previousThreads = queryClient.getQueryData<PaginatedResponse<Thread>>(
        threadKeys.list({ page: 1, limit: 10 })
      );
      
      if (previousThreads) {
        queryClient.setQueryData<PaginatedResponse<Thread>>(
          threadKeys.list({ page: 1, limit: 10 }),
          {
            ...previousThreads,
            data: [optimisticThread, ...previousThreads.data],
            total: previousThreads.total + 1,
          }
        );
      }
      
      return { previousThreads, optimisticThread };
    },
    onSuccess: (newThread: Thread, variables, context) => {
      // Update optimistic thread with real data
      if (context?.optimisticThread) {
        queryClient.setQueryData(threadKeys.detail(newThread.id), newThread);
        
        // Remove optimistic thread and add real one
        const currentThreads = queryClient.getQueryData<PaginatedResponse<Thread>>(
          threadKeys.list({ page: 1, limit: 10 })
        );
        
        if (currentThreads) {
          queryClient.setQueryData<PaginatedResponse<Thread>>(
            threadKeys.list({ page: 1, limit: 10 }),
            {
              ...currentThreads,
              data: currentThreads.data.map(t => 
                t.id === context.optimisticThread.id ? newThread : t
              ),
            }
          );
        }
      }
      
      // Invalidate threads list to refetch with updated data
      queryClient.invalidateQueries({ queryKey: threadKeys.lists() });
    },
    onError: (error, variables, context) => {
      // Rollback optimistic updates
      if (context?.previousThreads) {
        queryClient.setQueryData(
          threadKeys.list({ page: 1, limit: 10 }),
          context.previousThreads
        );
      }
      console.error('Save thread failed:', error);
    },
  });
}

// Update thread mutation with optimistic updates
export function useUpdateThread(threadId: string) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (updates: Partial<Thread>) => threadsApi.updateThread(threadId, updates),
    onMutate: async (newData) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: threadKeys.detail(threadId) });
      
      // Snapshot the previous value
      const previousThread = queryClient.getQueryData<Thread>(threadKeys.detail(threadId));
      
      // Optimistically update to the new value
      if (previousThread) {
        queryClient.setQueryData<Thread>(threadKeys.detail(threadId), {
          ...previousThread,
          ...newData,
          updatedAt: new Date().toISOString(),
        });
      }
      
      return { previousThread };
    },
    onSuccess: (updatedThread: Thread) => {
      // Update thread in cache
      queryClient.setQueryData(threadKeys.detail(threadId), updatedThread);
      
      // Invalidate threads list to show changes
      queryClient.invalidateQueries({ queryKey: threadKeys.lists() });
    },
    onError: (error, newData, context) => {
      // Rollback optimistic updates
      if (context?.previousThread) {
        queryClient.setQueryData(threadKeys.detail(threadId), context.previousThread);
      }
      console.error('Update thread failed:', error);
    },
  });
}

// Delete thread mutation with optimistic updates
export function useDeleteThread() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (threadId: string) => threadsApi.deleteThread(threadId),
    onMutate: async (threadId) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: threadKeys.lists() });
      
      // Remove from threads list optimistically
      const listsToUpdate = queryClient.getQueriesData({ queryKey: threadKeys.lists() });
      const updates: Array<{ queryKey: any; previousData: any }> = [];
      
      listsToUpdate.forEach(([queryKey, data]) => {
        if (data && typeof data === 'object' && 'data' in data) {
          const paginatedData = data as PaginatedResponse<Thread>;
          const filteredData = {
            ...paginatedData,
            data: paginatedData.data.filter(thread => thread.id !== threadId),
            total: paginatedData.total - 1,
          };
          
          queryClient.setQueryData(queryKey, filteredData);
          updates.push({ queryKey, previousData: data });
        }
      });
      
      return { updates };
    },
    onSuccess: (_, threadId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: threadKeys.detail(threadId) });
      
      // Invalidate threads list
      queryClient.invalidateQueries({ queryKey: threadKeys.lists() });
    },
    onError: (error, threadId, context) => {
      // Rollback optimistic updates
      context?.updates.forEach(({ queryKey, previousData }) => {
        queryClient.setQueryData(queryKey, previousData);
      });
      console.error('Delete thread failed:', error);
    },
  });
}

// Duplicate thread mutation
export function useDuplicateThread() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (threadId: string) => threadsApi.duplicateThread(threadId),
    onSuccess: (newThread: Thread) => {
      // Add to cache
      queryClient.setQueryData(threadKeys.detail(newThread.id), newThread);
      
      // Invalidate threads list
      queryClient.invalidateQueries({ queryKey: threadKeys.lists() });
    },
    onError: (error) => {
      console.error('Duplicate thread failed:', error);
    },
  });
}

// Get usage statistics with real-time updates
export function useThreadUsageStats() {
  return useQuery({
    queryKey: threadKeys.usage(),
    queryFn: threadsApi.getUsageStats,
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Refetch every minute
    retry: 3,
  });
}

// Get premium status
export function useThreadPremiumStatus() {
  return useQuery({
    queryKey: threadKeys.premium(),
    queryFn: threadsApi.getPremiumStatus,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 3,
  });
}

// Capture email mutation
export function useCaptureEmail() {
  return useMutation({
    mutationFn: (email: string) => threadsApi.captureEmail(email),
    onError: (error) => {
      console.error('Email capture failed:', error);
    },
  });
}

// Search threads with debounced query
export function useSearchThreads(query: string, params?: {
  page?: number;
  limit?: number;
  filters?: Record<string, any>;
}, enabled = true) {
  const { page = 1, limit = 10, filters = {} } = params || {};
  
  return useQuery({
    queryKey: threadKeys.search(`${query}-${JSON.stringify({ page, limit, filters })}`),
    queryFn: () => threadsApi.searchThreads(query, page, limit, filters),
    enabled: !!query && query.length > 2 && enabled,
    staleTime: 2 * 60 * 1000,
    placeholderData: { data: [], total: 0, page: 1, page_size: 10, total_pages: 0, has_next: false, has_previous: false },
  });
}

// Get threads by tag
export function useThreadsByTag(tag: string, page = 1, limit = 10, enabled = true) {
  return useQuery({
    queryKey: threadKeys.taggedThreads(`${tag}-${page}-${limit}`),
    queryFn: () => threadsApi.getThreadsByTag(tag, page, limit),
    enabled: !!tag && enabled,
    staleTime: 2 * 60 * 1000,
  });
}

// Get popular tags
export function usePopularTags() {
  return useQuery({
    queryKey: threadKeys.tags(),
    queryFn: threadsApi.getPopularTags,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Get draft threads
export function useDraftThreads(page = 1, limit = 10) {
  return useQuery({
    queryKey: threadKeys.drafts(),
    queryFn: () => threadsApi.getThreads(page, limit, { status: 'draft' }),
    staleTime: 1 * 60 * 1000, // 1 minute (drafts change frequently)
  });
}

// Get published threads
export function usePublishedThreads(page = 1, limit = 10) {
  return useQuery({
    queryKey: threadKeys.published(),
    queryFn: () => threadsApi.getThreads(page, limit, { status: 'published' }),
    staleTime: 5 * 60 * 1000,
  });
}

// Get favorite threads
export function useFavoriteThreads(page = 1, limit = 10) {
  return useQuery({
    queryKey: threadKeys.favorites(),
    queryFn: () => threadsApi.getFavoriteThreads(page, limit),
    staleTime: 2 * 60 * 1000,
  });
}

// Toggle favorite thread
export function useToggleFavorite() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (threadId: string) => threadsApi.toggleFavorite(threadId),
    onSuccess: (_, threadId) => {
      // Invalidate favorites list
      queryClient.invalidateQueries({ queryKey: threadKeys.favorites() });
      
      // Invalidate thread detail to update favorite status
      queryClient.invalidateQueries({ queryKey: threadKeys.detail(threadId) });
      
      // Invalidate threads list to update favorite status
      queryClient.invalidateQueries({ queryKey: threadKeys.lists() });
    },
    onError: (error) => {
      console.error('Toggle favorite failed:', error);
    },
  });
}

// Get recent threads
export function useRecentThreads(limit = 5) {
  return useQuery({
    queryKey: threadKeys.recent(),
    queryFn: () => threadsApi.getThreads(1, limit, { sortBy: 'updatedAt', sortOrder: 'desc' }),
    staleTime: 2 * 60 * 1000,
  });
}

// Get thread analytics
export function useThreadAnalytics(threadId: string, enabled = true) {
  return useQuery({
    queryKey: threadKeys.analytics(threadId),
    queryFn: () => threadsApi.getThreadAnalytics(threadId),
    enabled: !!threadId && enabled,
    staleTime: 5 * 60 * 1000,
  });
}

// Prefetch thread (for optimization)
export function usePrefetchThread() {
  const queryClient = useQueryClient();
  
  return (threadId: string) => {
    queryClient.prefetchQuery({
      queryKey: threadKeys.detail(threadId),
      queryFn: () => threadsApi.getThread(threadId),
      staleTime: 5 * 60 * 1000,
    });
  };
}

// Batch operations for multiple threads
export function useBatchDeleteThreads() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (threadIds: string[]) => threadsApi.batchDeleteThreads(threadIds),
    onSuccess: (_, threadIds) => {
      // Remove all deleted threads from cache
      threadIds.forEach(id => {
        queryClient.removeQueries({ queryKey: threadKeys.detail(id) });
      });
      
      // Invalidate all thread lists
      queryClient.invalidateQueries({ queryKey: threadKeys.lists() });
    },
    onError: (error) => {
      console.error('Batch delete failed:', error);
    },
  });
}

// Export threads
export function useExportThreads() {
  return useMutation({
    mutationFn: (params: { threadIds?: string[]; format: 'json' | 'csv' | 'txt' }) =>
      threadsApi.exportThreads(params),
    onSuccess: (blob, params) => {
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `threads-export.${params.format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    },
    onError: (error) => {
      console.error('Export failed:', error);
    },
  });
}

// Combined hook for thread management dashboard
export function useThreadsDashboard() {
  const threads = useThreads({ limit: 10, sortBy: 'updatedAt', sortOrder: 'desc' });
  const drafts = useDraftThreads(1, 5);
  const favorites = useFavoriteThreads(1, 5);
  const usage = useThreadUsageStats();
  const tags = usePopularTags();
  
  return {
    threads,
    drafts,
    favorites,
    usage,
    tags,
    isLoading: threads.isLoading || drafts.isLoading || favorites.isLoading || usage.isLoading,
    isError: threads.isError || drafts.isError || favorites.isError || usage.isError,
    error: threads.error || drafts.error || favorites.error || usage.error,
  };
}

// Hook for checking if user can generate more threads
export function useCanGenerateThread() {
  const { data: usage } = useThreadUsageStats();
  const { data: premiumStatus } = useThreadPremiumStatus();
  
  return {
    canGenerate: usage?.canGenerate || premiumStatus?.isPremium || false,
    remainingToday: usage ? Math.max(0, usage.dailyLimit - usage.dailyUsage) : 0,
    remainingThisMonth: usage ? Math.max(0, usage.monthlyLimit - usage.monthlyUsage) : 0,
    isPremium: premiumStatus?.isPremium || false,
    usage,
  };
}