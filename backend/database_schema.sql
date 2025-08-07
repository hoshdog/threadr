-- ============================================================================
-- Threadr PostgreSQL Database Schema
-- Production-ready schema with proper indexes, constraints, and audit fields
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search performance

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'premium', 'admin')),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    
    -- User metadata
    login_count INTEGER NOT NULL DEFAULT 0,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    last_failed_login TIMESTAMP WITH TIME ZONE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    -- Email verification
    is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    email_verification_expires TIMESTAMP WITH TIME ZONE,
    
    -- Password reset
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP WITH TIME ZONE,
    
    -- Additional metadata (JSON for flexibility)
    metadata JSONB NOT NULL DEFAULT '{}',
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Teams table
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    
    -- Owner and billing
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    plan VARCHAR(20) NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'starter', 'pro', 'enterprise')),
    billing_email VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    
    -- Limits and configuration
    max_members INTEGER NOT NULL DEFAULT 5,
    max_monthly_threads INTEGER NOT NULL DEFAULT 100,
    
    -- Settings and features (JSON for flexibility)
    settings JSONB NOT NULL DEFAULT '{}',
    features JSONB NOT NULL DEFAULT '{}',
    
    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    suspended_at TIMESTAMP WITH TIME ZONE,
    suspended_reason TEXT,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT teams_slug_valid CHECK (slug ~ '^[a-z0-9-]+$' AND length(slug) >= 3)
);

-- Team memberships table
CREATE TABLE team_memberships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('owner', 'admin', 'editor', 'viewer')),
    
    -- Granular permissions (JSON array of permission strings)
    permissions JSONB NOT NULL DEFAULT '[]',
    
    -- Status and activity
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_activity_at TIMESTAMP WITH TIME ZONE,
    thread_count INTEGER NOT NULL DEFAULT 0,
    
    -- Audit fields
    joined_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint
    UNIQUE(team_id, user_id)
);

-- Team invitations table
CREATE TABLE team_invites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    invited_by_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Invitation details
    email VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'editor', 'viewer')),
    token UUID NOT NULL DEFAULT uuid_generate_v4(),
    message TEXT,
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'expired', 'revoked')),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '7 days'),
    accepted_at TIMESTAMP WITH TIME ZONE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    
    -- Unique active invite per email per team
    UNIQUE(team_id, email, status)
);

-- Threads table (main content storage)
CREATE TABLE threads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,  -- NULL for personal threads
    
    -- Thread content
    title VARCHAR(200) NOT NULL,
    original_content TEXT NOT NULL,
    tweets JSONB NOT NULL,  -- Array of tweet objects
    
    -- Metadata
    metadata JSONB NOT NULL DEFAULT '{}',
    source_url TEXT,
    source_type VARCHAR(20) NOT NULL DEFAULT 'text' CHECK (source_type IN ('url', 'text')),
    ai_model VARCHAR(50) NOT NULL DEFAULT 'gpt-3.5-turbo',
    generation_time_ms INTEGER,
    content_length INTEGER,
    tags TEXT[] DEFAULT '{}',
    
    -- Usage tracking
    view_count INTEGER NOT NULL DEFAULT 0,
    copy_count INTEGER NOT NULL DEFAULT 0,
    
    -- User preferences
    is_favorite BOOLEAN NOT NULL DEFAULT FALSE,
    is_archived BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Team collaboration fields
    status VARCHAR(20) DEFAULT 'published' CHECK (status IN ('draft', 'submitted', 'approved', 'rejected', 'published')),
    assigned_to_id UUID REFERENCES users(id),
    
    -- Approval workflow
    submitted_at TIMESTAMP WITH TIME ZONE,
    submitted_by_id UUID REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    reviewed_by_id UUID REFERENCES users(id),
    review_notes TEXT,
    
    -- Collaboration
    collaborators UUID[] DEFAULT '{}',  -- Array of user IDs
    mentions UUID[] DEFAULT '{}',       -- Array of mentioned user IDs
    
    -- Version control
    version INTEGER NOT NULL DEFAULT 1,
    parent_version_id UUID REFERENCES threads(id),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT threads_tweets_valid CHECK (jsonb_array_length(tweets) > 0)
);

