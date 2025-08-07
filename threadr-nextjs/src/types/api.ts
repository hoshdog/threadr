/**
 * Comprehensive TypeScript type definitions for Threadr API
 * 
 * This file contains all TypeScript interfaces that match the FastAPI/Pydantic models
 * from the backend to ensure perfect API contract alignment.
 * 
 * Generated from backend models in:
 * - backend/src/models/auth.py
 * - backend/src/models/thread.py
 * - backend/src/models/analytics.py
 * - backend/src/models/team.py
 * - backend/src/main.py (API request/response models)
 */

// ============================================================================
// AUTHENTICATION TYPES
// ============================================================================

// Enums
export enum UserRole {
  USER = "user",
  PREMIUM = "premium",
  ADMIN = "admin"
}

export enum UserStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  SUSPENDED = "suspended" 
}

// Request Models
export interface UserRegistrationRequest {
  email: string;
  password: string;
  confirm_password: string;
}

export interface UserLoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface TokenRefreshRequest {
  refresh_token: string;
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
  confirm_new_password: string;
}

// Response Models
export interface UserResponse {
  user_id: string;
  email: string;
  role: UserRole;
  status: UserStatus;
  created_at: string;
  last_login_at: string | null;
  is_premium: boolean;
  premium_expires_at: string | null;
  usage_stats: Record<string, any> | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string; // "bearer"
  expires_in: number; // seconds
  refresh_token: string | null;
  user: UserResponse;
}

export interface TokenPayload {
  sub: string; // user_id
  email: string;
  role: string;
  exp: number;
  iat: number;
  type: string; // "access" or "refresh"
}

// Internal User Model (for completeness)
export interface User {
  user_id: string;
  email: string;
  password_hash: string;
  role: UserRole;
  status: UserStatus;
  created_at: string;
  updated_at: string;
  last_login_at: string | null;
  login_count: number;
  failed_login_attempts: number;
  last_failed_login: string | null;
  is_email_verified: boolean;
  email_verification_token: string | null;
  password_reset_token: string | null;
  password_reset_expires: string | null;
  metadata: Record<string, any>;
}

// ============================================================================
// THREAD TYPES
// ============================================================================

// Core Thread Models
export interface ThreadTweet {
  id: string;
  content: string;
  order: number; // 1-based
  character_count: number;
}

export interface ThreadMetadata {
  source_url: string | null;
  source_type: string; // "URL" or "text"
  generation_time_ms: number | null;
  ai_model: string; // default "gpt-3.5-turbo"
  content_length: number | null;
  tags: string[];
}

export interface SavedThread {
  id: string;
  user_id: string;
  title: string;
  original_content: string;
  tweets: ThreadTweet[];
  metadata: ThreadMetadata;
  // Timestamps
  created_at: string;
  updated_at: string;
  // Usage tracking
  view_count: number;
  copy_count: number;
  // Premium features
  is_favorite: boolean;
  is_archived: boolean;
  // Computed properties
  tweet_count: number;
  total_characters: number;
  preview_text: string;
}

// Request Models
export interface SaveThreadRequest {
  title: string;
  original_content: string;
  tweets: Record<string, any>[];
  metadata?: Record<string, any> | null;
}

export interface UpdateThreadRequest {
  title?: string | null;
  is_favorite?: boolean | null;
  is_archived?: boolean | null;
  tags?: string[] | null;
}

export interface ThreadHistoryRequest {
  page?: number; // default 1
  page_size?: number; // default 10, max 50
  search_query?: string | null;
  source_type?: string | null;
  is_favorite?: boolean | null;
  is_archived?: boolean | null;
  date_from?: string | null;
  date_to?: string | null;
  sort_by?: string; // "created_at" | "updated_at" | "title" | "tweet_count"
  sort_order?: string; // "asc" | "desc"
}

