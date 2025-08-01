"""
Analytics models for thread performance tracking
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class MetricPeriod(str, Enum):
    """Time periods for analytics aggregation"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    ALL_TIME = "all_time"


class EngagementType(str, Enum):
    """Types of engagement actions"""
    IMPRESSION = "impression"
    LIKE = "like"
    RETWEET = "retweet"
    REPLY = "reply"
    BOOKMARK = "bookmark"
    QUOTE = "quote"
    PROFILE_VISIT = "profile_visit"
    LINK_CLICK = "link_click"
    FOLLOW = "follow"


class ContentType(str, Enum):
    """Types of thread content"""
    EDUCATIONAL = "educational"
    NEWS = "news"
    PERSONAL = "personal"
    PROMOTIONAL = "promotional"
    ENTERTAINMENT = "entertainment"
    TECHNICAL = "technical"
    OTHER = "other"


class TweetMetrics(BaseModel):
    """Metrics for individual tweets in a thread"""
    tweet_id: str
    position: int  # Position in thread (1-based)
    content: str
    character_count: int
    
    # Engagement metrics
    impressions: int = 0
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    bookmarks: int = 0
    quotes: int = 0
    
    # Calculated metrics
    engagement_rate: float = 0.0
    drop_off_rate: Optional[float] = None  # % who didn't continue to next tweet
    
    # Timing
    posted_at: datetime
    peak_hour: Optional[int] = None  # Hour with most engagement
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ThreadAnalytics(BaseModel):
    """Complete analytics for a thread"""
    thread_id: str
    user_id: str
    created_at: datetime
    
    # Thread metadata
    title: str
    source_url: Optional[str] = None
    content_type: ContentType = ContentType.OTHER
    tweet_count: int
    total_character_count: int
    
    # Overall metrics
    total_impressions: int = 0
    total_engagements: int = 0
    engagement_rate: float = 0.0
    
    # Detailed engagement
    total_likes: int = 0
    total_retweets: int = 0
    total_replies: int = 0
    total_bookmarks: int = 0
    total_quotes: int = 0
    
    # Business metrics
    profile_visits: int = 0
    link_clicks: int = 0
    new_followers: int = 0
    
    # Performance metrics
    thread_completion_rate: float = 0.0  # % who viewed last tweet
    avg_time_on_thread: float = 0.0  # seconds
    virality_score: float = 0.0  # 0-100 score
    
    # Tweet-level metrics
    tweet_metrics: List[TweetMetrics] = []
    
    # Best performing elements
    best_tweet_position: Optional[int] = None
    worst_tweet_position: Optional[int] = None
    optimal_length: Optional[int] = None  # Optimal thread length based on engagement
    
    # Time analysis
    posted_at: datetime
    peak_engagement_hour: Optional[int] = None
    peak_engagement_day: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TimeSeriesDataPoint(BaseModel):
    """Single data point in a time series"""
    timestamp: datetime
    value: float
    period: MetricPeriod
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MetricSummary(BaseModel):
    """Summary of a metric with period comparison"""
    current_value: float
    previous_value: float
    change_percent: float
    trend: str  # "up", "down", "stable"
    period: MetricPeriod


class DashboardSummary(BaseModel):
    """Summary data for analytics dashboard"""
    user_id: str
    period: MetricPeriod
    generated_at: datetime
    
    # Key metrics with comparisons
    total_impressions: MetricSummary
    engagement_rate: MetricSummary
    follower_growth: MetricSummary
    avg_thread_performance: MetricSummary
    
    # Thread statistics
    total_threads: int
    threads_this_period: int
    best_performing_thread: Optional[Dict[str, Any]] = None
    worst_performing_thread: Optional[Dict[str, Any]] = None
    
    # Content analysis
    content_type_breakdown: Dict[str, float]  # content_type -> percentage
    optimal_posting_times: List[Dict[str, Any]]  # day/hour combinations
    
    # Time series data for charts
    impressions_over_time: List[TimeSeriesDataPoint] = []
    engagement_rate_over_time: List[TimeSeriesDataPoint] = []
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ThreadComparison(BaseModel):
    """Comparison between two threads"""
    thread_a: ThreadAnalytics
    thread_b: ThreadAnalytics
    
    # Comparison metrics
    impressions_diff: float
    engagement_rate_diff: float
    completion_rate_diff: float
    virality_score_diff: float
    
    # Winner indicators
    better_performer: str  # thread_id of better performer
    key_differences: List[str]  # Key insights about differences


class InsightRecommendation(BaseModel):
    """AI-generated insight or recommendation"""
    insight_id: str
    category: str  # "timing", "content", "engagement", "growth"
    priority: str  # "high", "medium", "low"
    
    title: str
    description: str
    action_items: List[str]
    
    # Supporting data
    confidence_score: float  # 0-1
    based_on_threads: List[str]  # thread_ids used for this insight
    potential_impact: str  # Expected improvement if implemented
    
    generated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BenchmarkData(BaseModel):
    """Industry benchmark data for comparison"""
    category: ContentType
    period: MetricPeriod
    
    # Percentile data
    avg_impressions_p50: float  # Median
    avg_impressions_p75: float  # 75th percentile
    avg_impressions_p90: float  # 90th percentile
    
    avg_engagement_rate_p50: float
    avg_engagement_rate_p75: float
    avg_engagement_rate_p90: float
    
    avg_thread_length: float
    avg_completion_rate: float
    
    # User's position
    user_percentile_impressions: Optional[float] = None
    user_percentile_engagement: Optional[float] = None


class AnalyticsExport(BaseModel):
    """Data structure for exporting analytics"""
    user_id: str
    export_date: datetime
    period: MetricPeriod
    
    # Summary metrics
    summary: DashboardSummary
    
    # Detailed thread data
    threads: List[ThreadAnalytics]
    
    # Insights and recommendations
    insights: List[InsightRecommendation]
    
    # Benchmark data
    benchmarks: Optional[BenchmarkData] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }