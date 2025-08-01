"""
Thread comparison and benchmarking service for Threadr analytics.
Provides intelligent comparisons and industry benchmarks.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import statistics
from dataclasses import dataclass

from ..models.analytics import ThreadAnalytics, UserAnalyticsSummary


class ComparisonType(str, Enum):
    """Types of comparisons available"""
    THREAD_VS_THREAD = "thread_vs_thread"
    THREAD_VS_AVERAGE = "thread_vs_average"
    PERIOD_VS_PERIOD = "period_vs_period"
    USER_VS_INDUSTRY = "user_vs_industry"
    CONTENT_TYPE = "content_type"
    THREAD_LENGTH = "thread_length"
    TIME_OF_DAY = "time_of_day"
    DAY_OF_WEEK = "day_of_week"


@dataclass
class ComparisonResult:
    """Result of a comparison analysis"""
    comparison_type: ComparisonType
    primary_subject: str
    comparison_subject: str
    metrics: Dict[str, Any]
    insights: List[str]
    confidence_score: float
    created_at: datetime


@dataclass
class BenchmarkData:
    """Industry benchmark data"""
    metric_name: str
    industry_median: float
    industry_top_10_percent: float
    industry_top_25_percent: float
    user_percentile: float
    sample_size: int


class AnalyticsComparison:
    """Service for comparing thread performance and generating benchmarks"""
    
    def __init__(self, analytics_data: List[ThreadAnalytics]):
        self.analytics_data = analytics_data
        self.industry_benchmarks = self._load_industry_benchmarks()
    
    def compare_threads(self, thread_id_1: str, thread_id_2: str) -> ComparisonResult:
        """Compare two specific threads across all metrics"""
        
        thread_1 = self._get_thread_by_id(thread_id_1)
        thread_2 = self._get_thread_by_id(thread_id_2)
        
        if not thread_1 or not thread_2:
            raise ValueError("One or both threads not found")
        
        metrics = {
            "impressions": {
                "thread_1": thread_1.impressions,
                "thread_2": thread_2.impressions,
                "difference": thread_1.impressions - thread_2.impressions,
                "percentage_change": self._calculate_percentage_change(
                    thread_2.impressions, thread_1.impressions
                )
            },
            "engagement_rate": {
                "thread_1": thread_1.engagement_rate,
                "thread_2": thread_2.engagement_rate,
                "difference": thread_1.engagement_rate - thread_2.engagement_rate,
                "percentage_change": self._calculate_percentage_change(
                    thread_2.engagement_rate, thread_1.engagement_rate
                )
            },
            "completion_rate": {
                "thread_1": thread_1.completion_rate,
                "thread_2": thread_2.completion_rate,
                "difference": thread_1.completion_rate - thread_2.completion_rate,
                "percentage_change": self._calculate_percentage_change(
                    thread_2.completion_rate, thread_1.completion_rate
                )
            },
            "follower_growth": {
                "thread_1": thread_1.follower_growth,
                "thread_2": thread_2.follower_growth,
                "difference": thread_1.follower_growth - thread_2.follower_growth,
                "percentage_change": self._calculate_percentage_change(
                    thread_2.follower_growth, thread_1.follower_growth
                ) if thread_2.follower_growth != 0 else 0
            },
            "thread_length": {
                "thread_1": thread_1.thread_length,
                "thread_2": thread_2.thread_length,
                "difference": thread_1.thread_length - thread_2.thread_length
            }
        }
        
        insights = self._generate_thread_comparison_insights(thread_1, thread_2, metrics)
        confidence_score = self._calculate_comparison_confidence(thread_1, thread_2)
        
        return ComparisonResult(
            comparison_type=ComparisonType.THREAD_VS_THREAD,
            primary_subject=thread_1.title,
            comparison_subject=thread_2.title,
            metrics=metrics,
            insights=insights,
            confidence_score=confidence_score,
            created_at=datetime.utcnow()
        )
    
    def compare_thread_to_user_average(self, thread_id: str, user_id: str, 
                                     period_days: int = 90) -> ComparisonResult:
        """Compare a thread to user's average performance"""
        
        thread = self._get_thread_by_id(thread_id)
        if not thread:
            raise ValueError("Thread not found")
        
        user_threads = [
            t for t in self.analytics_data 
            if t.user_id == user_id and 
            t.created_at >= datetime.utcnow() - timedelta(days=period_days) and
            t.thread_id != thread_id
        ]
        
        if not user_threads:
            raise ValueError("Insufficient user data for comparison")
        
        avg_metrics = self._calculate_average_metrics(user_threads)
        
        metrics = {
            "impressions": {
                "thread": thread.impressions,
                "user_average": avg_metrics["impressions"],
                "vs_average_change": self._calculate_percentage_change(
                    avg_metrics["impressions"], thread.impressions
                ),
                "percentile": self._calculate_percentile(
                    [t.impressions for t in user_threads], thread.impressions
                )
            },
            "engagement_rate": {
                "thread": thread.engagement_rate,
                "user_average": avg_metrics["engagement_rate"],
                "vs_average_change": self._calculate_percentage_change(
                    avg_metrics["engagement_rate"], thread.engagement_rate
                ),
                "percentile": self._calculate_percentile(
                    [t.engagement_rate for t in user_threads], thread.engagement_rate
                )
            },
            "completion_rate": {
                "thread": thread.completion_rate,
                "user_average": avg_metrics["completion_rate"],
                "vs_average_change": self._calculate_percentage_change(
                    avg_metrics["completion_rate"], thread.completion_rate
                ),
                "percentile": self._calculate_percentile(
                    [t.completion_rate for t in user_threads], thread.completion_rate
                )
            }
        }
        
        insights = self._generate_vs_average_insights(thread, avg_metrics, metrics)
        confidence_score = len(user_threads) / 50.0  # More data = higher confidence
        
        return ComparisonResult(
            comparison_type=ComparisonType.THREAD_VS_AVERAGE,
            primary_subject=thread.title,
            comparison_subject=f"Your {period_days}-day average",
            metrics=metrics,
            insights=insights,
            confidence_score=min(confidence_score, 1.0),
            created_at=datetime.utcnow()
        )
    
    def compare_periods(self, user_id: str, current_period_days: int, 
                       comparison_period_days: int) -> ComparisonResult:
        """Compare current period performance to a previous period"""
        
        now = datetime.utcnow()
        current_start = now - timedelta(days=current_period_days)
        comparison_start = current_start - timedelta(days=comparison_period_days)
        comparison_end = current_start
        
        current_threads = [
            t for t in self.analytics_data
            if t.user_id == user_id and current_start <= t.created_at <= now
        ]
        
        comparison_threads = [
            t for t in self.analytics_data
            if t.user_id == user_id and 
            comparison_start <= t.created_at <= comparison_end
        ]
        
        if not current_threads or not comparison_threads:
            raise ValueError("Insufficient data for period comparison")
        
        current_metrics = self._calculate_average_metrics(current_threads)
        comparison_metrics = self._calculate_average_metrics(comparison_threads)
        
        metrics = {
            "thread_count": {
                "current": len(current_threads),
                "previous": len(comparison_threads),
                "change": len(current_threads) - len(comparison_threads),
                "percentage_change": self._calculate_percentage_change(
                    len(comparison_threads), len(current_threads)
                )
            },
            "total_impressions": {
                "current": sum(t.impressions for t in current_threads),
                "previous": sum(t.impressions for t in comparison_threads),
                "percentage_change": self._calculate_percentage_change(
                    sum(t.impressions for t in comparison_threads),
                    sum(t.impressions for t in current_threads)
                )
            },
            "avg_engagement_rate": {
                "current": current_metrics["engagement_rate"],
                "previous": comparison_metrics["engagement_rate"],
                "percentage_change": self._calculate_percentage_change(
                    comparison_metrics["engagement_rate"],
                    current_metrics["engagement_rate"]
                )
            },
            "total_follower_growth": {
                "current": sum(t.follower_growth for t in current_threads),
                "previous": sum(t.follower_growth for t in comparison_threads),
                "percentage_change": self._calculate_percentage_change(
                    sum(t.follower_growth for t in comparison_threads),
                    sum(t.follower_growth for t in current_threads)
                )
            }
        }
        
        insights = self._generate_period_comparison_insights(
            current_threads, comparison_threads, metrics
        )
        
        return ComparisonResult(
            comparison_type=ComparisonType.PERIOD_VS_PERIOD,
            primary_subject=f"Last {current_period_days} days",
            comparison_subject=f"Previous {comparison_period_days} days",
            metrics=metrics,
            insights=insights,
            confidence_score=0.8,  # Period comparisons are generally reliable
            created_at=datetime.utcnow()
        )
    
    def get_industry_benchmarks(self, user_id: str) -> List[BenchmarkData]:
        """Get industry benchmarks for user's performance"""
        
        user_threads = [t for t in self.analytics_data if t.user_id == user_id]
        if not user_threads:
            return []
        
        user_avg_metrics = self._calculate_average_metrics(user_threads)
        benchmarks = []
        
        for metric_name, benchmark_data in self.industry_benchmarks.items():
            user_value = user_avg_metrics.get(metric_name, 0)
            percentile = self._calculate_user_percentile(user_value, benchmark_data)
            
            benchmarks.append(BenchmarkData(
                metric_name=metric_name,
                industry_median=benchmark_data["median"],
                industry_top_10_percent=benchmark_data["top_10"],
                industry_top_25_percent=benchmark_data["top_25"],
                user_percentile=percentile,
                sample_size=benchmark_data["sample_size"]
            ))
        
        return benchmarks
    
    def analyze_content_type_performance(self, user_id: str) -> Dict[str, Any]:
        """Analyze performance by content type (if we can infer it)"""
        
        user_threads = [t for t in self.analytics_data if t.user_id == user_id]
        
        # Group by inferred content type
        content_types = {
            "tutorial": [],
            "opinion": [],
            "news": [],
            "personal": [],
            "promotional": [],
            "other": []
        }
        
        for thread in user_threads:
            content_type = self._infer_content_type(thread)
            content_types[content_type].append(thread)
        
        results = {}
        for content_type, threads in content_types.items():
            if threads:
                avg_metrics = self._calculate_average_metrics(threads)
                results[content_type] = {
                    "count": len(threads),
                    "avg_engagement_rate": avg_metrics["engagement_rate"],
                    "avg_impressions": avg_metrics["impressions"],
                    "avg_completion_rate": avg_metrics["completion_rate"],
                    "total_follower_growth": sum(t.follower_growth for t in threads)
                }
        
        return results
    
    def analyze_optimal_timing(self, user_id: str) -> Dict[str, Any]:
        """Analyze optimal posting times based on performance"""
        
        user_threads = [
            t for t in self.analytics_data 
            if t.user_id == user_id and t.posted_at
        ]
        
        if not user_threads:
            return {}
        
        # Group by hour of day
        hourly_performance = {}
        for hour in range(24):
            hour_threads = [
                t for t in user_threads 
                if t.posted_at.hour == hour
            ]
            if hour_threads:
                avg_metrics = self._calculate_average_metrics(hour_threads)
                hourly_performance[hour] = {
                    "count": len(hour_threads),
                    "avg_engagement_rate": avg_metrics["engagement_rate"],
                    "avg_impressions": avg_metrics["impressions"]
                }
        
        # Group by day of week
        daily_performance = {}
        for day in range(7):  # 0=Monday, 6=Sunday
            day_threads = [
                t for t in user_threads 
                if t.posted_at.weekday() == day
            ]
            if day_threads:
                avg_metrics = self._calculate_average_metrics(day_threads)
                daily_performance[day] = {
                    "count": len(day_threads),
                    "avg_engagement_rate": avg_metrics["engagement_rate"],
                    "avg_impressions": avg_metrics["impressions"]
                }
        
        # Find optimal times
        best_hour = max(
            hourly_performance.items(),
            key=lambda x: x[1]["avg_engagement_rate"]
        )[0] if hourly_performance else None
        
        best_day = max(
            daily_performance.items(),
            key=lambda x: x[1]["avg_engagement_rate"]
        )[0] if daily_performance else None
        
        return {
            "hourly_performance": hourly_performance,
            "daily_performance": daily_performance,
            "optimal_hour": best_hour,
            "optimal_day": best_day,
            "day_names": ["Monday", "Tuesday", "Wednesday", "Thursday", 
                         "Friday", "Saturday", "Sunday"]
        }
    
    # Helper Methods
    
    def _get_thread_by_id(self, thread_id: str) -> Optional[ThreadAnalytics]:
        """Get thread by ID"""
        for thread in self.analytics_data:
            if thread.thread_id == thread_id:
                return thread
        return None
    
    def _calculate_percentage_change(self, old_value: float, new_value: float) -> float:
        """Calculate percentage change between two values"""
        if old_value == 0:
            return 100.0 if new_value > 0 else 0.0
        return ((new_value - old_value) / old_value) * 100
    
    def _calculate_average_metrics(self, threads: List[ThreadAnalytics]) -> Dict[str, float]:
        """Calculate average metrics for a list of threads"""
        if not threads:
            return {}
        
        return {
            "impressions": sum(t.impressions for t in threads) / len(threads),
            "engagement_rate": sum(t.engagement_rate for t in threads) / len(threads),
            "completion_rate": sum(t.completion_rate for t in threads) / len(threads),
            "click_through_rate": sum(t.click_through_rate for t in threads) / len(threads),
            "follower_growth": sum(t.follower_growth for t in threads) / len(threads)
        }
    
    def _calculate_percentile(self, values: List[float], target_value: float) -> float:
        """Calculate what percentile the target value represents"""
        if not values:
            return 50.0
        
        values_sorted = sorted(values)
        position = sum(1 for v in values_sorted if v <= target_value)
        return (position / len(values_sorted)) * 100
    
    def _calculate_comparison_confidence(self, thread_1: ThreadAnalytics, 
                                       thread_2: ThreadAnalytics) -> float:
        """Calculate confidence score for thread comparison"""
        # Higher confidence for threads with more impressions and recent data
        base_confidence = 0.5
        
        # Boost confidence based on impression count
        min_impressions = min(thread_1.impressions, thread_2.impressions)
        impression_boost = min(min_impressions / 10000, 0.3)
        
        # Reduce confidence for very old threads
        days_old = max(
            (datetime.utcnow() - thread_1.created_at).days,
            (datetime.utcnow() - thread_2.created_at).days
        )
        age_penalty = min(days_old / 365, 0.2)
        
        return min(base_confidence + impression_boost - age_penalty, 1.0)
    
    def _generate_thread_comparison_insights(self, thread_1: ThreadAnalytics, 
                                           thread_2: ThreadAnalytics, 
                                           metrics: Dict[str, Any]) -> List[str]:
        """Generate insights for thread-to-thread comparison"""
        insights = []
        
        # Engagement rate insights
        eng_diff = metrics["engagement_rate"]["percentage_change"]
        if abs(eng_diff) > 20:
            better_thread = thread_1.title if eng_diff > 0 else thread_2.title
            insights.append(
                f"'{better_thread}' had {abs(eng_diff):.1f}% higher engagement rate, "
                f"suggesting its content or timing resonated better with your audience."
            )
        
        # Thread length analysis
        length_diff = metrics["thread_length"]["difference"]
        if abs(length_diff) > 3:
            if length_diff > 0 and metrics["engagement_rate"]["difference"] > 0:
                insights.append(
                    f"The longer thread ({thread_1.thread_length} tweets) performed better, "
                    f"indicating your audience appreciates more detailed content."
                )
            elif length_diff < 0 and metrics["engagement_rate"]["difference"] > 0:
                insights.append(
                    f"The shorter thread ({thread_1.thread_length} tweets) performed better, "
                    f"suggesting more concise content drives higher engagement."
                )
        
        # Follower growth insights
        if metrics["follower_growth"]["difference"] > 5:
            insights.append(
                f"'{thread_1.title}' drove {metrics['follower_growth']['difference']} "
                f"more followers, indicating stronger audience acquisition potential."
            )
        
        return insights
    
    def _generate_vs_average_insights(self, thread: ThreadAnalytics, 
                                    avg_metrics: Dict[str, float], 
                                    metrics: Dict[str, Any]) -> List[str]:
        """Generate insights for thread vs average comparison"""
        insights = []
        
        # Performance ranking
        eng_percentile = metrics["engagement_rate"]["percentile"]
        if eng_percentile >= 90:
            insights.append(
                f"This thread is in your top 10% performers with "
                f"{thread.engagement_rate:.1f}% engagement rate."
            )
        elif eng_percentile >= 75:
            insights.append(
                f"This thread performed well, ranking in your top 25% with "
                f"{thread.engagement_rate:.1f}% engagement rate."
            )
        elif eng_percentile <= 25:
            insights.append(
                f"This thread underperformed compared to your average, "
                f"consider analyzing what made your top performers successful."
            )
        
        # Specific metric callouts
        for metric, data in metrics.items():
            change = data.get("vs_average_change", 0)
            if abs(change) > 50:
                direction = "higher" if change > 0 else "lower"
                insights.append(
                    f"{metric.replace('_', ' ').title()} was {abs(change):.1f}% {direction} "
                    f"than your average."
                )
        
        return insights
    
    def _generate_period_comparison_insights(self, current_threads: List[ThreadAnalytics],
                                           comparison_threads: List[ThreadAnalytics],
                                           metrics: Dict[str, Any]) -> List[str]:
        """Generate insights for period comparison"""
        insights = []
        
        # Overall trend
        eng_change = metrics["avg_engagement_rate"]["percentage_change"]
        if eng_change > 10:
            insights.append(
                f"Your engagement rate improved by {eng_change:.1f}%, "
                f"indicating your content strategy is working well."
            )
        elif eng_change < -10:
            insights.append(
                f"Your engagement rate decreased by {abs(eng_change):.1f}%, "
                f"consider reviewing your top performers for successful patterns."
            )
        
        # Volume insights
        thread_change = metrics["thread_count"]["change"]
        if thread_change > 0 and eng_change > 0:
            insights.append(
                f"You published {thread_change} more threads and maintained quality, "
                f"showing good content scaling."
            )
        elif thread_change > 0 and eng_change < -5:
            insights.append(
                f"While you published more content, engagement dropped slightly. "
                f"Focus on quality over quantity."
            )
        
        # Growth insights
        follower_change = metrics["total_follower_growth"]["percentage_change"]
        if follower_change > 20:
            insights.append(
                f"Follower growth accelerated by {follower_change:.1f}%, "
                f"indicating strong audience building momentum."
            )
        
        return insights
    
    def _infer_content_type(self, thread: ThreadAnalytics) -> str:
        """Infer content type from thread characteristics"""
        # Simple heuristic based on title keywords
        title_lower = thread.title.lower()
        
        if any(word in title_lower for word in ["how to", "guide", "tutorial", "step", "learn"]):
            return "tutorial"
        elif any(word in title_lower for word in ["think", "opinion", "believe", "should"]):
            return "opinion"
        elif any(word in title_lower for word in ["news", "breaking", "update", "announces"]):
            return "news"
        elif any(word in title_lower for word in ["my", "i ", "personal", "story", "journey"]):
            return "personal"
        elif any(word in title_lower for word in ["buy", "sale", "product", "launch", "offer"]):
            return "promotional"
        else:
            return "other"
    
    def _load_industry_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Load industry benchmark data (mock data for now)"""
        return {
            "engagement_rate": {
                "median": 2.1,
                "top_25": 4.2,
                "top_10": 7.8,
                "sample_size": 10000
            },
            "completion_rate": {
                "median": 45.0,
                "top_25": 65.0,
                "top_10": 82.0,
                "sample_size": 8500
            },
            "click_through_rate": {
                "median": 1.8,
                "top_25": 3.5,
                "top_10": 6.2,
                "sample_size": 9200
            }
        }
    
    def _calculate_user_percentile(self, user_value: float, 
                                 benchmark_data: Dict[str, float]) -> float:
        """Calculate user's percentile in industry"""
        if user_value >= benchmark_data["top_10"]:
            return 90.0
        elif user_value >= benchmark_data["top_25"]:
            return 75.0
        elif user_value >= benchmark_data["median"]:
            return 50.0
        else:
            # Estimate percentile below median
            return (user_value / benchmark_data["median"]) * 50