// Response Models
export interface ThreadHistoryResponse {
  threads: Record<string, any>[];
  total_count: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface ThreadHistoryFilter {
  search_query: string | null;
  source_type: string | null; // "url" or "text"
  is_favorite: boolean | null;
  is_archived: boolean | null;
  date_from: string | null;
  date_to: string | null;
  tags: string[] | null;
}

// ============================================================================
// ANALYTICS TYPES
// ============================================================================

// Enums
export enum MetricPeriod {
  HOUR = "hour",
  DAY = "day",
  WEEK = "week",
  MONTH = "month",
  ALL_TIME = "all_time"
}

export enum EngagementType {
  IMPRESSION = "impression",
  LIKE = "like",
  RETWEET = "retweet",
  REPLY = "reply",
  BOOKMARK = "bookmark",
  QUOTE = "quote",
  PROFILE_VISIT = "profile_visit",
  LINK_CLICK = "link_click",
  FOLLOW = "follow"
}

export enum ContentType {
  EDUCATIONAL = "educational",
  NEWS = "news",
  PERSONAL = "personal",
  PROMOTIONAL = "promotional",
  ENTERTAINMENT = "entertainment",
  TECHNICAL = "technical",
  OTHER = "other"
}

// Core Analytics Models
export interface TweetMetrics {
  tweet_id: string;
  position: number; // 1-based position in thread
  content: string;
  character_count: number;
  // Engagement metrics
  impressions: number;
  likes: number;
  retweets: number;
  replies: number;
  bookmarks: number;
  quotes: number;
  // Calculated metrics
  engagement_rate: number;
  drop_off_rate: number | null;
  // Timing
  posted_at: string;
  peak_hour: number | null;
}

export interface ThreadAnalytics {
  thread_id: string;
  user_id: string;
  created_at: string;
  // Thread metadata
  title: string;
  source_url: string | null;
  content_type: ContentType;
  tweet_count: number;
  total_character_count: number;
  // Overall metrics
  total_impressions: number;
  total_engagements: number;
  engagement_rate: number;
  // Detailed engagement
  total_likes: number;
  total_retweets: number;
  total_replies: number;
  total_bookmarks: number;
  total_quotes: number;
  // Business metrics
  profile_visits: number;
  link_clicks: number;
  new_followers: number;
  // Performance metrics
  thread_completion_rate: number; // % who viewed last tweet
  avg_time_on_thread: number; // seconds
  virality_score: number; // 0-100 score
  // Tweet-level metrics
  tweet_metrics: TweetMetrics[];
  // Best performing elements
  best_tweet_position: number | null;
  worst_tweet_position: number | null;
  optimal_length: number | null;
  // Time analysis
  posted_at: string;
  peak_engagement_hour: number | null;
  peak_engagement_day: string | null;
}

export interface TimeSeriesDataPoint {
  timestamp: string;
  value: number;
  period: MetricPeriod;
}

export interface MetricSummary {
  current_value: number;
  previous_value: number;
  change_percent: number;
  trend: string; // "up" | "down" | "stable"
  period: MetricPeriod;
}

export interface DashboardSummary {
  user_id: string;
  period: MetricPeriod;
  generated_at: string;
  // Key metrics with comparisons
  total_impressions: MetricSummary;
  engagement_rate: MetricSummary;
  follower_growth: MetricSummary;
  avg_thread_performance: MetricSummary;
  // Thread statistics
  total_threads: number;
  threads_this_period: number;
  best_performing_thread: Record<string, any> | null;
  worst_performing_thread: Record<string, any> | null;
  // Content analysis
  content_type_breakdown: Record<string, number>; // content_type -> percentage
  optimal_posting_times: Record<string, any>[]; // day/hour combinations
  // Time series data for charts
  impressions_over_time: TimeSeriesDataPoint[];
  engagement_rate_over_time: TimeSeriesDataPoint[];
}

export interface ThreadComparison {
  thread_a: ThreadAnalytics;
  thread_b: ThreadAnalytics;
  // Comparison metrics
  impressions_diff: number;
  engagement_rate_diff: number;
  completion_rate_diff: number;
  virality_score_diff: number;
  // Winner indicators
  better_performer: string; // thread_id of better performer
  key_differences: string[]; // Key insights about differences
}

export interface InsightRecommendation {
  insight_id: string;
  category: string; // "timing" | "content" | "engagement" | "growth"
  priority: string; // "high" | "medium" | "low"
  title: string;
  description: string;
  action_items: string[];
  // Supporting data
  confidence_score: number; // 0-1
  based_on_threads: string[]; // thread_ids used for this insight
  potential_impact: string; // Expected improvement if implemented
  generated_at: string;
}

export interface BenchmarkData {
  category: ContentType;
  period: MetricPeriod;
  // Percentile data
  avg_impressions_p50: number;
  avg_impressions_p75: number;
  avg_impressions_p90: number;
  avg_engagement_rate_p50: number;
  avg_engagement_rate_p75: number;
  avg_engagement_rate_p90: number;
  avg_thread_length: number;
  avg_completion_rate: number;
  // User's position
  user_percentile_impressions: number | null;
  user_percentile_engagement: number | null;
}

export interface AnalyticsExport {
  user_id: string;
  export_date: string;
  period: MetricPeriod;
  // Summary metrics
  summary: DashboardSummary;
  // Detailed thread data
  threads: ThreadAnalytics[];
  // Insights and recommendations
  insights: InsightRecommendation[];
  // Benchmark data
  benchmarks: BenchmarkData | null;
}

// Analytics API Response Models
export interface DashboardResponse {
  success: boolean;
  data: DashboardSummary;
  error?: string;
}

export interface ThreadComparisonRequest {
  thread_a_id: string;
  thread_b_id: string;
}

export interface InsightsResponse {
  success: boolean;
  insights: InsightRecommendation[];
  error?: string;
}

export interface BenchmarkResponse {
  success: boolean;
  benchmarks: BenchmarkData[];
  error?: string;
}

// ============================================================================
// TEAM COLLABORATION TYPES
// ============================================================================

// Enums
export enum TeamRole {
  OWNER = "owner",
  ADMIN = "admin", 
  EDITOR = "editor",
  VIEWER = "viewer"
}

export enum TeamPlan {
  FREE = "free",
  STARTER = "starter",
  PRO = "pro",
  ENTERPRISE = "enterprise"
}

export enum InviteStatus {
  PENDING = "pending",
  ACCEPTED = "accepted",
  EXPIRED = "expired",
  REVOKED = "revoked"
}

export enum ThreadStatus {
  DRAFT = "draft",
  SUBMITTED = "submitted",
  APPROVED = "approved",
  REJECTED = "rejected",
  PUBLISHED = "published"
}

// Core Team Models
export interface Team {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  // Owner and billing
  owner_id: string;
  plan: TeamPlan;
  billing_email: string | null;
  stripe_customer_id: string | null;
  stripe_subscription_id: string | null;
  // Settings
  settings: Record<string, any>;
  features: Record<string, boolean>;
  // Limits based on plan
  max_members: number;
  max_monthly_threads: number;
  // Timestamps
  created_at: string;
  updated_at: string;
  // Status
  is_active: boolean;
  suspended_at: string | null;
  suspended_reason: string | null;
}

export interface TeamMembership {
  id: string;
  team_id: string;
  user_id: string;
  role: TeamRole;
  // Permissions
  permissions: string[];
  // Status
  is_active: boolean;
  joined_at: string;
  updated_at: string;
  // Activity tracking
  last_activity_at: string | null;
  thread_count: number;
}

export interface TeamInvite {
  id: string;
  team_id: string;
  invited_by_user_id: string;
  // Invitee info
  email: string;
  role: TeamRole;
  // Invite details
  token: string;
  message: string | null;
  // Status and timestamps
  status: InviteStatus;
  created_at: string;
  expires_at: string;
  accepted_at: string | null;
  revoked_at: string | null;
}

export interface TeamThread {
  // Base thread info
  thread_id: string;
  team_id: string;
  // Collaboration fields
  author_id: string;
  assigned_to_id: string | null;
  status: ThreadStatus;
  // Approval workflow
  submitted_at: string | null;
  submitted_by_id: string | null;
  reviewed_at: string | null;
  reviewed_by_id: string | null;
  review_notes: string | null;
  // Collaboration metadata
  collaborators: string[]; // User IDs
  mentions: string[]; // User IDs mentioned
  // Version control
  version: number;
  parent_version_id: string | null;
  // Timestamps
  created_at: string;
  updated_at: string;
}

export interface TeamActivity {
  id: string;
  team_id: string;
  user_id: string;
  // Activity details
  action: string; // "thread.created", "member.invited", etc.
  resource_type: string; // "thread", "member", "team"
  resource_id: string | null;
  // Context
  details: Record<string, any>;
  ip_address: string | null;
  user_agent: string | null;
  // Timestamp
  timestamp: string;
}

// Team API Request/Response Models
export interface CreateTeamRequest {
  name: string;
  slug: string;
  description?: string | null;
  plan?: TeamPlan;
}

export interface UpdateTeamRequest {
  name?: string | null;
  description?: string | null;
  settings?: Record<string, any> | null;
}

export interface InviteMemberRequest {
  email: string;
  role: TeamRole;
  message?: string | null;
}

export interface UpdateMemberRequest {
  role?: TeamRole | null;
  permissions?: string[] | null;
}

export interface AcceptInviteRequest {
  token: string;
}

export interface TeamResponse {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  plan: TeamPlan;
  member_count: number;
  max_members: number;
  owner_id: string;
  created_at: string;
  current_user_role: TeamRole | null;
}

export interface MemberResponse {
  user_id: string;
  email: string;
  role: TeamRole;
  joined_at: string;
  last_activity_at: string | null;
  thread_count: number;
  is_active: boolean;
}

export interface InviteResponse {
  id: string;
  email: string;
  role: TeamRole;
  status: InviteStatus;
  created_at: string;
  expires_at: string;
  invited_by: string; // Email of inviter
}

export interface TeamStatsResponse {
  member_count: number;
  active_members: number;
  total_threads: number;
  threads_this_month: number;
  monthly_limit: number;
  plan_usage_percent: number;
}

// ============================================================================
// MAIN API TYPES (from main.py)
// ============================================================================

// Core Thread Generation
export interface GenerateThreadRequest {
  content: string;
  url?: string | null;
}

export interface Tweet {
  number: number;
  total: number;
  content: string;
  character_count: number;
}

export interface GenerateThreadResponse {
  success: boolean;
  thread: Tweet[];
  source_type: string;
  title: string | null;
  error: string | null;
  saved_thread_id: string | null; // Thread ID if saved to history
}

// Email Subscription
export interface EmailSubscribeRequest {
  email: string;
}

export interface EmailSubscribeResponse {
  success: boolean;
  message: string;
  email: string | null;
}

// Usage & Premium Status
export interface UsageStatus {
  daily_usage: number;
  daily_limit: number;
  monthly_usage: number;
  monthly_limit: number;
  has_premium: boolean;
  premium_expires_at: string | null;
}

export interface PremiumCheckResponse {
  has_premium: boolean;
  usage_status: UsageStatus;
  needs_payment: boolean;
  premium_price: number;
  message: string;
}

export interface GrantPremiumRequest {
  email?: string | null;
  plan?: string; // default "premium"
  duration_days?: number; // default 30
  payment_reference: string;
}

// ============================================================================
// TEMPLATE TYPES (Extended from existing frontend types)
// ============================================================================

export interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  is_premium: boolean;
  prompt: string;
  tags: string[];
  preview_tweets: string[];
  usage_count: number;
  rating: number;
  created_at: string;
  updated_at: string;
  is_favorite?: boolean;
  user_rating?: number;
}

