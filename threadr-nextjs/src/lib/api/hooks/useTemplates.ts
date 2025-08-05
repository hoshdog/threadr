import { useMutation, useQuery, useQueryClient, useInfiniteQuery } from '@tanstack/react-query';
import { templatesApi, Template, TemplateCategory, CreateTemplateRequest, GenerateFromTemplateRequest } from '../templates';

// Query keys
export const templateKeys = {
  all: ['templates'] as const,
  lists: () => [...templateKeys.all, 'list'] as const,
  list: (filters: Record<string, any>) => [...templateKeys.lists(), { filters }] as const,
  details: () => [...templateKeys.all, 'detail'] as const,
  detail: (id: string) => [...templateKeys.details(), id] as const,
  categories: () => [...templateKeys.all, 'categories'] as const,
  popular: () => [...templateKeys.all, 'popular'] as const,
  featured: () => [...templateKeys.all, 'featured'] as const,
  user: () => [...templateKeys.all, 'user'] as const,
  favorites: () => [...templateKeys.all, 'favorites'] as const,
  search: (query: string) => [...templateKeys.all, 'search', query] as const,
  categoryTemplates: (categoryId: string) => [...templateKeys.all, 'category', categoryId] as const,
  stats: (id: string) => [...templateKeys.all, 'stats', id] as const,
  suggestions: (content: string) => [...templateKeys.all, 'suggestions', content] as const,
} as const;

// Get templates with filtering
export function useTemplates(params?: {
  category?: string;
  isPremium?: boolean;
  search?: string;
  tags?: string[];
  page?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: templateKeys.list(params || {}),
    queryFn: () => templatesApi.getTemplates(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Get infinite templates (for infinite scroll)
export function useInfiniteTemplates(params?: {
  category?: string;
  isPremium?: boolean;
  search?: string;
  tags?: string[];
  limit?: number;
}) {
  const { limit = 12, ...otherParams } = params || {};
  
  return useInfiniteQuery({
    queryKey: templateKeys.lists(),
    queryFn: ({ pageParam = 1 }) => 
      templatesApi.getTemplates({ ...otherParams, page: pageParam, limit }),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      const { page, totalPages } = lastPage;
      return page < totalPages ? page + 1 : undefined;
    },
    staleTime: 5 * 60 * 1000,
  });
}

// Get specific template
export function useTemplate(templateId: string, enabled = true) {
  return useQuery({
    queryKey: templateKeys.detail(templateId),
    queryFn: () => templatesApi.getTemplate(templateId),
    enabled: !!templateId && enabled,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Get template categories
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

// Get templates by category
export function useTemplatesByCategory(categoryId: string, page = 1, limit = 12, enabled = true) {
  return useQuery({
    queryKey: templateKeys.categoryTemplates(categoryId),
    queryFn: () => templatesApi.getTemplatesByCategory(categoryId, page, limit),
    enabled: !!categoryId && enabled,
    staleTime: 5 * 60 * 1000,
  });
}

// Generate thread from template
export function useGenerateFromTemplate() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (request: GenerateFromTemplateRequest) => 
      templatesApi.generateFromTemplate(request),
    onSuccess: (_, variables) => {
      // Invalidate template stats to update usage count
      queryClient.invalidateQueries({ 
        queryKey: templateKeys.stats(variables.templateId) 
      });
      
      // Invalidate popular templates as usage affects popularity
      queryClient.invalidateQueries({ queryKey: templateKeys.popular() });
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
    },
  });
}

// Update template
export function useUpdateTemplate(templateId: string) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (updates: Partial<CreateTemplateRequest>) => 
      templatesApi.updateTemplate(templateId, updates),
    onSuccess: (updatedTemplate: Template) => {
      // Update in cache
      queryClient.setQueryData(templateKeys.detail(templateId), updatedTemplate);
      
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: templateKeys.user() });
      queryClient.invalidateQueries({ queryKey: templateKeys.lists() });
    },
  });
}

// Delete template
export function useDeleteTemplate() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (templateId: string) => templatesApi.deleteTemplate(templateId),
    onSuccess: (_, templateId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: templateKeys.detail(templateId) });
      
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: templateKeys.user() });
      queryClient.invalidateQueries({ queryKey: templateKeys.lists() });
    },
  });
}

// Get user's custom templates
export function useUserTemplates(page = 1, limit = 12) {
  return useQuery({
    queryKey: templateKeys.user(),
    queryFn: () => templatesApi.getUserTemplates(page, limit),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

// Toggle favorite template
export function useToggleFavorite() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (templateId: string) => templatesApi.toggleFavorite(templateId),
    onSuccess: (_, templateId) => {
      // Invalidate favorites list
      queryClient.invalidateQueries({ queryKey: templateKeys.favorites() });
      
      // Invalidate template detail to update favorite status
      queryClient.invalidateQueries({ queryKey: templateKeys.detail(templateId) });
    },
  });
}

// Get favorite templates
export function useFavoriteTemplates(page = 1, limit = 12) {
  return useQuery({
    queryKey: templateKeys.favorites(),
    queryFn: () => templatesApi.getFavoriteTemplates(page, limit),
    staleTime: 2 * 60 * 1000,
  });
}

// Rate template
export function useRateTemplate() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ templateId, rating }: { templateId: string; rating: number }) =>
      templatesApi.rateTemplate(templateId, rating),
    onSuccess: (_, { templateId }) => {
      // Invalidate template detail and stats
      queryClient.invalidateQueries({ queryKey: templateKeys.detail(templateId) });
      queryClient.invalidateQueries({ queryKey: templateKeys.stats(templateId) });
      
      // Invalidate popular templates as rating affects popularity
      queryClient.invalidateQueries({ queryKey: templateKeys.popular() });
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

// Search templates
export function useSearchTemplates(
  query: string,
  filters?: {
    category?: string;
    isPremium?: boolean;
    tags?: string[];
  },
  enabled = true
) {
  return useQuery({
    queryKey: templateKeys.search(query),
    queryFn: () => templatesApi.searchTemplates(query, filters),
    enabled: !!query && query.length > 2 && enabled,
    staleTime: 2 * 60 * 1000,
  });
}

// Get template suggestions
export function useTemplateSuggestions(content: string, limit = 5, enabled = true) {
  return useQuery({
    queryKey: templateKeys.suggestions(content),
    queryFn: () => templatesApi.getTemplateSuggestions(content, limit),
    enabled: !!content && content.length > 10 && enabled,
    staleTime: 5 * 60 * 1000,
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