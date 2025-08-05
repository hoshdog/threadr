import { apiClient } from './client';

// Template types
export interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  isPremium: boolean;
  isPublic?: boolean;
  prompt: string;
  tags: string[];
  previewTweets: string[];
  usage: number;
  rating: number;
  totalRatings?: number;
  isFavorite?: boolean;
  userRating?: number;
  createdAt: string;
  updatedAt: string;
}

export interface TemplateCategory {
  id: string;
  name: string;
  description: string;
  templateCount: number;
  isPremium: boolean;
}

export interface CreateTemplateRequest {
  name: string;
  description: string;
  category: string;
  prompt: string;
  tags: string[];
  isPremium?: boolean;
}

export interface GenerateFromTemplateRequest {
  templateId: string;
  content?: string;
  url?: string;
  customizations?: Record<string, any>;
}

export const templatesApi = {

  // Get a specific template by ID
  async getTemplate(templateId: string): Promise<Template> {
    return apiClient.get<Template>(`/templates/${templateId}`);
  },

  // Get template categories
  async getCategories(): Promise<TemplateCategory[]> {
    return apiClient.get<TemplateCategory[]>('/templates/categories');
  },

  // Get popular templates
  async getPopularTemplates(limit = 10): Promise<Template[]> {
    return apiClient.get<Template[]>(`/templates/popular?limit=${limit}`);
  },

  // Get featured templates
  async getFeaturedTemplates(): Promise<Template[]> {
    return apiClient.get<Template[]>('/templates/featured');
  },

  // Get templates by category
  async getTemplatesByCategory(categoryId: string, page = 1, limit = 10, options?: {
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
  }): Promise<{
    data: Template[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });
    
    if (options?.sortBy) params.append('sortBy', options.sortBy);
    if (options?.sortOrder) params.append('sortOrder', options.sortOrder);
    
    return apiClient.get(`/templates/category/${categoryId}?${params.toString()}`);
  },

  // Generate thread from template
  async generateFromTemplate(request: GenerateFromTemplateRequest): Promise<{
    threadId?: string;
    tweets: Array<{
      id: string;
      content: string;
      order: number;
      characterCount: number;
    }>;
    sourceTitle?: string;
    sourceUrl?: string;
    totalCharacters: number;
    templateUsed: string;
  }> {
    return apiClient.post('/templates/generate', request);
  },

  // Create custom template (premium feature)
  async createTemplate(templateData: CreateTemplateRequest): Promise<Template> {
    return apiClient.post<Template>('/templates', templateData);
  },

  // Update template (only for user's own templates)
  async updateTemplate(templateId: string, updates: Partial<CreateTemplateRequest>): Promise<Template> {
    return apiClient.put<Template>(`/templates/${templateId}`, updates);
  },

  // Delete template (only for user's own templates)
  async deleteTemplate(templateId: string): Promise<void> {
    return apiClient.delete(`/templates/${templateId}`);
  },

  // Get user's custom templates
  async getUserTemplates(page = 1, limit = 10, options?: {
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
  }): Promise<{
    data: Template[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });
    
    if (options?.sortBy) params.append('sortBy', options.sortBy);
    if (options?.sortOrder) params.append('sortOrder', options.sortOrder);
    
    return apiClient.get(`/templates/user?${params.toString()}`);
  },

  // Favorite/unfavorite template
  async toggleFavorite(templateId: string): Promise<{ isFavorite: boolean }> {
    return apiClient.post(`/templates/${templateId}/favorite`);
  },

  // Get user's favorite templates
  async getFavoriteTemplates(page = 1, limit = 10, options?: {
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
  }): Promise<{
    data: Template[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });
    
    if (options?.sortBy) params.append('sortBy', options.sortBy);
    if (options?.sortOrder) params.append('sortOrder', options.sortOrder);
    
    return apiClient.get(`/templates/favorites?${params.toString()}`);
  },

  // Rate template
  async rateTemplate(templateId: string, rating: number): Promise<{ averageRating: number; userRating: number }> {
    return apiClient.post(`/templates/${templateId}/rate`, { rating });
  },

  // Get template usage statistics
  async getTemplateStats(templateId: string): Promise<{
    totalUsage: number;
    recentUsage: Array<{ date: string; count: number }>;
    averageRating: number;
    totalRatings: number;
  }> {
    return apiClient.get(`/templates/${templateId}/stats`);
  },

  // Search templates
  async searchTemplates(query: string, filters?: {
    category?: string;
    isPremium?: boolean;
    tags?: string[];
    minRating?: number;
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
  }): Promise<{
    data: Template[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    const params = new URLSearchParams({ q: query });
    
    if (filters?.category) params.append('category', filters.category);
    if (filters?.isPremium !== undefined) params.append('isPremium', filters.isPremium.toString());
    if (filters?.tags) filters.tags.forEach(tag => params.append('tags', tag));
    if (filters?.minRating) params.append('minRating', filters.minRating.toString());
    if (filters?.sortBy) params.append('sortBy', filters.sortBy);
    if (filters?.sortOrder) params.append('sortOrder', filters.sortOrder);
    
    return apiClient.get(`/templates/search?${params.toString()}`);
  },

  // Get template suggestions based on content
  async getTemplateSuggestions(content: string, limit = 5): Promise<Template[]> {
    return apiClient.post<Template[]>('/templates/suggestions', { content, limit });
  },

  // Get trending templates
  async getTrendingTemplates(limit = 10): Promise<Template[]> {
    return apiClient.get<Template[]>(`/templates/trending?limit=${limit}`);
  },

  // Duplicate template
  async duplicateTemplate(templateId: string): Promise<Template> {
    return apiClient.post<Template>(`/templates/${templateId}/duplicate`);
  },

  // Batch operations
  async batchDeleteTemplates(templateIds: string[]): Promise<{ deleted: number }> {
    return apiClient.post('/templates/batch/delete', { templateIds });
  },

  // Get template recommendations for user
  async getRecommendations(limit = 6): Promise<Template[]> {
    return apiClient.get<Template[]>(`/templates/recommendations?limit=${limit}`);
  },

  // Advanced template operations
  async getTemplates(params?: {
    category?: string;
    isPremium?: boolean;
    isPublic?: boolean;
    search?: string;
    tags?: string[];
    page?: number;
    limit?: number;
    sortBy?: 'name' | 'usage' | 'rating' | 'createdAt' | 'updatedAt';
    sortOrder?: 'asc' | 'desc';
  }): Promise<{
    data: Template[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }> {
    const queryParams = new URLSearchParams();
    
    if (params?.category) queryParams.append('category', params.category);
    if (params?.isPremium !== undefined) queryParams.append('isPremium', params.isPremium.toString());
    if (params?.isPublic !== undefined) queryParams.append('isPublic', params.isPublic.toString());
    if (params?.search) queryParams.append('search', params.search);
    if (params?.tags) params.tags.forEach(tag => queryParams.append('tags', tag));
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.sortBy) queryParams.append('sortBy', params.sortBy);
    if (params?.sortOrder) queryParams.append('sortOrder', params.sortOrder);

    const query = queryParams.toString();
    const url = query ? `/templates?${query}` : '/templates';
    
    return apiClient.get(url);
  },
};