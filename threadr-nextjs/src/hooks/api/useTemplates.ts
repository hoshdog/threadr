import { useMutation, useQuery, useQueryClient, useInfiniteQuery } from '@tanstack/react-query';
import { templatesApi, Template, TemplateCategory } from '@/lib/api/templates';
import { PaginatedResponse } from '@/types';

// Additional types for templates
export interface CreateTemplateRequest {
  name: string;
  description: string;
  category: string;
  prompt: string;
  tags: string[];
  isPublic?: boolean;
  isPremium?: boolean;
  previewTweets?: string[];
}

export interface GenerateFromTemplateRequest {
  templateId: string;
  content?: string;
  variables?: Record<string, string>;
  customPrompt?: string;
}

export interface TemplateStats {
  id: string;
  usage: number;
  rating: number;
  totalRatings: number;
  createdAt: string;
  lastUsed?: string;
}

// Query keys for template-related data
export const templateKeys = {
  all: ['templates'] as const,
  lists: () => [...templateKeys.all, 'list'] as const,
  list: (filters: Record<string, any>) => [...templateKeys.lists(), { filters }] as const,
  details: () => [...templateKeys.all, 'detail'] as const,
  detail: (id: string) => [...templateKeys.details(), id] as const,
  categories: () => [...templateKeys.all, 'categories'] as const,
  category: (id: string) => [...templateKeys.all, 'category', id] as const,
  popular: () => [...templateKeys.all, 'popular'] as const,
  featured: () => [...templateKeys.all, 'featured'] as const,
  trending: () => [...templateKeys.all, 'trending'] as const,
  user: () => [...templateKeys.all, 'user'] as const,
  favorites: () => [...templateKeys.all, 'favorites'] as const,
  recent: () => [...templateKeys.all, 'recent'] as const,
  search: (query: string) => [...templateKeys.all, 'search', query] as const,
  categoryTemplates: (categoryId: string) => [...templateKeys.all, 'category', categoryId] as const,
  stats: (id: string) => [...templateKeys.all, 'stats', id] as const,
  suggestions: (content: string) => [...templateKeys.all, 'suggestions', content] as const,
  premium: () => [...templateKeys.all, 'premium'] as const,
  free: () => [...templateKeys.all, 'free'] as const,
} as const;

// Get templates with advanced filtering and sorting
export function useTemplates(params?: {
  category?: string;
  isPremium?: boolean;
  isPublic?: boolean;
  search?: string;
  tags?: string[];
  page?: number;
  limit?: number;
  sortBy?: 'name' | 'usage' | 'rating' | 'createdAt' | 'updatedAt';
  sortOrder?: 'asc' | 'desc';
}) {
  const { page = 1, limit = 12, ...filters } = params || {};
  
  return useQuery({
    queryKey: templateKeys.list({ page, limit, ...filters }),
    queryFn: () => templatesApi.getTemplates({ page, limit, ...filters }),
    staleTime: 5 * 60 * 1000, // 5 minutes
    placeholderData: { data: [], total: 0, page: 1, limit: 12, totalPages: 0 },
  });
}

// Get infinite templates (for infinite scroll)
export function useInfiniteTemplates(params?: {
  category?: string;
  isPremium?: boolean;
  isPublic?: boolean;
  search?: string;
  tags?: string[];
  limit?: number;
  sortBy?: 'name' | 'usage' | 'rating' | 'createdAt' | 'updatedAt';
  sortOrder?: 'asc' | 'desc';
}) {
  const { limit = 12, ...otherParams } = params || {};
  
  return useInfiniteQuery({
    queryKey: templateKeys.lists(),
    queryFn: ({ pageParam = 1 }) => 
      templatesApi.getTemplates({ ...otherParams, page: pageParam, limit }),
    initialPageParam: 1,
    getNextPageParam: (lastPage: any) => {
      // Handle both totalPages and total_pages property names
      const totalPages = lastPage.totalPages || lastPage.total_pages || 1;
      const page = lastPage.page || 1;
      return page < totalPages ? page + 1 : undefined;
    },
    staleTime: 5 * 60 * 1000,
    placeholderData: {
      pages: [],
      pageParams: [],
    },
  });
}

// Get specific template with related data
export function useTemplate(templateId: string, enabled = true) {
  return useQuery({
    queryKey: templateKeys.detail(templateId),
    queryFn: () => templatesApi.getTemplate(templateId),
    enabled: !!templateId && enabled,
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: (failureCount, error: any) => {
      // Don't retry on 404 (template not found)
      if (error?.status === 404) return false;
      return failureCount < 3;
    },
  });
}

// Get template categories with template counts
export function useTemplateCategories() {
  return useQuery({
    queryKey: templateKeys.categories(),
    queryFn: templatesApi.getCategories,
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
}

// Get popular templates
export function usePopularTemplates(limit = 10) {
  return useQuery({
    queryKey: templateKeys.popular(),
    queryFn: () => templatesApi.getPopularTemplates(limit),
    staleTime: 10 * 60 * 1000,
  });
}

// Get featured templates
export function useFeaturedTemplates() {
  return useQuery({
    queryKey: templateKeys.featured(),
    queryFn: templatesApi.getFeaturedTemplates,
    staleTime: 15 * 60 * 1000, // 15 minutes
  });
}

// Get trending templates
export function useTrendingTemplates(limit = 10) {
  return useQuery({
    queryKey: templateKeys.trending(),
    queryFn: () => templatesApi.getTrendingTemplates(limit),
    staleTime: 5 * 60 * 1000, // 5 minutes (trending changes frequently)
  });
}

// Get templates by category
export function useTemplatesByCategory(categoryId: string, params?: {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}, enabled = true) {
  const { page = 1, limit = 12, sortBy, sortOrder } = params || {};
  
  return useQuery({
    queryKey: templateKeys.categoryTemplates(`${categoryId}-${page}-${limit}-${sortBy}-${sortOrder}`),
    queryFn: () => templatesApi.getTemplatesByCategory(categoryId, page, limit, { sortBy, sortOrder }),
    enabled: !!categoryId && enabled,
    staleTime: 5 * 60 * 1000,
  });
}

// Generate thread from template with optimistic updates
export function useGenerateFromTemplate() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (request: GenerateFromTemplateRequest) => 
      templatesApi.generateFromTemplate(request),
    onMutate: async (variables) => {
      // Optimistically update template usage count
      const templateData = queryClient.getQueryData<Template>(
        templateKeys.detail(variables.templateId)
      );
      
      if (templateData) {
        queryClient.setQueryData<Template>(templateKeys.detail(variables.templateId), {
          ...templateData,
          usage: templateData.usage + 1,
        });
      }
      
      return { templateData };
    },
    onSuccess: (data, variables) => {
      // Invalidate template stats to update usage count
      queryClient.invalidateQueries({ 
        queryKey: templateKeys.stats(variables.templateId) 
      });
      
      // Invalidate popular templates as usage affects popularity
      queryClient.invalidateQueries({ queryKey: templateKeys.popular() });
      queryClient.invalidateQueries({ queryKey: templateKeys.trending() });
      
      // Invalidate template detail to get accurate usage
      queryClient.invalidateQueries({ 
        queryKey: templateKeys.detail(variables.templateId) 
      });
    },
    onError: (error, variables, context) => {
      // Rollback optimistic updates
      if (context?.templateData) {
        queryClient.setQueryData(
          templateKeys.detail(variables.templateId), 
          context.templateData
        );
      }
      console.error('Generate from template failed:', error);
    },
  });
}

// Create custom template
export function useCreateTemplate() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (templateData: CreateTemplateRequest) => 
      templatesApi.createTemplate(templateData),
    onSuccess: (newTemplate: Template) => {
      // Add to cache
      queryClient.setQueryData(templateKeys.detail(newTemplate.id), newTemplate);
      
      // Invalidate user templates list
      queryClient.invalidateQueries({ queryKey: templateKeys.user() });
      
      // Invalidate main templates list
      queryClient.invalidateQueries({ queryKey: templateKeys.lists() });
      
      // Invalidate category templates if categorized
      if (newTemplate.category) {
        queryClient.invalidateQueries({ 
          queryKey: templateKeys.categoryTemplates(newTemplate.category) 
        });
      }
    },
    onError: (error) => {
      console.error('Create template failed:', error);
    },
  });
}

// Update template with optimistic updates
export function useUpdateTemplate(templateId: string) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (updates: Partial<CreateTemplateRequest>) => 
      templatesApi.updateTemplate(templateId, updates),
    onMutate: async (newData) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: templateKeys.detail(templateId) });
      
      // Snapshot the previous value
      const previousTemplate = queryClient.getQueryData<Template>(templateKeys.detail(templateId));
      
      // Optimistically update
      if (previousTemplate) {
        queryClient.setQueryData<Template>(templateKeys.detail(templateId), {
          ...previousTemplate,
          ...newData,
          updatedAt: new Date().toISOString(),
        });
      }
      
      return { previousTemplate };
    },
    onSuccess: (updatedTemplate: Template) => {
      // Update in cache
      queryClient.setQueryData(templateKeys.detail(templateId), updatedTemplate);
      
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: templateKeys.user() });
      queryClient.invalidateQueries({ queryKey: templateKeys.lists() });
    },
    onError: (error, newData, context) => {
      // Rollback optimistic updates
      if (context?.previousTemplate) {
        queryClient.setQueryData(templateKeys.detail(templateId), context.previousTemplate);
      }
      console.error('Update template failed:', error);
    },
  });
}

// Delete template with optimistic updates
export function useDeleteTemplate() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (templateId: string) => templatesApi.deleteTemplate(templateId),
    onMutate: async (templateId) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: templateKeys.lists() });
      
      // Remove from all template lists optimistically
      const listsToUpdate = queryClient.getQueriesData({ queryKey: templateKeys.lists() });
      const updates: Array<{ queryKey: any; previousData: any }> = [];
      
      listsToUpdate.forEach(([queryKey, data]) => {
        if (data && typeof data === 'object' && 'data' in data) {
          const paginatedData = data as PaginatedResponse<Template>;
          const filteredData = {
            ...paginatedData,
            data: paginatedData.data.filter(template => template.id !== templateId),
            total: paginatedData.total - 1,
          };
          
          queryClient.setQueryData(queryKey, filteredData);
          updates.push({ queryKey, previousData: data });
        }
      });
      
      return { updates };
    },
    onSuccess: (_, templateId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: templateKeys.detail(templateId) });
      
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: templateKeys.user() });
      queryClient.invalidateQueries({ queryKey: templateKeys.lists() });
    },
    onError: (error, templateId, context) => {
      // Rollback optimistic updates
      context?.updates.forEach(({ queryKey, previousData }) => {
        queryClient.setQueryData(queryKey, previousData);
      });
      console.error('Delete template failed:', error);
    },
  });
}

// Get user's custom templates
export function useUserTemplates(params?: {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}) {
  const { page = 1, limit = 12, sortBy = 'updatedAt', sortOrder = 'desc' } = params || {};
  
  return useQuery({
    queryKey: templateKeys.user(),
    queryFn: () => templatesApi.getUserTemplates(page, limit, { sortBy, sortOrder }),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

// Toggle favorite template
export function useToggleTemplateFavorite() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (templateId: string) => templatesApi.toggleFavorite(templateId),
    onMutate: async (templateId) => {
      // Optimistically update template favorite status
      const templateData = queryClient.getQueryData<Template>(templateKeys.detail(templateId));
      
      if (templateData) {
        queryClient.setQueryData<Template>(templateKeys.detail(templateId), {
          ...templateData,
          isFavorite: !templateData.isFavorite,
        });
      }
      
      return { templateData };
    },
    onSuccess: (_, templateId) => {
      // Invalidate favorites list
      queryClient.invalidateQueries({ queryKey: templateKeys.favorites() });
      
      // Invalidate template detail to get accurate favorite status
      queryClient.invalidateQueries({ queryKey: templateKeys.detail(templateId) });
    },
    onError: (error, templateId, context) => {
      // Rollback optimistic updates
      if (context?.templateData) {
        queryClient.setQueryData(templateKeys.detail(templateId), context.templateData);
      }
      console.error('Toggle favorite failed:', error);
    },
  });
}

// Get favorite templates
export function useFavoriteTemplates(params?: {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}) {
  const { page = 1, limit = 12, sortBy = 'createdAt', sortOrder = 'desc' } = params || {};
  
  return useQuery({
    queryKey: templateKeys.favorites(),
    queryFn: () => templatesApi.getFavoriteTemplates(page, limit, { sortBy, sortOrder }),
    staleTime: 2 * 60 * 1000,
  });
}

// Rate template
export function useRateTemplate() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ templateId, rating }: { templateId: string; rating: number }) =>
      templatesApi.rateTemplate(templateId, rating),
    onMutate: async ({ templateId, rating }) => {
      // Optimistically update template rating
      const templateData = queryClient.getQueryData<Template>(templateKeys.detail(templateId));
      
      if (templateData) {
        // TODO: Fix rating calculation based on actual Template interface properties
        const newRating = rating; // Simplified for now
        
        queryClient.setQueryData<Template>(templateKeys.detail(templateId), {
          ...templateData,
          rating: newRating,
          // TODO: Add proper rating tracking properties to Template interface
        });
      }
      
      return { templateData };
    },
    onSuccess: (_, { templateId }) => {
      // Invalidate template detail and stats
      queryClient.invalidateQueries({ queryKey: templateKeys.detail(templateId) });
      queryClient.invalidateQueries({ queryKey: templateKeys.stats(templateId) });
      
      // Invalidate popular templates as rating affects popularity
      queryClient.invalidateQueries({ queryKey: templateKeys.popular() });
    },
    onError: (error, { templateId }, context) => {
      // Rollback optimistic updates
      if (context?.templateData) {
        queryClient.setQueryData(templateKeys.detail(templateId), context.templateData);
      }
      console.error('Rate template failed:', error);
    },
  });
}

