"""
Analytics data models for Threadr thread performance tracking.
Designed for both relational (PostgreSQL) and NoSQL (Redis/MongoDB) storage.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from enum import Enum


class MetricType(str, Enum):
    """Types of metrics we track"""
    ENGAGEMENT = "engagement"
    REACH = "reach" 
    CONVERSION = "conversion"
    BEHAVIOR = "behavior"


class DataSource(str, Enum):
    """Where analytics data comes from"""
    TWITTER_API = "twitter_api"
    WEBHOOK = "webhook"
    MANUAL = "manual"
    ESTIMATED = "estimated"


class ThreadAnalytics(BaseModel):
    """Core analytics model for a thread"""
    
    # Identifiers
    thread_id: str = Field(..., description="Unique thread identifier")
    user_id: str = Field(..., description="User who created the thread")
    twitter_thread_id: Optional[str] = Field(None, description="X/Twitter thread ID if posted")
    
    # Thread Metadata
    title: str = Field(..., description="Thread title/topic")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    posted_at: Optional[datetime] = Field(None, description="When thread was posted to X")
    thread_length: int = Field(..., description="Number of tweets in thread")
    content_source: Optional[str] = Field(None, description="Original article URL")
    
    # Primary Engagement Metrics
    impressions: int = Field(default=0, description="Total thread views")
    reach: int = Field(default=0, description="Unique users who saw thread")
    likes: int = Field(default=0, description="Total likes across all tweets")
    retweets: int = Field(default=0, description="Total retweets")
    replies: int = Field(default=0, description="Total replies")
    bookmarks: int = Field(default=0, description="Total bookmarks")
    quotes: int = Field(default=0, description="Quote tweets")
    
    # Calculated Metrics
    engagement_rate: float = Field(default=0.0, description="Total engagement / impressions")
    completion_rate: float = Field(default=0.0, description="Users who read full thread")
    click_through_rate: float = Field(default=0.0, description="Profile visits / impressions")
    
    # Business Impact
    profile_visits: int = Field(default=0, description="Profile clicks from thread")
    link_clicks: int = Field(default=0, description="External link clicks")
    follower_growth: int = Field(default=0, description="New followers from thread")
    
    # Performance Tracking
    peak_engagement_hour: Optional[int] = Field(None, description="Hour with most engagement (0-23)")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data_sources: List[DataSource] = Field(default_factory=list, description="How data was collected")
    
    # Thread Structure Analytics
    hook_performance: float = Field(default=0.0, description="First tweet engagement vs average")
    drop_off_points: List[int] = Field(default_factory=list, description="Tweet numbers where users drop off")
    best_performing_tweet: Optional[int] = Field(None, description="Tweet number with highest engagement")


class TweetMetrics(BaseModel):
    """Individual tweet performance within a thread"""
    
    tweet_id: str = Field(..., description="Individual tweet ID")
    thread_id: str = Field(..., description="Parent thread ID")
    position: int = Field(..., description="Position in thread (1-based)")
    
    # Tweet Content
    content: str = Field(..., description="Tweet text content")
    character_count: int = Field(..., description="Characters used")
    has_media: bool = Field(default=False, description="Contains images/video")
    has_links: bool = Field(default=False, description="Contains external links")
    has_hashtags: bool = Field(default=False, description="Contains hashtags")
    
    # Individual Metrics
    impressions: int = Field(default=0)
    likes: int = Field(default=0)
    retweets: int = Field(default=0)
    replies: int = Field(default=0)
    bookmarks: int = Field(default=0)
    
    # Performance Indicators
    engagement_rate: float = Field(default=0.0)
    is_hook: bool = Field(default=False, description="Is this the first tweet")
    is_cta: bool = Field(default=False, description="Contains call-to-action")
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AnalyticsSnapshot(BaseModel):
    """Time-series snapshot for tracking metrics over time"""
    
    snapshot_id: str = Field(..., description="Unique snapshot identifier")
    thread_id: str = Field(..., description="Thread being tracked")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Snapshot Data
    metrics: Dict[str, Any] = Field(..., description="Metric values at this time")
    data_source: DataSource = Field(..., description="How this data was collected")
    
    # Context
    hours_since_posted: Optional[float] = Field(None, description="Hours since thread was posted")
    day_of_week: int = Field(..., description="0=Monday, 6=Sunday")
    hour_of_day: int = Field(..., description="0-23")


class UserAnalyticsSummary(BaseModel):
    """Aggregated analytics for a user across all threads"""
    
    user_id: str = Field(..., description="User identifier")
    period_start: datetime = Field(..., description="Analytics period start")
    period_end: datetime = Field(..., description="Analytics period end")
    
    # Summary Stats
    total_threads: int = Field(default=0)
    total_impressions: int = Field(default=0)
    total_engagement: int = Field(default=0)
    average_engagement_rate: float = Field(default=0.0)
    
    # Performance Insights
    best_performing_thread: Optional[str] = Field(None, description="Thread ID with highest engagement")
    optimal_posting_hour: Optional[int] = Field(None, description="Best hour to post (0-23)")
    optimal_thread_length: Optional[int] = Field(None, description="Best performing thread length")
    
    # Growth Metrics
    follower_growth: int = Field(default=0)
    profile_visits: int = Field(default=0)
    total_reach: int = Field(default=0)
    
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AnalyticsGoal(BaseModel):
    """User-defined goals and targets"""
    
    goal_id: str = Field(..., description="Unique goal identifier")
    user_id: str = Field(..., description="User who set the goal")
    
    # Goal Definition
    metric_name: str = Field(..., description="What metric to track (engagement_rate, impressions, etc.)")
    target_value: float = Field(..., description="Target value to achieve")
    timeframe_days: int = Field(..., description="Days to achieve goal")
    
    # Progress Tracking
    current_value: float = Field(default=0.0)
    progress_percentage: float = Field(default=0.0)
    is_achieved: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deadline: datetime = Field(..., description="When goal should be achieved")


# Database Schema (SQL DDL for reference)
SQL_SCHEMA = """
-- Thread Analytics Main Table
CREATE TABLE thread_analytics (
    thread_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    twitter_thread_id VARCHAR(50),
    title TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    posted_at TIMESTAMP WITH TIME ZONE,
    thread_length INTEGER NOT NULL,
    content_source TEXT,
    
    -- Engagement Metrics
    impressions INTEGER DEFAULT 0,
    reach INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    retweets INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    bookmarks INTEGER DEFAULT 0,
    quotes INTEGER DEFAULT 0,
    
    -- Calculated Metrics
    engagement_rate DECIMAL(5,2) DEFAULT 0.00,
    completion_rate DECIMAL(5,2) DEFAULT 0.00,
    click_through_rate DECIMAL(5,2) DEFAULT 0.00,
    
    -- Business Impact
    profile_visits INTEGER DEFAULT 0,
    link_clicks INTEGER DEFAULT 0,
    follower_growth INTEGER DEFAULT 0,
    
    -- Performance Data
    peak_engagement_hour INTEGER,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    hook_performance DECIMAL(5,2) DEFAULT 0.00,
    best_performing_tweet INTEGER,
    
    INDEX idx_user_created (user_id, created_at),
    INDEX idx_posted_at (posted_at),
    INDEX idx_engagement_rate (engagement_rate DESC)
);

