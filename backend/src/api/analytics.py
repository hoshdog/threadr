"""
Analytics API endpoints for Threadr thread performance tracking.
Provides comprehensive analytics data and insights for the dashboard.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from ..models.analytics import ThreadAnalytics, TweetMetrics, AnalyticsSnapshot
from ..services.analytics_comparison import AnalyticsComparison, ComparisonType
from ..services.insights_engine import InsightsEngine
from ..utils.mock_analytics_data import MockAnalyticsGenerator


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# Request/Response Models

class AnalyticsPeriod(BaseModel):
    """Time period for analytics queries"""
    days: int = Field(default=30, ge=1, le=365, description="Number of days to analyze")
    end_date: Optional[datetime] = Field(default=None, description="End date (defaults to now)")


class DashboardResponse(BaseModel):
    """Dashboard analytics response"""
    summary: Dict[str, Any]
    threads: List[Dict[str, Any]]
    charts: Dict[str, Any]
    insights: Dict[str, List[Dict[str, Any]]]


class ThreadComparisonRequest(BaseModel):
    """Thread comparison request"""
    thread_id_1: str
    thread_id_2: str


class InsightsResponse(BaseModel):
    """Insights response"""
    insights: List[Dict[str, Any]]
    summary: Dict[str, Any]


class BenchmarkResponse(BaseModel):
    """Benchmark comparison response"""
    benchmarks: List[Dict[str, Any]]
    user_score: float
    industry_position: str


# Dependency functions (in production these would connect to actual databases)

async def get_user_analytics_data(user_id: str) -> List[ThreadAnalytics]:
    """Get analytics data for a user (mock implementation)"""
    # In production, this would query the database
    generator = MockAnalyticsGenerator()
    return generator.generate_user_threads(user_id, num_threads=50, days_back=90)


async def get_tweet_metrics_data(user_id: str) -> List[TweetMetrics]:
    """Get tweet-level metrics data (mock implementation)"""
    # In production, this would query the database
    generator = MockAnalyticsGenerator()
    threads = await get_user_analytics_data(user_id)
    
    all_tweets = []
    for thread in threads[:10]:  # Generate tweet data for first 10 threads
        tweets = generator.generate_tweet_metrics(thread)
        all_tweets.extend(tweets)
    
    return all_tweets


# Main Analytics Endpoints

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard_analytics(
    user_id: str = Query(..., description="User ID to get analytics for"),
    period: str = Query(default="30d", regex="^(7d|30d|90d|1y)$", description="Time period"),
    comparison: str = Query(default="previous", regex="^(none|previous|last_year)$", description="Comparison period")
):
    """
    Get comprehensive dashboard analytics data including:
    - Summary metrics with period-over-period comparisons
    - Thread performance data
    - Chart data for visualizations
    - AI-generated insights and recommendations
    """
    
    # Parse period
    period_days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}[period]
    
    # Get analytics data
    threads = await get_user_analytics_data(user_id)
    tweets = await get_tweet_metrics_data(user_id)
    
    # Filter to requested period
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=period_days)
    period_threads = [
        t for t in threads 
        if start_date <= t.created_at <= end_date
    ]
    
    if not period_threads:
        raise HTTPException(status_code=404, detail="No analytics data found for this period")
    
    # Generate dashboard data using mock generator for consistency
    generator = MockAnalyticsGenerator()
    dashboard_data = generator.generate_dashboard_data(user_id)
    
    # Add insights using the insights engine
    insights_engine = InsightsEngine(threads, tweets)
    insights = insights_engine.generate_user_insights(user_id, period_days)
    insights_summary = insights_engine.get_insights_summary(insights)
    
    # Format insights for response
    formatted_insights = {
        "performance": [
            {
                "id": insight.id,
                "message": insight.message,
                "impact": insight.impact_description
            }
            for insight in insights if insight.type.value == "performance"
        ][:5],  # Top 5 performance insights
        "optimization": [
            {
                "id": insight.id,
                "message": insight.recommended_actions[0] if insight.recommended_actions else insight.message,
                "priority": insight.priority.value.title()
            }
            for insight in insights if insight.type.value == "optimization"
        ][:5]  # Top 5 optimization tips
    }
    
    # Update dashboard data with real insights
    dashboard_data["insights"] = formatted_insights
    
    return DashboardResponse(**dashboard_data)


@router.get("/threads/{thread_id}")
async def get_thread_analytics(
    thread_id: str,
    user_id: str = Query(..., description="User ID for authorization")
):
    """
    Get detailed analytics for a specific thread including:
    - Thread-level metrics
    - Individual tweet performance
    - Time-series data showing performance over time
    - Drop-off analysis
    """
    
    threads = await get_user_analytics_data(user_id)
    thread = next((t for t in threads if t.thread_id == thread_id), None)
    
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Get tweet metrics for this thread
    generator = MockAnalyticsGenerator()
    tweet_metrics = generator.generate_tweet_metrics(thread)
    
    # Generate time-series data
    time_series = generator.generate_time_series_data(thread, hours_to_track=72)
    
    return {
        "thread": {
            "thread_id": thread.thread_id,
            "title": thread.title,
            "created_at": thread.created_at,
            "posted_at": thread.posted_at,
            "thread_length": thread.thread_length,
            "content_source": thread.content_source,
            "impressions": thread.impressions,
            "reach": thread.reach,
            "likes": thread.likes,
            "retweets": thread.retweets,
            "replies": thread.replies,
            "bookmarks": thread.bookmarks,
            "engagement_rate": thread.engagement_rate,
            "completion_rate": thread.completion_rate,
            "click_through_rate": thread.click_through_rate,
            "profile_visits": thread.profile_visits,
            "follower_growth": thread.follower_growth,
            "hook_performance": thread.hook_performance,
            "drop_off_points": thread.drop_off_points,
            "best_performing_tweet": thread.best_performing_tweet
        },
        "tweets": [
            {
                "position": tweet.position,
                "content": tweet.content,
                "impressions": tweet.impressions,
                "likes": tweet.likes,
                "retweets": tweet.retweets,
                "replies": tweet.replies,
                "bookmarks": tweet.bookmarks,
                "engagement_rate": tweet.engagement_rate,
                "is_hook": tweet.is_hook,
                "is_cta": tweet.is_cta
            }
            for tweet in tweet_metrics
        ],
        "time_series": [
            {
                "timestamp": snapshot.timestamp,
                "hours_since_posted": snapshot.hours_since_posted,
                "metrics": snapshot.metrics
            }
            for snapshot in time_series
        ]
    }


@router.post("/compare/threads")
async def compare_threads(
    request: ThreadComparisonRequest,
    user_id: str = Query(..., description="User ID for authorization")
):
    """
    Compare two threads across all metrics and provide insights on:
    - Performance differences
    - What made one thread perform better
    - Actionable recommendations based on comparison
    """
    
    threads = await get_user_analytics_data(user_id)
    
    # Verify both threads exist and belong to user
    thread_1 = next((t for t in threads if t.thread_id == request.thread_id_1), None)
    thread_2 = next((t for t in threads if t.thread_id == request.thread_id_2), None)
    
    if not thread_1 or not thread_2:
        raise HTTPException(status_code=404, detail="One or both threads not found")
    
    # Perform comparison
    comparison_service = AnalyticsComparison(threads)
    comparison_result = comparison_service.compare_threads(
        request.thread_id_1, 
        request.thread_id_2
    )
    
    return {
        "comparison_type": comparison_result.comparison_type,
        "primary_thread": {
            "id": request.thread_id_1,
            "title": comparison_result.primary_subject
        },
        "comparison_thread": {
            "id": request.thread_id_2,
            "title": comparison_result.comparison_subject
        },
        "metrics": comparison_result.metrics,
        "insights": comparison_result.insights,
        "confidence_score": comparison_result.confidence_score,
        "created_at": comparison_result.created_at
    }


@router.get("/insights", response_model=InsightsResponse)
async def get_user_insights(
    user_id: str = Query(..., description="User ID to generate insights for"),
    period_days: int = Query(default=90, ge=7, le=365, description="Period to analyze in days")
):
    """
    Get AI-powered insights and recommendations including:
    - Performance pattern analysis
    - Content optimization suggestions
    - Timing recommendations
    - Audience behavior insights
    """
    
    threads = await get_user_analytics_data(user_id)
    tweets = await get_tweet_metrics_data(user_id)
    
    # Generate insights
    insights_engine = InsightsEngine(threads, tweets)
    insights = insights_engine.generate_user_insights(user_id, period_days)
    summary = insights_engine.get_insights_summary(insights)
    
    # Format response
    formatted_insights = [
        {
            "id": insight.id,
            "type": insight.type.value,
            "priority": insight.priority.value,
            "title": insight.title,
            "message": insight.message,
            "impact_description": insight.impact_description,
            "recommended_actions": insight.recommended_actions,
            "confidence_score": insight.confidence_score,
            "supporting_data": insight.supporting_data
        }
        for insight in insights
    ]
    
    return InsightsResponse(
        insights=formatted_insights,
        summary={
            "total_insights": summary.total_insights,
            "critical_count": summary.critical_count,
            "high_priority_count": summary.high_priority_count,
            "top_recommendation": summary.top_recommendation,
            "performance_score": summary.performance_score,
            "improvement_potential": summary.improvement_potential
        }
    )


@router.get("/benchmarks", response_model=BenchmarkResponse)
async def get_industry_benchmarks(
    user_id: str = Query(..., description="User ID to benchmark against industry")
):
    """
    Compare user's performance to industry benchmarks including:
    - Engagement rate percentiles
    - Completion rate comparisons
    - Click-through rate positioning
    - Overall performance scoring
    """
    
    threads = await get_user_analytics_data(user_id)
    
    comparison_service = AnalyticsComparison(threads)
    benchmarks = comparison_service.get_industry_benchmarks(user_id)
    
    if not benchmarks:
        raise HTTPException(status_code=404, detail="Insufficient data for benchmarking")
    
    # Calculate overall user score
    percentiles = [b.user_percentile for b in benchmarks]
    avg_percentile = sum(percentiles) / len(percentiles)
    
    # Determine position description
    if avg_percentile >= 90:
        position = "Top 10% - Exceptional Performance"
    elif avg_percentile >= 75:
        position = "Top 25% - Strong Performance"
    elif avg_percentile >= 50:
        position = "Above Average"
    elif avg_percentile >= 25:
        position = "Below Average"
    else:
        position = "Bottom 25% - Needs Improvement"
    
    formatted_benchmarks = [
        {
            "metric_name": b.metric_name,
            "industry_median": b.industry_median,
            "industry_top_10_percent": b.industry_top_10_percent,
            "industry_top_25_percent": b.industry_top_25_percent,
            "user_percentile": b.user_percentile,
            "sample_size": b.sample_size
        }
        for b in benchmarks
    ]
    
    return BenchmarkResponse(
        benchmarks=formatted_benchmarks,
        user_score=avg_percentile,
        industry_position=position
    )


@router.get("/timing/analysis")
async def get_timing_analysis(
    user_id: str = Query(..., description="User ID to analyze timing for")
):
    """
    Analyze optimal posting times based on historical performance:
    - Best days of the week
    - Optimal hours for posting
    - Peak engagement windows
    - Audience activity patterns
    """
    
    threads = await get_user_analytics_data(user_id)
    
    comparison_service = AnalyticsComparison(threads)
    timing_analysis = comparison_service.analyze_optimal_timing(user_id)
    
    if not timing_analysis:
        raise HTTPException(status_code=404, detail="Insufficient data for timing analysis")
    
    return {
        "optimal_posting_times": {
            "best_hour": timing_analysis.get("optimal_hour"),
            "best_day": timing_analysis.get("optimal_day"),
            "day_names": timing_analysis.get("day_names", [])
        },
        "hourly_performance": timing_analysis.get("hourly_performance", {}),
        "daily_performance": timing_analysis.get("daily_performance", {}),
        "recommendations": [
            f"Post around {timing_analysis.get('optimal_hour', 12):02d}:00 for best results",
            f"Focus on {timing_analysis.get('day_names', [''])[timing_analysis.get('optimal_day', 0)]} for important content",
            "Avoid posting during your lowest performing times",
            "Test posting 1-2 hours before and after your peak times"
        ]
    }


@router.get("/content/analysis")
async def get_content_analysis(
    user_id: str = Query(..., description="User ID to analyze content for")
):
    """
    Analyze content performance patterns:
    - Optimal thread lengths
    - Content type performance
    - Hook effectiveness
    - Engagement patterns by content characteristics
    """
    
    threads = await get_user_analytics_data(user_id)
    
    comparison_service = AnalyticsComparison(threads)
    content_analysis = comparison_service.analyze_content_type_performance(user_id)
    
    if not content_analysis:
        raise HTTPException(status_code=404, detail="Insufficient data for content analysis")
    
    # Analyze thread length performance
    length_performance = {}
    for thread in threads:
        if thread.posted_at:  # Only analyze posted threads
            length_bucket = _get_length_bucket(thread.thread_length)
            if length_bucket not in length_performance:
                length_performance[length_bucket] = {
                    "count": 0,
                    "total_engagement": 0,
                    "total_impressions": 0
                }
            
            length_performance[length_bucket]["count"] += 1
            length_performance[length_bucket]["total_engagement"] += thread.engagement_rate
            length_performance[length_bucket]["total_impressions"] += thread.impressions
    
    # Calculate averages
    for bucket, data in length_performance.items():
        if data["count"] > 0:
            data["avg_engagement_rate"] = data["total_engagement"] / data["count"]
            data["avg_impressions"] = data["total_impressions"] / data["count"]
    
    return {
        "content_type_performance": content_analysis,
        "thread_length_analysis": length_performance,
        "recommendations": [
            "Focus on your best-performing content types",
            "Experiment with different thread lengths to find your sweet spot",
            "Analyze your top-performing threads for common patterns",
            "Consider repurposing successful content formats"
        ]
    }


@router.get("/export")
async def export_analytics_data(
    user_id: str = Query(..., description="User ID to export data for"),
    period_days: int = Query(default=90, ge=1, le=365, description="Period to export"),
    format: str = Query(default="json", regex="^(json|csv)$", description="Export format")
):
    """
    Export analytics data for external analysis:
    - Thread-level metrics
    - Tweet-level performance data
    - Time-series snapshots
    - Available in JSON or CSV format
    """
    
    threads = await get_user_analytics_data(user_id)
    tweets = await get_tweet_metrics_data(user_id)
    
    # Filter to requested period
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=period_days)
    period_threads = [
        t for t in threads 
        if start_date <= t.created_at <= end_date
    ]
    
    if format == "json":
        return {
            "export_date": datetime.utcnow(),
            "period": f"{period_days} days",
            "threads": [
                {
                    "thread_id": t.thread_id,
                    "title": t.title,
                    "created_at": t.created_at,
                    "posted_at": t.posted_at,
                    "thread_length": t.thread_length,
                    "impressions": t.impressions,
                    "engagement_rate": t.engagement_rate,
                    "likes": t.likes,
                    "retweets": t.retweets,
                    "replies": t.replies,
                    "bookmarks": t.bookmarks,
                    "follower_growth": t.follower_growth
                }
                for t in period_threads
            ],
            "tweets": [
                {
                    "thread_id": t.thread_id,
                    "position": t.position,
                    "content": t.content,
                    "impressions": t.impressions,
                    "engagement_rate": t.engagement_rate,
                    "likes": t.likes,
                    "retweets": t.retweets,
                    "replies": t.replies
                }
                for t in tweets
                if any(thread.thread_id == t.thread_id for thread in period_threads)
            ]
        }
    
    # CSV format would be implemented here
    # For now, return JSON with CSV indication
    return {"message": "CSV export not yet implemented", "format": "json"}


# Health check endpoint
@router.get("/health")
async def analytics_health_check():
    """Health check for analytics service"""
    return {
        "status": "healthy",
        "service": "analytics",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }


# Helper functions

def _get_length_bucket(length: int) -> str:
    """Categorize thread length into buckets"""
    if length <= 3:
        return "Short (1-3 tweets)"
    elif length <= 7:
        return "Medium (4-7 tweets)"
    elif length <= 12:
        return "Long (8-12 tweets)"
    else:
        return "Very Long (13+ tweets)"