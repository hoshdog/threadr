"""
API routes for analytics endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from .auth_middleware import get_current_user, require_premium_user
from .auth_models import User
from .analytics_models import (
    ThreadAnalytics, DashboardSummary, MetricPeriod, ContentType,
    ThreadComparison, InsightRecommendation, BenchmarkData, AnalyticsExport
)
from .analytics_service import AnalyticsService
from .redis_manager import get_redis_client

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def get_analytics_service():
    """Get analytics service instance"""
    redis = get_redis_client()
    return AnalyticsService(redis)


@router.post("/thread/{thread_id}")
async def save_thread_analytics(
    thread_id: str,
    analytics: ThreadAnalytics,
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Save analytics for a thread (internal use)"""
    # Ensure user owns the thread
    if analytics.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    success = await service.save_thread_analytics(analytics)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save analytics")
    
    return {"message": "Analytics saved successfully"}


@router.get("/thread/{thread_id}", response_model=ThreadAnalytics)
async def get_thread_analytics(
    thread_id: str,
    current_user: User = Depends(require_premium_user),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get analytics for a specific thread"""
    analytics = await service.get_thread_analytics(current_user.user_id, thread_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics not found")
    
    return analytics


@router.get("/threads", response_model=List[ThreadAnalytics])
async def get_user_threads_analytics(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_premium_user),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get analytics for user's threads"""
    analytics = await service.get_user_threads_analytics(
        current_user.user_id, 
        limit=limit, 
        offset=offset
    )
    return analytics


@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard_summary(
    period: MetricPeriod = Query(MetricPeriod.WEEK),
    current_user: User = Depends(require_premium_user),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get dashboard summary with key metrics"""
    summary = await service.get_dashboard_summary(current_user.user_id, period)
    if not summary:
        # Return empty summary for new users
        summary = DashboardSummary(
            user_id=current_user.user_id,
            period=period,
            generated_at=datetime.utcnow(),
            total_threads=0,
            threads_this_period=0,
            total_impressions={
                "current_value": 0,
                "previous_value": 0,
                "change_percent": 0,
                "trend": "stable",
                "period": period
            },
            engagement_rate={
                "current_value": 0,
                "previous_value": 0,
                "change_percent": 0,
                "trend": "stable",
                "period": period
            },
            follower_growth={
                "current_value": 0,
                "previous_value": 0,
                "change_percent": 0,
                "trend": "stable",
                "period": period
            },
            avg_thread_performance={
                "current_value": 0,
                "previous_value": 0,
                "change_percent": 0,
                "trend": "stable",
                "period": period
            },
            content_type_breakdown={},
            optimal_posting_times=[]
        )
    
    return summary


@router.get("/compare", response_model=ThreadComparison)
async def compare_threads(
    thread_a: str = Query(..., description="First thread ID"),
    thread_b: str = Query(..., description="Second thread ID"),
    current_user: User = Depends(require_premium_user),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Compare two threads"""
    comparison = await service.compare_threads(
        current_user.user_id, 
        thread_a, 
        thread_b
    )
    if not comparison:
        raise HTTPException(status_code=404, detail="One or both threads not found")
    
    return comparison


@router.get("/insights", response_model=List[InsightRecommendation])
async def get_insights(
    current_user: User = Depends(require_premium_user),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get AI-generated insights and recommendations"""
    insights = await service.get_insights(current_user.user_id)
    return insights


@router.get("/benchmarks", response_model=BenchmarkData)
async def get_benchmarks(
    content_type: ContentType = Query(ContentType.OTHER),
    period: MetricPeriod = Query(MetricPeriod.MONTH),
    current_user: User = Depends(require_premium_user),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Get industry benchmarks and user's position"""
    benchmarks = await service.get_benchmarks(
        current_user.user_id,
        content_type,
        period
    )
    if not benchmarks:
        raise HTTPException(status_code=404, detail="Benchmark data not available")
    
    return benchmarks


@router.get("/export", response_model=AnalyticsExport)
async def export_analytics(
    period: MetricPeriod = Query(MetricPeriod.ALL_TIME),
    current_user: User = Depends(require_premium_user),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Export analytics data"""
    # Get dashboard summary
    summary = await service.get_dashboard_summary(current_user.user_id, period)
    
    # Get all threads
    threads = await service.get_user_threads_analytics(
        current_user.user_id, 
        limit=1000
    )
    
    # Get insights
    insights = await service.get_insights(current_user.user_id)
    
    # Get benchmarks
    benchmarks = await service.get_benchmarks(
        current_user.user_id,
        ContentType.OTHER,
        period
    )
    
    export_data = AnalyticsExport(
        user_id=current_user.user_id,
        export_date=datetime.utcnow(),
        period=period,
        summary=summary or DashboardSummary(
            user_id=current_user.user_id,
            period=period,
            generated_at=datetime.utcnow(),
            total_threads=0,
            threads_this_period=0,
            total_impressions={
                "current_value": 0,
                "previous_value": 0,
                "change_percent": 0,
                "trend": "stable",
                "period": period
            },
            engagement_rate={
                "current_value": 0,
                "previous_value": 0,
                "change_percent": 0,
                "trend": "stable",
                "period": period
            },
            follower_growth={
                "current_value": 0,
                "previous_value": 0,
                "change_percent": 0,
                "trend": "stable",
                "period": period
            },
            avg_thread_performance={
                "current_value": 0,
                "previous_value": 0,
                "change_percent": 0,
                "trend": "stable",
                "period": period
            },
            content_type_breakdown={},
            optimal_posting_times=[]
        ),
        threads=threads,
        insights=insights,
        benchmarks=benchmarks
    )
    
    return export_data


# Mock data endpoint for development/testing
@router.post("/mock/{thread_id}")
async def create_mock_analytics(
    thread_id: str,
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Create mock analytics data for testing (development only)"""
    import random
    from datetime import timedelta
    
    # Create mock analytics
    mock_analytics = ThreadAnalytics(
        thread_id=thread_id,
        user_id=current_user.user_id,
        created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72)),
        title=f"Mock Thread {thread_id}",
        source_url="https://example.com/article",
        content_type=random.choice(list(ContentType)),
        tweet_count=random.randint(5, 15),
        total_character_count=random.randint(1000, 3000),
        total_impressions=random.randint(1000, 50000),
        total_engagements=random.randint(50, 5000),
        engagement_rate=random.uniform(1.0, 10.0),
        total_likes=random.randint(20, 2000),
        total_retweets=random.randint(10, 1000),
        total_replies=random.randint(5, 500),
        total_bookmarks=random.randint(2, 200),
        total_quotes=random.randint(1, 100),
        profile_visits=random.randint(10, 1000),
        link_clicks=random.randint(5, 500),
        new_followers=random.randint(0, 100),
        thread_completion_rate=random.uniform(20.0, 80.0),
        avg_time_on_thread=random.uniform(30.0, 300.0),
        virality_score=random.uniform(0.0, 100.0),
        posted_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72)),
        peak_engagement_hour=random.randint(9, 22),
        peak_engagement_day=random.choice(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]),
        tweet_metrics=[]
    )
    
    # Add mock tweet metrics
    for i in range(mock_analytics.tweet_count):
        tweet_metric = {
            "tweet_id": f"{thread_id}_tweet_{i+1}",
            "position": i + 1,
            "content": f"This is tweet {i+1} of the thread",
            "character_count": random.randint(50, 280),
            "impressions": random.randint(100, 10000),
            "likes": random.randint(5, 500),
            "retweets": random.randint(2, 200),
            "replies": random.randint(1, 100),
            "bookmarks": random.randint(0, 50),
            "quotes": random.randint(0, 20),
            "engagement_rate": random.uniform(1.0, 15.0),
            "drop_off_rate": random.uniform(5.0, 30.0) if i < mock_analytics.tweet_count - 1 else None,
            "posted_at": mock_analytics.posted_at + timedelta(minutes=i),
            "peak_hour": random.randint(9, 22)
        }
        mock_analytics.tweet_metrics.append(tweet_metric)
    
    # Save mock analytics
    success = await service.save_thread_analytics(mock_analytics)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save mock analytics")
    
    return {"message": "Mock analytics created successfully", "thread_id": thread_id}