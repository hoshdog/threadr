"""
API routes for analytics endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Callable, Any
from datetime import datetime

try:
    from ..models.auth import User
    from ..models.analytics import (
        ThreadAnalytics, DashboardSummary, MetricPeriod, ContentType,
        ThreadComparison, InsightRecommendation, BenchmarkData, AnalyticsExport
    )
    from ..services.analytics.analytics_service import AnalyticsService
    from ..core.redis_manager import get_redis_manager
except ImportError:
    from models.auth import User
    from models.analytics import (
        ThreadAnalytics, DashboardSummary, MetricPeriod, ContentType,
        ThreadComparison, InsightRecommendation, BenchmarkData, AnalyticsExport
    )
    from services.analytics.analytics_service import AnalyticsService
    from core.redis_manager import get_redis_manager


def create_analytics_router(get_current_user_func: Callable, require_premium_func: Callable) -> APIRouter:
    """Create analytics router with auth dependencies"""
    router = APIRouter(prefix="/api/analytics", tags=["analytics"])

    def get_analytics_service():
        """Get analytics service instance"""
        redis_manager = get_redis_manager()
        # Get the underlying Redis client if available
        redis = redis_manager.client if redis_manager and redis_manager.is_available else None
        return AnalyticsService(redis)

    @router.post("/thread/{thread_id}")
    async def save_thread_analytics(
        thread_id: str,
        analytics: ThreadAnalytics,
        current_user: User = Depends(get_current_user_func),
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
        current_user: User = Depends(require_premium_func),
        service: AnalyticsService = Depends(get_analytics_service)
    ):
        """Get detailed analytics for a specific thread"""
        analytics = await service.get_thread_analytics(thread_id, current_user.user_id)
        if not analytics:
            raise HTTPException(status_code=404, detail="Thread analytics not found")
        return analytics

    @router.get("/dashboard", response_model=DashboardSummary)
    async def get_dashboard(
        period: MetricPeriod = Query(MetricPeriod.MONTH, description="Time period for metrics"),
        current_user: User = Depends(require_premium_func),
        service: AnalyticsService = Depends(get_analytics_service)
    ):
        """Get dashboard summary with key metrics"""
        dashboard = await service.get_dashboard_summary(current_user.user_id, period)
        return dashboard

    @router.get("/threads", response_model=List[ThreadAnalytics])
    async def get_user_threads(
        limit: int = Query(50, ge=1, le=100, description="Number of threads to return"),
        offset: int = Query(0, ge=0, description="Number of threads to skip"),
        period: Optional[MetricPeriod] = Query(None, description="Filter by time period"),
        content_type: Optional[ContentType] = Query(None, description="Filter by content type"),
        current_user: User = Depends(require_premium_func),
        service: AnalyticsService = Depends(get_analytics_service)
    ):
        """Get user's thread analytics with filtering"""
        threads = await service.get_user_threads(
            current_user.user_id, 
            limit=limit, 
            offset=offset,
            period=period,
            content_type=content_type
        )
        return threads

    @router.get("/compare/{thread_id_1}/{thread_id_2}", response_model=ThreadComparison)
    async def compare_threads(
        thread_id_1: str,
        thread_id_2: str,
        current_user: User = Depends(require_premium_func),
        service: AnalyticsService = Depends(get_analytics_service)
    ):
        """Compare performance between two threads"""
        comparison = await service.compare_threads(thread_id_1, thread_id_2, current_user.user_id)
        if not comparison:
            raise HTTPException(status_code=404, detail="One or more threads not found")
        return comparison

    @router.get("/insights", response_model=List[InsightRecommendation])
    async def get_insights(
        current_user: User = Depends(require_premium_func),
        service: AnalyticsService = Depends(get_analytics_service)
    ):
        """Get personalized insights and recommendations"""
        insights = await service.generate_insights(current_user.user_id)
        return insights

    @router.get("/benchmarks", response_model=BenchmarkData)
    async def get_benchmarks(
        content_type: ContentType = Query(ContentType.BLOG_POST, description="Content type for benchmarks"),
        current_user: User = Depends(require_premium_func),
        service: AnalyticsService = Depends(get_analytics_service)
    ):
        """Get industry benchmarks for comparison"""
        benchmarks = await service.get_benchmarks(content_type)
        return benchmarks

    @router.post("/export", response_model=AnalyticsExport)
    async def export_analytics(
        period: MetricPeriod = Query(MetricPeriod.MONTH, description="Time period to export"),
        format: str = Query("csv", description="Export format (csv, json)"),
        current_user: User = Depends(require_premium_func),
        service: AnalyticsService = Depends(get_analytics_service)
    ):
        """Export analytics data"""
        if format not in ["csv", "json"]:
            raise HTTPException(status_code=400, detail="Invalid export format")
        
        export_data = await service.export_analytics(current_user.user_id, period, format)
        return export_data

    return router


# Default router for backwards compatibility (will be None if not properly configured)
router = None