-- Subscriptions table (Stripe integration)
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    
    -- Stripe details
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255) NOT NULL,
    stripe_price_id VARCHAR(255) NOT NULL,
    stripe_product_id VARCHAR(255) NOT NULL,
    
    -- Subscription details
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'canceled', 'past_due', 'unpaid', 'trialing')),
    plan_name VARCHAR(50) NOT NULL,
    billing_cycle VARCHAR(20) NOT NULL CHECK (billing_cycle IN ('monthly', 'yearly', 'one_time')),
    
    -- Pricing
    amount_cents INTEGER NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    
    -- Dates
    current_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    current_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE,
    canceled_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    trial_start TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    
    -- Premium access tracking
    premium_expires_at TIMESTAMP WITH TIME ZONE,
    is_premium BOOLEAN GENERATED ALWAYS AS (
        status = 'active' AND 
        (premium_expires_at IS NULL OR premium_expires_at > CURRENT_TIMESTAMP)
    ) STORED,
    
    -- Metadata
    metadata JSONB NOT NULL DEFAULT '{}',
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT subscriptions_user_or_team CHECK (
        (user_id IS NOT NULL AND team_id IS NULL) OR 
        (user_id IS NULL AND team_id IS NOT NULL)
    )
);

-- Usage tracking table (rate limiting and analytics)
CREATE TABLE usage_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    ip_address INET,
    
    -- Usage details
    endpoint VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,  -- 'generate_thread', 'api_call', etc.
    
    -- Tracking data
    daily_count INTEGER NOT NULL DEFAULT 1,
    monthly_count INTEGER NOT NULL DEFAULT 1,
    date_bucket DATE NOT NULL DEFAULT CURRENT_DATE,
    month_bucket DATE NOT NULL DEFAULT DATE_TRUNC('month', CURRENT_DATE),
    
    -- Request metadata
    user_agent TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    
    -- Timestamps
    first_request_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_request_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint for efficient upserts
    UNIQUE(user_id, ip_address, endpoint, date_bucket)
);

-- Sessions table (JWT token management)
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Session details
    session_token VARCHAR(255) NOT NULL UNIQUE,
    refresh_token VARCHAR(255) UNIQUE,
    device_id VARCHAR(255),
    
    -- Device/client information
    ip_address INET,
    user_agent TEXT,
    device_name VARCHAR(100),
    browser_name VARCHAR(50),
    os_name VARCHAR(50),
    
    -- Session status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_remember_me BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================================
-- ANALYTICS TABLES
-- ============================================================================

-- Thread analytics
CREATE TABLE thread_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    thread_id UUID NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Basic metrics
    total_impressions BIGINT NOT NULL DEFAULT 0,
    total_engagements BIGINT NOT NULL DEFAULT 0,
    engagement_rate DECIMAL(5,4) NOT NULL DEFAULT 0.0000,
    
    -- Detailed engagement metrics
    total_likes BIGINT NOT NULL DEFAULT 0,
    total_retweets BIGINT NOT NULL DEFAULT 0,
    total_replies BIGINT NOT NULL DEFAULT 0,
    total_bookmarks BIGINT NOT NULL DEFAULT 0,
    total_quotes BIGINT NOT NULL DEFAULT 0,
    
    -- Business metrics
    profile_visits BIGINT NOT NULL DEFAULT 0,
    link_clicks BIGINT NOT NULL DEFAULT 0,
    new_followers INTEGER NOT NULL DEFAULT 0,
    
    -- Performance metrics
    thread_completion_rate DECIMAL(5,4) NOT NULL DEFAULT 0.0000,
    avg_time_on_thread DECIMAL(8,2) NOT NULL DEFAULT 0.00,  -- seconds
    virality_score DECIMAL(5,2) NOT NULL DEFAULT 0.00,     -- 0-100 score
    
    -- Content analysis
    content_type VARCHAR(20) DEFAULT 'other' CHECK (content_type IN ('educational', 'news', 'personal', 'promotional', 'entertainment', 'technical', 'other')),
    
    -- Performance insights
    best_tweet_position INTEGER,
    worst_tweet_position INTEGER,
    optimal_length INTEGER,
    
    -- Time analysis
    posted_at TIMESTAMP WITH TIME ZONE,
    peak_engagement_hour INTEGER CHECK (peak_engagement_hour BETWEEN 0 AND 23),
    peak_engagement_day VARCHAR(10),
    
    -- Tweet-level metrics (JSON array)
    tweet_metrics JSONB NOT NULL DEFAULT '[]',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint
    UNIQUE(thread_id)
);