export interface TemplateCategory {
  id: string;
  name: string;
  description: string;
  template_count: number;
  is_premium: boolean;
}

// ============================================================================
// ERROR TYPES
// ============================================================================

// Authentication Errors
export class AuthError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AuthError';
  }
}

export class InvalidCredentialsError extends AuthError {
  constructor(message: string = 'Invalid credentials') {
    super(message);
    this.name = 'InvalidCredentialsError';
  }
}

export class UserNotFoundError extends AuthError {
  constructor(message: string = 'User not found') {
    super(message);
    this.name = 'UserNotFoundError';
  }
}

export class UserAlreadyExistsError extends AuthError {
  constructor(message: string = 'User already exists') {
    super(message);
    this.name = 'UserAlreadyExistsError';
  }
}

export class AccountSuspendedError extends AuthError {
  constructor(message: string = 'Account suspended') {
    super(message);
    this.name = 'AccountSuspendedError';
  }
}

export class InvalidTokenError extends AuthError {
  constructor(message: string = 'Invalid token') {
    super(message);
    this.name = 'InvalidTokenError';
  }
}

export class TokenExpiredError extends AuthError {
  constructor(message: string = 'Token expired') {
    super(message);
    this.name = 'TokenExpiredError';
  }
}

// Thread Errors
export class ThreadNotFoundError extends Error {
  constructor(message: string = 'Thread not found') {
    super(message);
    this.name = 'ThreadNotFoundError';
  }
}

export class ThreadAccessDeniedError extends Error {
  constructor(message: string = 'Thread access denied') {
    super(message);
    this.name = 'ThreadAccessDeniedError';
  }
}

export class ThreadStorageError extends Error {
  constructor(message: string = 'Thread storage error') {
    super(message);
    this.name = 'ThreadStorageError';
  }
}

// Team Errors
export class TeamError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'TeamError';
  }
}

export class TeamNotFoundError extends TeamError {
  constructor(message: string = 'Team not found') {
    super(message);
    this.name = 'TeamNotFoundError';
  }
}

export class TeamAccessDeniedError extends TeamError {
  constructor(message: string = 'Team access denied') {
    super(message);
    this.name = 'TeamAccessDeniedError';
  }
}

export class TeamLimitExceededError extends TeamError {
  constructor(message: string = 'Team limit exceeded') {
    super(message);
    this.name = 'TeamLimitExceededError';
  }
}

export class InviteError extends TeamError {
  constructor(message: string) {
    super(message);
    this.name = 'InviteError';
  }
}

export class InviteNotFoundError extends InviteError {
  constructor(message: string = 'Invite not found') {
    super(message);
    this.name = 'InviteNotFoundError';
  }
}

export class InviteExpiredError extends InviteError {
  constructor(message: string = 'Invite expired') {
    super(message);
    this.name = 'InviteExpiredError';
  }
}