// Get template statistics
export function useTemplateStats(templateId: string, enabled = true) {
  return useQuery({
    queryKey: templateKeys.stats(templateId),
    queryFn: () => templatesApi.getTemplateStats(templateId),
    enabled: !!templateId && enabled,
    staleTime: 5 * 60 * 1000,
  });
}

// Search templates with advanced filters
export function useSearchTemplates(
  query: string,
  filters?: {
    category?: string;
    isPremium?: boolean;
    tags?: string[];
    minRating?: number;
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
  },
  enabled = true
) {
  return useQuery({
    queryKey: templateKeys.search(`${query}-${JSON.stringify(filters)}`),
    queryFn: () => templatesApi.searchTemplates(query, filters),
    enabled: !!query && query.length > 2 && enabled,
    staleTime: 2 * 60 * 1000,
    placeholderData: { data: [], total: 0, page: 1, limit: 12, totalPages: 0 },
  });
}

// Get template suggestions based on content
export function useTemplateSuggestions(content: string, limit = 5, enabled = true) {
  return useQuery({
    queryKey: templateKeys.suggestions(content),
    queryFn: () => templatesApi.getTemplateSuggestions(content, limit),
    enabled: !!content && content.length > 10 && enabled,
    staleTime: 5 * 60 * 1000,
    placeholderData: [],
  });
}

// Get premium templates
export function usePremiumTemplates(params?: {
  page?: number;
  limit?: number;
  category?: string;
}) {
  return useQuery({
    queryKey: templateKeys.premium(),
    queryFn: () => templatesApi.getTemplates({ ...params, isPremium: true }),
    staleTime: 10 * 60 * 1000,
  });
}

// Get free templates
export function useFreeTemplates(params?: {
  page?: number;
  limit?: number;
  category?: string;
}) {
  return useQuery({
    queryKey: templateKeys.free(),
    queryFn: () => templatesApi.getTemplates({ ...params, isPremium: false }),
    staleTime: 10 * 60 * 1000,
  });
}

// Get recent templates
export function useRecentTemplates(limit = 5) {
  return useQuery({
    queryKey: templateKeys.recent(),
    queryFn: () => templatesApi.getTemplates({ 
      limit, 
      sortBy: 'createdAt', 
      sortOrder: 'desc' 
    }),
    staleTime: 5 * 60 * 1000,
  });
}

// Duplicate template
export function useDuplicateTemplate() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (templateId: string) => templatesApi.duplicateTemplate(templateId),
    onSuccess: (newTemplate: Template) => {
      // Add to cache
      queryClient.setQueryData(templateKeys.detail(newTemplate.id), newTemplate);
      
      // Invalidate user templates
      queryClient.invalidateQueries({ queryKey: templateKeys.user() });
    },
    onError: (error) => {
      console.error('Duplicate template failed:', error);
    },
  });
}

// Batch operations
export function useBatchDeleteTemplates() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (templateIds: string[]) => templatesApi.batchDeleteTemplates(templateIds),
    onSuccess: (_, templateIds) => {
      // Remove all deleted templates from cache
      templateIds.forEach(id => {
        queryClient.removeQueries({ queryKey: templateKeys.detail(id) });
      });
      
      // Invalidate all template lists
      queryClient.invalidateQueries({ queryKey: templateKeys.lists() });
      queryClient.invalidateQueries({ queryKey: templateKeys.user() });
    },
    onError: (error) => {
      console.error('Batch delete templates failed:', error);
    },
  });
}

// Prefetch template (for optimization)
export function usePrefetchTemplate() {
  const queryClient = useQueryClient();
  
  return (templateId: string) => {
    queryClient.prefetchQuery({
      queryKey: templateKeys.detail(templateId),
      queryFn: () => templatesApi.getTemplate(templateId),
      staleTime: 10 * 60 * 1000,
    });
  };
}

// Combined hook for template browser/dashboard
export function useTemplatesDashboard() {
  const featured = useFeaturedTemplates();
  const popular = usePopularTemplates(8);
  const trending = useTrendingTemplates(6);
  const categories = useTemplateCategories();
  const recent = useRecentTemplates(5);
  
  return {
    featured,
    popular,
    trending,
    categories,
    recent,
    isLoading: featured.isLoading || popular.isLoading || trending.isLoading || categories.isLoading,
    isError: featured.isError || popular.isError || trending.isError || categories.isError,
    error: featured.error || popular.error || trending.error || categories.error,
  };
}

// Hook for template recommendations
export function useTemplateRecommendations(userId?: string, limit = 6) {
  return useQuery({
    queryKey: [...templateKeys.all, 'recommendations', userId, limit],
    queryFn: () => templatesApi.getRecommendations(limit),
    enabled: !!userId,
    staleTime: 15 * 60 * 1000, // 15 minutes
  });
}