-- Time-series analytics data
CREATE TABLE analytics_timeseries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    thread_id UUID REFERENCES threads(id) ON DELETE CASCADE,  -- NULL for aggregate data
    
    -- Metric details
    metric_name VARCHAR(50) NOT NULL,  -- 'impressions', 'engagement_rate', etc.
    metric_value DECIMAL(12,4) NOT NULL,
    
    -- Time dimensions
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    period_type VARCHAR(10) NOT NULL CHECK (period_type IN ('hour', 'day', 'week', 'month')),
    date_bucket DATE NOT NULL,
    hour_bucket TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    metadata JSONB NOT NULL DEFAULT '{}',
    
    -- Index for efficient time-series queries
    INDEX CONCURRENTLY idx_analytics_timeseries_user_metric_time ON analytics_timeseries 
    (user_id, metric_name, timestamp DESC)
);

-- Team activity log
CREATE TABLE team_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Activity details
    action VARCHAR(50) NOT NULL,        -- 'thread.created', 'member.invited', etc.
    resource_type VARCHAR(20) NOT NULL, -- 'thread', 'member', 'team'
    resource_id UUID,
    
    -- Context
    details JSONB NOT NULL DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    
    -- Timestamp
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Users indexes
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_users_status ON users(status) WHERE status != 'active';
CREATE INDEX CONCURRENTLY idx_users_created_at ON users(created_at);
CREATE INDEX CONCURRENTLY idx_users_email_verification ON users(email_verification_token) WHERE email_verification_token IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_users_password_reset ON users(password_reset_token) WHERE password_reset_token IS NOT NULL;

-- Teams indexes
CREATE INDEX CONCURRENTLY idx_teams_owner ON teams(owner_id);
CREATE INDEX CONCURRENTLY idx_teams_slug ON teams(slug);
CREATE INDEX CONCURRENTLY idx_teams_plan ON teams(plan);
CREATE INDEX CONCURRENTLY idx_teams_active ON teams(is_active) WHERE is_active = true;

-- Team memberships indexes
CREATE INDEX CONCURRENTLY idx_team_memberships_team ON team_memberships(team_id);
CREATE INDEX CONCURRENTLY idx_team_memberships_user ON team_memberships(user_id);
CREATE INDEX CONCURRENTLY idx_team_memberships_active ON team_memberships(team_id, user_id) WHERE is_active = true;
CREATE INDEX CONCURRENTLY idx_team_memberships_activity ON team_memberships(last_activity_at DESC);

-- Team invites indexes
CREATE INDEX CONCURRENTLY idx_team_invites_team ON team_invites(team_id);
CREATE INDEX CONCURRENTLY idx_team_invites_email ON team_invites(email);
CREATE INDEX CONCURRENTLY idx_team_invites_token ON team_invites(token);
CREATE INDEX CONCURRENTLY idx_team_invites_status ON team_invites(status, expires_at) WHERE status = 'pending';

-- Threads indexes
CREATE INDEX CONCURRENTLY idx_threads_user ON threads(user_id);
CREATE INDEX CONCURRENTLY idx_threads_team ON threads(team_id) WHERE team_id IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_threads_created ON threads(created_at DESC);
CREATE INDEX CONCURRENTLY idx_threads_updated ON threads(updated_at DESC);
CREATE INDEX CONCURRENTLY idx_threads_favorites ON threads(user_id, is_favorite) WHERE is_favorite = true;
CREATE INDEX CONCURRENTLY idx_threads_archived ON threads(user_id, is_archived);
CREATE INDEX CONCURRENTLY idx_threads_status ON threads(status);
CREATE INDEX CONCURRENTLY idx_threads_source_type ON threads(source_type);
CREATE INDEX CONCURRENTLY idx_threads_tags ON threads USING GIN(tags);
CREATE INDEX CONCURRENTLY idx_threads_title_search ON threads USING GIN(to_tsvector('english', title));
CREATE INDEX CONCURRENTLY idx_threads_content_search ON threads USING GIN(to_tsvector('english', original_content));

-- Subscriptions indexes
CREATE INDEX CONCURRENTLY idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX CONCURRENTLY idx_subscriptions_team ON subscriptions(team_id) WHERE team_id IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_subscriptions_stripe_id ON subscriptions(stripe_subscription_id);
CREATE INDEX CONCURRENTLY idx_subscriptions_status ON subscriptions(status);
CREATE INDEX CONCURRENTLY idx_subscriptions_premium ON subscriptions(premium_expires_at) WHERE is_premium = true;

-- Usage tracking indexes
CREATE INDEX CONCURRENTLY idx_usage_tracking_user ON usage_tracking(user_id);
CREATE INDEX CONCURRENTLY idx_usage_tracking_ip ON usage_tracking(ip_address);
CREATE INDEX CONCURRENTLY idx_usage_tracking_date ON usage_tracking(date_bucket DESC);
CREATE INDEX CONCURRENTLY idx_usage_tracking_month ON usage_tracking(month_bucket DESC);
CREATE INDEX CONCURRENTLY idx_usage_tracking_endpoint ON usage_tracking(endpoint, date_bucket);

