"""
Analytics service for managing thread performance data
"""
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from redis import Redis
import statistics

try:
    from ...models.analytics import (
        ThreadAnalytics, TweetMetrics, DashboardSummary, MetricPeriod,
        TimeSeriesDataPoint, MetricSummary, ContentType, InsightRecommendation,
        BenchmarkData, ThreadComparison, EngagementType
    )
except ImportError:
    from models.analytics import (
        ThreadAnalytics, TweetMetrics, DashboardSummary, MetricPeriod,
        TimeSeriesDataPoint, MetricSummary, ContentType, InsightRecommendation,
        BenchmarkData, ThreadComparison, EngagementType
    )


class AnalyticsService:
    """Service for managing thread analytics data"""
    
    def __init__(self, redis_client: Optional[Redis] = None):
        self.redis = redis_client
        self.analytics_ttl = 90 * 24 * 60 * 60  # 90 days in seconds
        
    def _get_analytics_key(self, user_id: str, thread_id: str) -> str:
        """Generate Redis key for thread analytics"""
        return f"analytics:{user_id}:thread:{thread_id}"
    
    def _get_user_analytics_key(self, user_id: str) -> str:
        """Generate Redis key for user's analytics list"""
        return f"analytics:{user_id}:threads"
    
    def _get_timeseries_key(self, user_id: str, metric: str, period: MetricPeriod) -> str:
        """Generate Redis key for time series data"""
        return f"analytics:{user_id}:timeseries:{metric}:{period}"
    
    async def save_thread_analytics(self, analytics: ThreadAnalytics) -> bool:
        """Save thread analytics data"""
        if not self.redis:
            return False
            
        try:
            # Save analytics data
            key = self._get_analytics_key(analytics.user_id, analytics.thread_id)
            self.redis.setex(
                key,
                self.analytics_ttl,
                analytics.json()
            )
            
            # Add to user's analytics list
            list_key = self._get_user_analytics_key(analytics.user_id)
            self.redis.zadd(
                list_key,
                {analytics.thread_id: analytics.created_at.timestamp()}
            )
            
            # Update time series data
            await self._update_timeseries_data(analytics)
            
            return True
        except Exception as e:
            print(f"Error saving analytics: {e}")
            return False
    
    async def get_thread_analytics(self, user_id: str, thread_id: str) -> Optional[ThreadAnalytics]:
        """Get analytics for a specific thread"""
        if not self.redis:
            return None
            
        try:
            key = self._get_analytics_key(user_id, thread_id)
            data = self.redis.get(key)
            if data:
                return ThreadAnalytics.parse_raw(data)
            return None
        except Exception as e:
            print(f"Error retrieving analytics: {e}")
            return None
    
    async def get_user_threads_analytics(
        self, 
        user_id: str, 
        limit: int = 50,
        offset: int = 0
    ) -> List[ThreadAnalytics]:
        """Get analytics for user's threads"""
        if not self.redis:
            return []
            
        try:
            # Get thread IDs sorted by creation date
            list_key = self._get_user_analytics_key(user_id)
            thread_ids = self.redis.zrevrange(
                list_key, 
                offset, 
                offset + limit - 1
            )
            
            # Retrieve analytics for each thread
            analytics_list = []
            for thread_id in thread_ids:
                analytics = await self.get_thread_analytics(user_id, thread_id.decode())
                if analytics:
                    analytics_list.append(analytics)
                    
            return analytics_list
        except Exception as e:
            print(f"Error retrieving user analytics: {e}")
            return []
    
    async def get_dashboard_summary(
        self, 
        user_id: str, 
        period: MetricPeriod = MetricPeriod.WEEK
    ) -> Optional[DashboardSummary]:
        """Generate dashboard summary for user"""
        if not self.redis:
            return None
            
        try:
            # Get all user's threads
            all_threads = await self.get_user_threads_analytics(user_id, limit=1000)
            if not all_threads:
                return None
            
            # Filter threads by period
            now = datetime.utcnow()
            period_start = self._get_period_start(now, period)
            period_threads = [t for t in all_threads if t.created_at >= period_start]
            
            # Calculate previous period for comparison
            prev_period_start = self._get_period_start(period_start - timedelta(seconds=1), period)
            prev_period_threads = [
                t for t in all_threads 
                if prev_period_start <= t.created_at < period_start
            ]
            
            # Calculate metrics
            summary = DashboardSummary(
                user_id=user_id,
                period=period,
                generated_at=now,
                total_threads=len(all_threads),
                threads_this_period=len(period_threads),
                total_impressions=self._calculate_metric_summary(
                    period_threads, prev_period_threads, "total_impressions"
                ),
                engagement_rate=self._calculate_metric_summary(
                    period_threads, prev_period_threads, "engagement_rate"
                ),
                follower_growth=self._calculate_follower_growth(
                    period_threads, prev_period_threads
                ),
                avg_thread_performance=self._calculate_avg_performance(
                    period_threads, prev_period_threads
                ),
                content_type_breakdown=self._calculate_content_breakdown(period_threads),
                optimal_posting_times=self._calculate_optimal_times(all_threads),
                impressions_over_time=await self._get_timeseries_data(
                    user_id, "impressions", period
                ),
                engagement_rate_over_time=await self._get_timeseries_data(
                    user_id, "engagement_rate", period
                )
            )
            
            # Find best and worst performing threads
            if period_threads:
                sorted_threads = sorted(
                    period_threads, 
                    key=lambda t: t.virality_score, 
                    reverse=True
                )
                summary.best_performing_thread = {
                    "thread_id": sorted_threads[0].thread_id,
                    "title": sorted_threads[0].title,
                    "virality_score": sorted_threads[0].virality_score,
                    "impressions": sorted_threads[0].total_impressions
                }
                summary.worst_performing_thread = {
                    "thread_id": sorted_threads[-1].thread_id,
                    "title": sorted_threads[-1].title,
                    "virality_score": sorted_threads[-1].virality_score,
                    "impressions": sorted_threads[-1].total_impressions
                }
            
            return summary
            
        except Exception as e:
            print(f"Error generating dashboard summary: {e}")
            return None
    
    async def compare_threads(
        self, 
        user_id: str, 
        thread_a_id: str, 
        thread_b_id: str
    ) -> Optional[ThreadComparison]:
        """Compare two threads"""
        thread_a = await self.get_thread_analytics(user_id, thread_a_id)
        thread_b = await self.get_thread_analytics(user_id, thread_b_id)
        
        if not thread_a or not thread_b:
            return None
        
        comparison = ThreadComparison(
            thread_a=thread_a,
            thread_b=thread_b,
            impressions_diff=thread_a.total_impressions - thread_b.total_impressions,
            engagement_rate_diff=thread_a.engagement_rate - thread_b.engagement_rate,
            completion_rate_diff=thread_a.thread_completion_rate - thread_b.thread_completion_rate,
            virality_score_diff=thread_a.virality_score - thread_b.virality_score,
            better_performer=thread_a_id if thread_a.virality_score > thread_b.virality_score else thread_b_id,
            key_differences=self._analyze_thread_differences(thread_a, thread_b)
        )
        
        return comparison
    
    async def get_insights(self, user_id: str) -> List[InsightRecommendation]:
        """Generate AI-powered insights for user"""
        threads = await self.get_user_threads_analytics(user_id, limit=100)
        if len(threads) < 5:  # Need minimum data for insights
            return []
        
        insights = []
        
        # Timing insights
        timing_insight = self._generate_timing_insight(threads)
        if timing_insight:
            insights.append(timing_insight)
        
        # Content length insights
        length_insight = self._generate_length_insight(threads)
        if length_insight:
            insights.append(length_insight)
        
        # Engagement pattern insights
        engagement_insight = self._generate_engagement_insight(threads)
        if engagement_insight:
            insights.append(engagement_insight)
        
        # Content type insights
        content_insight = self._generate_content_type_insight(threads)
        if content_insight:
            insights.append(content_insight)
        
        return insights
    
    async def get_benchmarks(
        self, 
        user_id: str, 
        content_type: ContentType,
        period: MetricPeriod = MetricPeriod.MONTH
    ) -> Optional[BenchmarkData]:
        """Get industry benchmarks and user's position"""
        # In production, this would query aggregated industry data
        # For now, return mock benchmark data
        benchmarks = BenchmarkData(
            category=content_type,
            period=period,
            avg_impressions_p50=5000,
            avg_impressions_p75=15000,
            avg_impressions_p90=50000,
            avg_engagement_rate_p50=3.5,
            avg_engagement_rate_p75=5.2,
            avg_engagement_rate_p90=8.1,
            avg_thread_length=7,
            avg_completion_rate=45.0
        )
        
        # Calculate user's position
        user_threads = await self.get_user_threads_analytics(user_id, limit=50)
        if user_threads:
            user_avg_impressions = statistics.mean([t.total_impressions for t in user_threads])
            user_avg_engagement = statistics.mean([t.engagement_rate for t in user_threads])
            
            # Simple percentile calculation
            if user_avg_impressions < benchmarks.avg_impressions_p50:
                benchmarks.user_percentile_impressions = 25
            elif user_avg_impressions < benchmarks.avg_impressions_p75:
                benchmarks.user_percentile_impressions = 50
            elif user_avg_impressions < benchmarks.avg_impressions_p90:
                benchmarks.user_percentile_impressions = 75
            else:
                benchmarks.user_percentile_impressions = 90
                
            if user_avg_engagement < benchmarks.avg_engagement_rate_p50:
                benchmarks.user_percentile_engagement = 25
            elif user_avg_engagement < benchmarks.avg_engagement_rate_p75:
                benchmarks.user_percentile_engagement = 50
            elif user_avg_engagement < benchmarks.avg_engagement_rate_p90:
                benchmarks.user_percentile_engagement = 75
            else:
                benchmarks.user_percentile_engagement = 90
        
        return benchmarks
    
    # Helper methods
    
    def _get_period_start(self, date: datetime, period: MetricPeriod) -> datetime:
        """Get start date for a period"""
        if period == MetricPeriod.HOUR:
            return date - timedelta(hours=1)
        elif period == MetricPeriod.DAY:
            return date - timedelta(days=1)
        elif period == MetricPeriod.WEEK:
            return date - timedelta(weeks=1)
        elif period == MetricPeriod.MONTH:
            return date - timedelta(days=30)
        else:  # ALL_TIME
            return datetime.min
    
    def _calculate_metric_summary(
        self, 
        current_threads: List[ThreadAnalytics],
        previous_threads: List[ThreadAnalytics],
        metric_name: str
    ) -> MetricSummary:
        """Calculate metric summary with comparison"""
        current_values = [getattr(t, metric_name) for t in current_threads]
        previous_values = [getattr(t, metric_name) for t in previous_threads]
        
        current_value = sum(current_values) if current_values else 0
        previous_value = sum(previous_values) if previous_values else 0
        
        if metric_name == "engagement_rate" and current_values:
            current_value = statistics.mean(current_values)
        if metric_name == "engagement_rate" and previous_values:
            previous_value = statistics.mean(previous_values)
        
        change_percent = 0
        if previous_value > 0:
            change_percent = ((current_value - previous_value) / previous_value) * 100
        
        trend = "stable"
        if change_percent > 5:
            trend = "up"
        elif change_percent < -5:
            trend = "down"
        
        return MetricSummary(
            current_value=current_value,
            previous_value=previous_value,
            change_percent=change_percent,
            trend=trend,
            period=MetricPeriod.WEEK
        )
    
    def _calculate_follower_growth(
        self,
        current_threads: List[ThreadAnalytics],
        previous_threads: List[ThreadAnalytics]
    ) -> MetricSummary:
        """Calculate follower growth metric"""
        current_followers = sum([t.new_followers for t in current_threads])
        previous_followers = sum([t.new_followers for t in previous_threads])
        
        change_percent = 0
        if previous_followers > 0:
            change_percent = ((current_followers - previous_followers) / previous_followers) * 100
        
        trend = "stable"
        if change_percent > 5:
            trend = "up"
        elif change_percent < -5:
            trend = "down"
        
        return MetricSummary(
            current_value=current_followers,
            previous_value=previous_followers,
            change_percent=change_percent,
            trend=trend,
            period=MetricPeriod.WEEK
        )
    
    def _calculate_avg_performance(
        self,
        current_threads: List[ThreadAnalytics],
        previous_threads: List[ThreadAnalytics]
    ) -> MetricSummary:
        """Calculate average thread performance"""
        current_scores = [t.virality_score for t in current_threads]
        previous_scores = [t.virality_score for t in previous_threads]
        
        current_avg = statistics.mean(current_scores) if current_scores else 0
        previous_avg = statistics.mean(previous_scores) if previous_scores else 0
        
        change_percent = 0
        if previous_avg > 0:
            change_percent = ((current_avg - previous_avg) / previous_avg) * 100
        
        trend = "stable"
        if change_percent > 5:
            trend = "up"
        elif change_percent < -5:
            trend = "down"
        
        return MetricSummary(
            current_value=current_avg,
            previous_value=previous_avg,
            change_percent=change_percent,
            trend=trend,
            period=MetricPeriod.WEEK
        )
    
    def _calculate_content_breakdown(self, threads: List[ThreadAnalytics]) -> Dict[str, float]:
        """Calculate content type breakdown"""
        if not threads:
            return {}
        
        content_counts = {}
        for thread in threads:
            content_type = thread.content_type.value
            content_counts[content_type] = content_counts.get(content_type, 0) + 1
        
        total = len(threads)
        return {k: (v / total) * 100 for k, v in content_counts.items()}
    
    def _calculate_optimal_times(self, threads: List[ThreadAnalytics]) -> List[Dict[str, Any]]:
        """Calculate optimal posting times"""
        if not threads:
            return []
        
        # Group by day and hour
        time_performance = {}
        for thread in threads:
            day = thread.posted_at.strftime("%A")
            hour = thread.posted_at.hour
            key = f"{day}_{hour}"
            
            if key not in time_performance:
                time_performance[key] = []
            time_performance[key].append(thread.engagement_rate)
        
        # Calculate averages and sort
        time_stats = []
        for key, rates in time_performance.items():
            day, hour = key.split("_")
            avg_rate = statistics.mean(rates)
            time_stats.append({
                "day": day,
                "hour": int(hour),
                "avg_engagement_rate": avg_rate,
                "sample_size": len(rates)
            })
        
        # Sort by engagement rate and return top 5
        time_stats.sort(key=lambda x: x["avg_engagement_rate"], reverse=True)
        return time_stats[:5]
    
    async def _update_timeseries_data(self, analytics: ThreadAnalytics):
        """Update time series data for metrics"""
        if not self.redis:
            return
        
        # Update impressions time series
        impressions_key = self._get_timeseries_key(
            analytics.user_id, "impressions", MetricPeriod.DAY
        )
        datapoint = TimeSeriesDataPoint(
            timestamp=analytics.created_at,
            value=analytics.total_impressions,
            period=MetricPeriod.DAY
        )
        self.redis.zadd(
            impressions_key,
            {datapoint.json(): analytics.created_at.timestamp()}
        )
        
        # Update engagement rate time series
        engagement_key = self._get_timeseries_key(
            analytics.user_id, "engagement_rate", MetricPeriod.DAY
        )
        datapoint = TimeSeriesDataPoint(
            timestamp=analytics.created_at,
            value=analytics.engagement_rate,
            period=MetricPeriod.DAY
        )
        self.redis.zadd(
            engagement_key,
            {datapoint.json(): analytics.created_at.timestamp()}
        )
    
    async def _get_timeseries_data(
        self, 
        user_id: str, 
        metric: str, 
        period: MetricPeriod
    ) -> List[TimeSeriesDataPoint]:
        """Get time series data for a metric"""
        if not self.redis:
            return []
        
        key = self._get_timeseries_key(user_id, metric, period)
        # Get data for the period
        now = datetime.utcnow()
        start = self._get_period_start(now, period)
        
        data = self.redis.zrangebyscore(
            key,
            start.timestamp(),
            now.timestamp()
        )
        
        datapoints = []
        for item in data:
            try:
                datapoints.append(TimeSeriesDataPoint.parse_raw(item))
            except:
                pass
        
        return datapoints
    
    def _analyze_thread_differences(
        self, 
        thread_a: ThreadAnalytics, 
        thread_b: ThreadAnalytics
    ) -> List[str]:
        """Analyze key differences between threads"""
        differences = []
        
        # Length difference
        if abs(thread_a.tweet_count - thread_b.tweet_count) >= 3:
            if thread_a.tweet_count > thread_b.tweet_count:
                differences.append(f"Thread A is {thread_a.tweet_count - thread_b.tweet_count} tweets longer")
            else:
                differences.append(f"Thread B is {thread_b.tweet_count - thread_a.tweet_count} tweets longer")
        
        # Timing difference
        if thread_a.posted_at.hour != thread_b.posted_at.hour:
            differences.append(
                f"Posted at different times: {thread_a.posted_at.hour}:00 vs {thread_b.posted_at.hour}:00"
            )
        
        # Content type difference
        if thread_a.content_type != thread_b.content_type:
            differences.append(
                f"Different content types: {thread_a.content_type.value} vs {thread_b.content_type.value}"
            )
        
        # Performance differences
        if thread_a.thread_completion_rate > thread_b.thread_completion_rate + 10:
            differences.append(
                f"Thread A has {thread_a.thread_completion_rate - thread_b.thread_completion_rate:.1f}% higher completion rate"
            )
        
        return differences
    
    def _generate_timing_insight(self, threads: List[ThreadAnalytics]) -> Optional[InsightRecommendation]:
        """Generate timing-based insights"""
        if len(threads) < 10:
            return None
        
        # Group by hour and calculate average engagement
        hour_performance = {}
        for thread in threads:
            hour = thread.posted_at.hour
            if hour not in hour_performance:
                hour_performance[hour] = []
            hour_performance[hour].append(thread.engagement_rate)
        
        # Find best and worst hours
        hour_stats = {
            hour: statistics.mean(rates) 
            for hour, rates in hour_performance.items() 
            if len(rates) >= 2
        }
        
        if len(hour_stats) < 3:
            return None
        
        best_hour = max(hour_stats.items(), key=lambda x: x[1])
        worst_hour = min(hour_stats.items(), key=lambda x: x[1])
        
        if best_hour[1] > worst_hour[1] * 1.5:  # Significant difference
            return InsightRecommendation(
                insight_id=f"timing_{datetime.utcnow().timestamp()}",
                category="timing",
                priority="high",
                title="Optimal Posting Time Identified",
                description=f"Your threads perform {((best_hour[1] / worst_hour[1]) - 1) * 100:.0f}% better when posted at {best_hour[0]}:00 compared to {worst_hour[0]}:00",
                action_items=[
                    f"Schedule your next thread for {best_hour[0]}:00",
                    f"Avoid posting at {worst_hour[0]}:00",
                    "Test posting at adjacent hours to refine timing"
                ],
                confidence_score=0.85,
                based_on_threads=[t.thread_id for t in threads[-20:]],
                potential_impact=f"+{((best_hour[1] / worst_hour[1]) - 1) * 100:.0f}% engagement",
                generated_at=datetime.utcnow()
            )
        
        return None
    
    def _generate_length_insight(self, threads: List[ThreadAnalytics]) -> Optional[InsightRecommendation]:
        """Generate thread length insights"""
        if len(threads) < 10:
            return None
        
        # Group by length and calculate performance
        length_groups = {
            "short": [],  # 1-5 tweets
            "medium": [],  # 6-10 tweets
            "long": []  # 11+ tweets
        }
        
        for thread in threads:
            if thread.tweet_count <= 5:
                length_groups["short"].append(thread.engagement_rate)
            elif thread.tweet_count <= 10:
                length_groups["medium"].append(thread.engagement_rate)
            else:
                length_groups["long"].append(thread.engagement_rate)
        
        # Calculate averages
        length_stats = {}
        for group, rates in length_groups.items():
            if len(rates) >= 3:
                length_stats[group] = statistics.mean(rates)
        
        if len(length_stats) < 2:
            return None
        
        best_length = max(length_stats.items(), key=lambda x: x[1])
        
        return InsightRecommendation(
            insight_id=f"length_{datetime.utcnow().timestamp()}",
            category="content",
            priority="medium",
            title=f"{best_length[0].capitalize()}-form threads perform best",
            description=f"Your {best_length[0]} threads ({"1-5" if best_length[0] == "short" else "6-10" if best_length[0] == "medium" else "11+"} tweets) achieve {best_length[1]:.1f}% average engagement rate",
            action_items=[
                f"Focus on creating {best_length[0]}-form threads",
                "Test varying lengths within the optimal range",
                "Consider thread purpose when choosing length"
            ],
            confidence_score=0.75,
            based_on_threads=[t.thread_id for t in threads[-30:]],
            potential_impact=f"Consistent {best_length[1]:.1f}% engagement",
            generated_at=datetime.utcnow()
        )
    
    def _generate_engagement_insight(self, threads: List[ThreadAnalytics]) -> Optional[InsightRecommendation]:
        """Generate engagement pattern insights"""
        recent_threads = threads[-20:]
        if len(recent_threads) < 5:
            return None
        
        # Find threads with high first-tweet engagement
        high_hook_threads = [
            t for t in recent_threads 
            if t.tweet_metrics and t.tweet_metrics[0].engagement_rate > t.engagement_rate * 1.5
        ]
        
        if len(high_hook_threads) >= 3:
            hook_examples = []
            for thread in high_hook_threads[:3]:
                if thread.tweet_metrics:
                    hook = thread.tweet_metrics[0].content[:50] + "..."
                    hook_examples.append(hook)
            
            return InsightRecommendation(
                insight_id=f"engagement_{datetime.utcnow().timestamp()}",
                category="engagement",
                priority="high",
                title="Strong Opening Hooks Drive Engagement",
                description="Your best-performing threads have opening tweets with 50% higher engagement than the thread average",
                action_items=[
                    "Craft compelling opening hooks",
                    "Lead with the most interesting insight",
                    "Use these high-performing hooks as templates: " + ", ".join(hook_examples[:2])
                ],
                confidence_score=0.9,
                based_on_threads=[t.thread_id for t in high_hook_threads],
                potential_impact="+50% thread engagement",
                generated_at=datetime.utcnow()
            )
        
        return None
    
    def _generate_content_type_insight(self, threads: List[ThreadAnalytics]) -> Optional[InsightRecommendation]:
        """Generate content type insights"""
        # Group by content type
        content_performance = {}
        for thread in threads:
            content_type = thread.content_type.value
            if content_type not in content_performance:
                content_performance[content_type] = []
            content_performance[content_type].append(thread.engagement_rate)
        
        # Calculate averages
        content_stats = {}
        for content_type, rates in content_performance.items():
            if len(rates) >= 5:
                content_stats[content_type] = statistics.mean(rates)
        
        if len(content_stats) < 2:
            return None
        
        best_type = max(content_stats.items(), key=lambda x: x[1])
        worst_type = min(content_stats.items(), key=lambda x: x[1])
        
        if best_type[1] > worst_type[1] * 1.3:  # 30% difference
            return InsightRecommendation(
                insight_id=f"content_type_{datetime.utcnow().timestamp()}",
                category="content",
                priority="medium",
                title=f"{best_type[0].capitalize()} content resonates most",
                description=f"Your {best_type[0]} content achieves {best_type[1]:.1f}% engagement rate, {((best_type[1] / worst_type[1]) - 1) * 100:.0f}% higher than {worst_type[0]} content",
                action_items=[
                    f"Create more {best_type[0]} content",
                    f"Analyze what makes your {best_type[0]} threads successful",
                    f"Consider pivoting {worst_type[0]} content to {best_type[0]} style"
                ],
                confidence_score=0.8,
                based_on_threads=[t.thread_id for t in threads[-50:]],
                potential_impact=f"+{((best_type[1] / worst_type[1]) - 1) * 100:.0f}% engagement",
                generated_at=datetime.utcnow()
            )
        
        return None