-- Individual Tweet Metrics
CREATE TABLE tweet_metrics (
    tweet_id VARCHAR(50) PRIMARY KEY,
    thread_id VARCHAR(50) NOT NULL,
    position INTEGER NOT NULL,
    content TEXT NOT NULL,
    character_count INTEGER NOT NULL,
    has_media BOOLEAN DEFAULT FALSE,
    has_links BOOLEAN DEFAULT FALSE,
    has_hashtags BOOLEAN DEFAULT FALSE,
    
    impressions INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    retweets INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    bookmarks INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,2) DEFAULT 0.00,
    
    is_hook BOOLEAN DEFAULT FALSE,
    is_cta BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    FOREIGN KEY (thread_id) REFERENCES thread_analytics(thread_id),
    INDEX idx_thread_position (thread_id, position)
);

-- Time Series Snapshots
CREATE TABLE analytics_snapshots (
    snapshot_id VARCHAR(50) PRIMARY KEY,
    thread_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metrics JSONB NOT NULL,
    data_source VARCHAR(20) NOT NULL,
    hours_since_posted DECIMAL(10,2),
    day_of_week INTEGER NOT NULL,
    hour_of_day INTEGER NOT NULL,
    
    FOREIGN KEY (thread_id) REFERENCES thread_analytics(thread_id),
    INDEX idx_thread_timestamp (thread_id, timestamp),
    INDEX idx_timestamp (timestamp)
);

-- User Summary Analytics
CREATE TABLE user_analytics_summary (
    user_id VARCHAR(50) NOT NULL,
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    
    total_threads INTEGER DEFAULT 0,
    total_impressions INTEGER DEFAULT 0,
    total_engagement INTEGER DEFAULT 0,
    average_engagement_rate DECIMAL(5,2) DEFAULT 0.00,
    
    best_performing_thread VARCHAR(50),
    optimal_posting_hour INTEGER,
    optimal_thread_length INTEGER,
    
    follower_growth INTEGER DEFAULT 0,
    profile_visits INTEGER DEFAULT 0,
    total_reach INTEGER DEFAULT 0,
    
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (user_id, period_start),
    INDEX idx_updated (updated_at)
);
"""