-- Sessions indexes
CREATE INDEX CONCURRENTLY idx_user_sessions_user ON user_sessions(user_id);
CREATE INDEX CONCURRENTLY idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX CONCURRENTLY idx_user_sessions_refresh ON user_sessions(refresh_token) WHERE refresh_token IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_user_sessions_active ON user_sessions(user_id, is_active) WHERE is_active = true;
CREATE INDEX CONCURRENTLY idx_user_sessions_expires ON user_sessions(expires_at) WHERE is_active = true;

-- Analytics indexes
CREATE INDEX CONCURRENTLY idx_thread_analytics_thread ON thread_analytics(thread_id);
CREATE INDEX CONCURRENTLY idx_thread_analytics_user ON thread_analytics(user_id);
CREATE INDEX CONCURRENTLY idx_thread_analytics_engagement ON thread_analytics(engagement_rate DESC);
CREATE INDEX CONCURRENTLY idx_thread_analytics_impressions ON thread_analytics(total_impressions DESC);

-- Team activities indexes
CREATE INDEX CONCURRENTLY idx_team_activities_team ON team_activities(team_id);
CREATE INDEX CONCURRENTLY idx_team_activities_user ON team_activities(user_id);
CREATE INDEX CONCURRENTLY idx_team_activities_timestamp ON team_activities(timestamp DESC);
CREATE INDEX CONCURRENTLY idx_team_activities_action ON team_activities(action, timestamp DESC);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add update triggers to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_team_memberships_updated_at BEFORE UPDATE ON team_memberships 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_threads_updated_at BEFORE UPDATE ON threads 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_thread_analytics_updated_at BEFORE UPDATE ON thread_analytics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    UPDATE user_sessions 
    SET is_active = false, revoked_at = CURRENT_TIMESTAMP
    WHERE is_active = true AND expires_at < CURRENT_TIMESTAMP;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up expired invites
CREATE OR REPLACE FUNCTION cleanup_expired_invites()
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE team_invites 
    SET status = 'expired'
    WHERE status = 'pending' AND expires_at < CURRENT_TIMESTAMP;
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- BACKUP STRATEGIES
-- ============================================================================

-- Daily backup script (to be run via cron)
-- pg_dump --verbose --clean --no-owner --no-privileges --format=custom 
--   --file=threadr_backup_$(date +%Y%m%d_%H%M%S).dump threadr_production

-- Point-in-time recovery setup
-- Enable WAL archiving in postgresql.conf:
-- wal_level = replica
-- archive_mode = on
-- archive_command = 'cp %p /backup/wal_archive/%f'

-- ============================================================================
-- PARTITIONING FOR LARGE TABLES
-- ============================================================================

-- Partition analytics_timeseries by month for better performance
-- This should be implemented when data volume grows significantly

-- CREATE TABLE analytics_timeseries_y2025m01 PARTITION OF analytics_timeseries
-- FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- CREATE TABLE analytics_timeseries_y2025m02 PARTITION OF analytics_timeseries
-- FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- ============================================================================
-- REPLICATION SETUP
-- ============================================================================

-- Master-slave replication configuration
-- On primary server in postgresql.conf:
-- wal_level = replica
-- max_wal_senders = 3
-- wal_keep_segments = 64

-- Create replication user:
-- CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replication_password';

-- ============================================================================
-- MONITORING QUERIES
-- ============================================================================

-- Query to monitor connection usage
-- SELECT count(*) as active_connections, 
--        max_conn - count(*) as available_connections
-- FROM pg_stat_activity, (SELECT setting::int as max_conn FROM pg_settings WHERE name = 'max_connections') mc;

-- Query to monitor table sizes
-- SELECT schemaname, tablename, 
--        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
-- FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Query to monitor index usage
-- SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch 
-- FROM pg_stat_user_indexes ORDER BY idx_scan DESC;

-- ============================================================================
-- SECURITY SETTINGS
-- ============================================================================

-- Row Level Security examples (uncomment and customize as needed)
-- ALTER TABLE threads ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY threads_user_policy ON threads FOR ALL TO authenticated_users USING (user_id = current_user_id());

-- Grant appropriate permissions
-- GRANT CONNECT ON DATABASE threadr TO threadr_app_user;
-- GRANT USAGE ON SCHEMA public TO threadr_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO threadr_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO threadr_app_user;