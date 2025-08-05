import { useMutation, useQuery, useQueryClient, useInfiniteQuery } from '@tanstack/react-query';
import { threadsApi } from '../threads';
import { 
  Thread, 
  GenerateThreadRequest, 
  GenerateThreadResponse, 
  UsageStats,
  PaginatedResponse 
} from '@/types';

// Query keys
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
} as const;

// Get paginated threads
export function useThreads(page = 1, limit = 10) {
  return useQuery({
    queryKey: threadKeys.list({ page, limit }),
    queryFn: () => threadsApi.getThreads(page, limit),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

// Get infinite threads (for infinite scroll)
export function useInfiniteThreads(limit = 10) {
  return useInfiniteQuery({
    queryKey: threadKeys.lists(),
    queryFn: ({ pageParam = 1 }) => threadsApi.getThreads(pageParam, limit),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      const { page, total_pages } = lastPage;
      return page < total_pages ? page + 1 : undefined;
    },
    staleTime: 2 * 60 * 1000,
  });
}

// Get specific thread
export function useThread(threadId: string, enabled = true) {
  return useQuery({
    queryKey: threadKeys.detail(threadId),
    queryFn: () => threadsApi.getThread(threadId),
    enabled: !!threadId && enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Generate thread mutation
export function useGenerateThread() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (request: GenerateThreadRequest) => threadsApi.generateThread(request),
    onSuccess: () => {
      // Invalidate usage stats and threads list
      queryClient.invalidateQueries({ queryKey: threadKeys.usage() });
      queryClient.invalidateQueries({ queryKey: threadKeys.lists() });
    },
  });
}

// Save thread mutation
export function useSaveThread() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (thread: Omit<Thread, 'id' | 'createdAt' | 'updatedAt'>) => 
      threadsApi.saveThread(thread),
    onSuccess: (newThread: Thread) => {
      // Add to threads list cache
      queryClient.setQueryData(threadKeys.detail(newThread.id), newThread);
      
      // Invalidate threads list to refetch
      queryClient.invalidateQueries({ queryKey: threadKeys.lists() });
    },
  });
}

// Update thread mutation
export function useUpdateThread(threadId: string) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (updates: Partial<Thread>) => threadsApi.updateThread(threadId, updates),
    onSuccess: (updatedThread: Thread) => {
      // Update thread in cache
      queryClient.setQueryData(threadKeys.detail(threadId), updatedThread);
      
      // Invalidate threads list to show changes
      queryClient.invalidateQueries({ queryKey: threadKeys.lists() });
    },
  });
}

// Delete thread mutation
export function useDeleteThread() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (threadId: string) => threadsApi.deleteThread(threadId),
    onSuccess: (_, threadId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: threadKeys.detail(threadId) });
      
      // Invalidate threads list
      queryClient.invalidateQueries({ queryKey: threadKeys.lists() });
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
  });
}

// Get usage statistics
export function useUsageStats() {
  return useQuery({
    queryKey: threadKeys.usage(),
    queryFn: threadsApi.getUsageStats,
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Refetch every minute
  });
}

// Get premium status
export function usePremiumStatus() {
  return useQuery({
    queryKey: threadKeys.premium(),
    queryFn: threadsApi.getPremiumStatus,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Capture email mutation
export function useCaptureEmail() {
  return useMutation({
    mutationFn: (email: string) => threadsApi.captureEmail(email),
  });
}

// Search threads
export function useSearchThreads(query: string, page = 1, limit = 10, enabled = true) {
  return useQuery({
    queryKey: threadKeys.search(query),
    queryFn: () => threadsApi.searchThreads(query, page, limit),
    enabled: !!query && query.length > 2 && enabled,
    staleTime: 2 * 60 * 1000,
  });
}

// Get threads by tag
export function useThreadsByTag(tag: string, page = 1, limit = 10, enabled = true) {
  return useQuery({
    queryKey: threadKeys.taggedThreads(tag),
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