// ============================================================================
// PAYMENT & SUBSCRIPTION TYPES (For Stripe Integration)
// ============================================================================

export interface SubscriptionStatus {
  is_active: boolean;
  plan: string;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  status: string; // Stripe subscription status
  trial_end: string | null;
}

export interface PaymentHistory {
  id: string;
  amount: number;
  currency: string;
  status: string; // "succeeded", "pending", "failed"
  created: string;
  description: string;
  invoice_url: string | null;
  payment_method_brand: string | null;
  payment_method_last4: string | null;
}

export interface CreatePaymentIntentRequest {
  amount: number;
  currency: string;
  plan_id: string;
}

export interface CreatePaymentIntentResponse {
  client_secret: string;
  payment_intent_id: string;
}

// ============================================================================
// GENERIC API RESPONSE TYPES
// ============================================================================

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
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface ErrorResponse {
  detail: string;
  error_code?: string;
  field_errors?: Record<string, string[]>;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export type SortOrder = 'asc' | 'desc';

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

// Type guards for error handling
export const isApiError = (error: any): error is { status: number; message: string } => {
  return error && typeof error.status === 'number' && typeof error.message === 'string';
};

export const isValidationError = (error: any): error is { field_errors: Record<string, string[]> } => {
  return error && error.field_errors && typeof error.field_errors === 'object';
};

// ============================================================================
// RE-EXPORT EXISTING TYPES FOR COMPATIBILITY
// ============================================================================

// Re-export key types from the existing index.ts for backward compatibility
export type { 
  User as LegacyUser,
  Thread as LegacyThread,
  Tweet as LegacyTweet,
  GenerateThreadRequest as LegacyGenerateThreadRequest,
  GenerateThreadResponse as LegacyGenerateThreadResponse,
  UsageStats,
  AnalyticsDashboard,
  TeamMember as LegacyTeamMember,
  Team as LegacyTeam,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  ButtonProps,
  InputProps,
  PaymentIntent,
  SubscriptionPlan,
  ApiError,
  Template as LegacyTemplate,
  TemplateCategory as LegacyTemplateCategory,
  Theme,
  AppState
} from './index';