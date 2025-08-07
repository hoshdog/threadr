// Core types for Threadr application

export interface User {
  id: string;
  email: string;
  username?: string;
  isPremium: boolean;
  premiumExpiresAt?: string;
  emailVerified?: boolean;
  hasCompletedOnboarding?: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Thread {
  id: string;
  userId: string;
  title: string;
  sourceUrl?: string;
  sourceContent?: string;
  tweets: Tweet[];
  createdAt: string;
  updatedAt: string;
  isPublic: boolean;
  tags?: string[];
}

export interface Tweet {
  id: string;
  content: string;
  order: number;
  characterCount: number;
}

export interface GenerateThreadRequest {
  content?: string;
  url?: string;
  customPrompt?: string;
}

export interface GenerateThreadResponse {
  threadId?: string;
  tweets: Tweet[];
  sourceTitle?: string;
  sourceUrl?: string;
  totalCharacters: number;
}

export interface UsageStats {
  dailyUsage: number;
  monthlyUsage: number;
  dailyLimit: number;
  monthlyLimit: number;
  isPremium: boolean;
  canGenerate: boolean;
}

export interface AnalyticsDashboard {
  totalThreads: number;
  totalTweets: number;
  averageThreadLength: number;
  popularDomains: Array<{
    domain: string;
    count: number;
  }>;
  recentActivity: Array<{
    date: string;
    threadsCreated: number;
  }>;
}

export interface TeamMember {
  id: string;
  userId: string;
  teamId: string;
  role: 'owner' | 'admin' | 'member';
  joinedAt: string;
  user: Pick<User, 'id' | 'email' | 'username'>;
}

export interface Team {
  id: string;
  name: string;
  description?: string;
  ownerId: string;
  createdAt: string;
  updatedAt: string;
  members: TeamMember[];
}

// Authentication types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  username?: string;
}

export interface AuthResponse {
  user: User;
  token: string;
  refreshToken: string;
}

// API Response types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// UI Component types
export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}

export interface InputProps {
  label?: string;
  placeholder?: string;
  type?: string;
  value?: string;
  onChange?: (value: string) => void;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  className?: string;
}

// Payment types
export interface PaymentIntent {
  clientSecret: string;
  amount: number;
  currency: string;
}

export interface SubscriptionPlan {
  id: string;
  name: string;
  display_name: string;
  monthly_price: number; // Price in cents
  annual_price: number;  // Price in cents
  thread_limit: number;  // -1 for unlimited
  tier_level: number;
  features: string[];
  monthly_price_id: string; // Stripe price ID
  annual_price_id: string;  // Stripe price ID
  isPopular?: boolean; // Frontend-only property
}

// Error types
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Template types (additional types for the templates API)
export interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  isPremium: boolean;
  prompt: string;
  tags: string[];
  previewTweets: string[];
  usage: number;
  rating: number;
  createdAt: string;
  updatedAt: string;
  isFavorite?: boolean;
  userRating?: number;
}

export interface TemplateCategory {
  id: string;
  name: string;
  description: string;
  templateCount: number;
  isPremium: boolean;
}

// Utility types
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export type Theme = 'light' | 'dark' | 'system';

export interface AppState {
  user: User | null;
  isAuthenticated: boolean;
  theme: Theme;
  isLoading: boolean;
}