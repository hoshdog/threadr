import { apiClient } from './client';
import {
  Thread,
  UsageStats,
} from '@/types';
import { PaginatedResponse, SavedThread, GenerateThreadRequest, GenerateThreadResponse } from '@/types/api';

export const threadsApi = {
  async generateThread(request: GenerateThreadRequest): Promise<GenerateThreadResponse> {
    // The backend expects either 'url' or 'text' field in the request
    const response = await apiClient.postRaw<any>('/generate', request);
    
    // Handle the raw response from the backend
    if (response.data.success) {
      // Transform backend response to match frontend expectations
      const backendData = response.data;
      
      // Convert string array to Tweet array with proper structure
      const tweets = (backendData.tweets || []).map((content: string, index: number) => ({
        number: index + 1,
        total: backendData.thread_count || backendData.tweets?.length || 0,
        content: content,
        character_count: content.length
      }));
      
      return {
        success: true,
        thread: tweets,
        source_type: request.url ? 'url' : 'text',
        title: backendData.title || null,
        error: null,
        saved_thread_id: backendData.saved_thread_id || null
      };
    } else {
      throw new Error(response.data.error || 'Invalid response format from server');
    }
  },

  async getThreads(page = 1, limit = 10, filters?: Record<string, any>): Promise<PaginatedResponse<SavedThread>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...filters,
    });
    return apiClient.get<PaginatedResponse<SavedThread>>(`/threads?${params.toString()}`);
  },

  async getThread(threadId: string): Promise<Thread> {
    return apiClient.get<Thread>(`/threads/${threadId}`);
  },

  async saveThread(thread: Omit<Thread, 'id' | 'createdAt' | 'updatedAt'>): Promise<Thread> {
    return apiClient.post<Thread>('/threads', thread);
  },

  async updateThread(threadId: string, updates: Partial<Thread>): Promise<Thread> {
    return apiClient.put<Thread>(`/threads/${threadId}`, updates);
  },

  async deleteThread(threadId: string): Promise<void> {
    return apiClient.delete(`/threads/${threadId}`);
  },

  async duplicateThread(threadId: string): Promise<Thread> {
    return apiClient.post<Thread>(`/threads/${threadId}/duplicate`);
  },

  async getUsageStats(): Promise<UsageStats> {
    return apiClient.get<UsageStats>('/usage-stats');
  },

  async getPremiumStatus(): Promise<{ isPremium: boolean; expiresAt?: string }> {
    return apiClient.get('/premium-status');
  },

  async captureEmail(email: string): Promise<{ message: string }> {
    return apiClient.post('/capture-email', { email });
  },

  // Search and filtering
  async searchThreads(query: string, page = 1, limit = 10, filters?: Record<string, any>): Promise<PaginatedResponse<Thread>> {
    const params = new URLSearchParams({
      q: query,
      page: page.toString(),
      limit: limit.toString(),
      ...filters,
    });
    return apiClient.get<PaginatedResponse<Thread>>(`/threads/search?${params.toString()}`);
  },

  async getThreadsByTag(tag: string, page = 1, limit = 10): Promise<PaginatedResponse<Thread>> {
    return apiClient.get<PaginatedResponse<Thread>>(
      `/threads/tags/${encodeURIComponent(tag)}?page=${page}&limit=${limit}`
    );
  },

  async getPopularTags(): Promise<Array<{ tag: string; count: number }>> {
    return apiClient.get('/threads/tags/popular');
  },

  // Favorites
  async getFavoriteThreads(page = 1, limit = 10): Promise<PaginatedResponse<Thread>> {
    return apiClient.get<PaginatedResponse<Thread>>(`/threads/favorites?page=${page}&limit=${limit}`);
  },

  async toggleFavorite(threadId: string): Promise<{ isFavorite: boolean }> {
    return apiClient.post(`/threads/${threadId}/favorite`);
  },

  // Analytics
  async getThreadAnalytics(threadId: string): Promise<{
    views: number;
    clicks: number;
    shares: number;
    engagement: number;
    performance: 'high' | 'medium' | 'low';
  }> {
    return apiClient.get(`/threads/${threadId}/analytics`);
  },

  // Batch operations
  async batchDeleteThreads(threadIds: string[]): Promise<{ deleted: number }> {
    return apiClient.post('/threads/batch/delete', { threadIds });
  },

  // Export
  async exportThreads(params: { threadIds?: string[]; format: 'json' | 'csv' | 'txt' }): Promise<Blob> {
    const response = await apiClient.postRaw('/threads/export', params, {
      responseType: 'blob',
    });
    return response.data;
  },
};