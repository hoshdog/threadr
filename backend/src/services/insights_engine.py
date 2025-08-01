"""
AI-powered insights and recommendations engine for Threadr analytics.
Generates actionable insights to help users improve their thread performance.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import statistics
from collections import defaultdict, Counter

from ..models.analytics import ThreadAnalytics, TweetMetrics
from .analytics_comparison import AnalyticsComparison, BenchmarkData


class InsightType(str, Enum):
    """Types of insights generated"""
    PERFORMANCE = "performance"
    TIMING = "timing"
    CONTENT = "content"
    AUDIENCE = "audience"
    OPTIMIZATION = "optimization"
    TREND = "trend"
    BENCHMARK = "benchmark"


class InsightPriority(str, Enum):
    """Priority levels for insights"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Insight:
    """Individual insight with actionable recommendations"""
    id: str
    type: InsightType
    priority: InsightPriority
    title: str
    message: str
    impact_description: str
    recommended_actions: List[str]
    supporting_data: Dict[str, Any]
    confidence_score: float
    created_at: datetime


@dataclass
class InsightSummary:
    """Summary of insights for dashboard display"""
    total_insights: int
    critical_count: int
    high_priority_count: int
    top_recommendation: str
    performance_score: float
    improvement_potential: float


class InsightsEngine:
    """Generate actionable insights from thread analytics"""
    
    def __init__(self, analytics_data: List[ThreadAnalytics], 
                 tweet_data: List[TweetMetrics] = None):
        self.analytics_data = analytics_data
        self.tweet_data = tweet_data or []
        self.comparison_service = AnalyticsComparison(analytics_data)
        
    def generate_user_insights(self, user_id: str, 
                             period_days: int = 90) -> List[Insight]:
        """Generate comprehensive insights for a user"""
        
        user_threads = [
            t for t in self.analytics_data 
            if t.user_id == user_id and 
            t.created_at >= datetime.utcnow() - timedelta(days=period_days)
        ]
        
        if not user_threads:
            return []
        
        insights = []
        
        # Performance insights
        insights.extend(self._analyze_performance_patterns(user_threads))
        
        # Timing optimization insights
        insights.extend(self._analyze_timing_patterns(user_threads))
        
        # Content optimization insights
        insights.extend(self._analyze_content_patterns(user_threads))
        
        # Audience engagement insights
        insights.extend(self._analyze_audience_behavior(user_threads))
        
        # Benchmark comparisons
        insights.extend(self._analyze_benchmark_performance(user_id))
        
        # Trend analysis
        insights.extend(self._analyze_trends(user_threads))
        
        # Sort by priority and confidence
        insights.sort(key=lambda x: (x.priority.value, -x.confidence_score))
        
        return insights[:20]  # Return top 20 insights
    
    def get_insights_summary(self, insights: List[Insight]) -> InsightSummary:
        """Generate summary of insights for dashboard"""
        
        if not insights:
            return InsightSummary(
                total_insights=0,
                critical_count=0,
                high_priority_count=0,
                top_recommendation="Keep creating content!",
                performance_score=75.0,
                improvement_potential=25.0
            )
        
        critical_count = sum(1 for i in insights if i.priority == InsightPriority.CRITICAL)
        high_priority_count = sum(1 for i in insights if i.priority == InsightPriority.HIGH)
        
        # Calculate performance score based on insights
        performance_score = self._calculate_performance_score(insights)
        improvement_potential = 100 - performance_score
        
        top_recommendation = insights[0].recommended_actions[0] if insights[0].recommended_actions else "Continue optimizing your content"
        
        return InsightSummary(
            total_insights=len(insights),
            critical_count=critical_count,
            high_priority_count=high_priority_count,
            top_recommendation=top_recommendation,
            performance_score=performance_score,
            improvement_potential=improvement_potential
        )
    
    def _analyze_performance_patterns(self, threads: List[ThreadAnalytics]) -> List[Insight]:
        """Analyze performance patterns and identify issues/opportunities"""
        insights = []
        
        if len(threads) < 5:
            return insights
        
        # Analyze engagement rate distribution
        engagement_rates = [t.engagement_rate for t in threads]
        avg_engagement = statistics.mean(engagement_rates)
        engagement_std = statistics.stdev(engagement_rates) if len(engagement_rates) > 1 else 0
        
        # High variance insight
        if engagement_std > avg_engagement * 0.5:
            insights.append(Insight(
                id=f"perf_variance_{datetime.utcnow().timestamp()}",
                type=InsightType.PERFORMANCE,
                priority=InsightPriority.MEDIUM,
                title="Inconsistent Performance",
                message=f"Your thread performance varies significantly (σ={engagement_std:.1f}%). Some threads perform much better than others.",
                impact_description="High variance suggests untapped potential for consistent growth",
                recommended_actions=[
                    "Analyze your top 3 performing threads to identify success patterns",
                    "Create a content checklist based on your best performers",
                    "Test similar formats and topics that worked well previously"
                ],
                supporting_data={
                    "avg_engagement": avg_engagement,
                    "std_deviation": engagement_std,
                    "variance_coefficient": engagement_std / avg_engagement
                },
                confidence_score=0.85,
                created_at=datetime.utcnow()
            ))
        
        # Low completion rate insight
        completion_rates = [t.completion_rate for t in threads if t.completion_rate > 0]
        if completion_rates:
            avg_completion = statistics.mean(completion_rates)
            if avg_completion < 50:
                insights.append(Insight(
                    id=f"completion_low_{datetime.utcnow().timestamp()}",
                    type=InsightType.CONTENT,
                    priority=InsightPriority.HIGH,
                    title="Low Thread Completion Rate",
                    message=f"Only {avg_completion:.1f}% of users read your full threads on average.",
                    impact_description="Low completion rates limit engagement and reduce thread effectiveness",
                    recommended_actions=[
                        "Reduce thread length - aim for 5-8 tweets maximum",
                        "Improve your hook (first tweet) to build momentum",
                        "Add more engaging elements like questions or surprising facts",
                        "Use thread numbering to show progress (1/7, 2/7, etc.)"
                    ],
                    supporting_data={
                        "avg_completion_rate": avg_completion,
                        "threads_analyzed": len(completion_rates)
                    },
                    confidence_score=0.8,
                    created_at=datetime.utcnow()
                ))
        
        # Declining performance trend
        if len(threads) >= 10:
            recent_threads = sorted(threads, key=lambda x: x.created_at)[-5:]
            older_threads = sorted(threads, key=lambda x: x.created_at)[-10:-5]
            
            recent_avg = statistics.mean([t.engagement_rate for t in recent_threads])
            older_avg = statistics.mean([t.engagement_rate for t in older_threads])
            
            if recent_avg < older_avg * 0.8:  # 20% decline
                insights.append(Insight(
                    id=f"declining_perf_{datetime.utcnow().timestamp()}",
                    type=InsightType.TREND,
                    priority=InsightPriority.HIGH,
                    title="Declining Performance Trend",
                    message=f"Your recent threads are performing {((older_avg - recent_avg) / older_avg * 100):.1f}% worse than previous ones.",
                    impact_description="Declining performance may indicate audience fatigue or algorithm changes",
                    recommended_actions=[
                        "Experiment with new content formats and topics",
                        "Engage more with your audience through replies and conversations",
                        "Analyze what changed in your approach recently",
                        "Consider taking a short break to avoid burnout"
                    ],
                    supporting_data={
                        "recent_avg": recent_avg,
                        "older_avg": older_avg,
                        "decline_percentage": (older_avg - recent_avg) / older_avg * 100
                    },
                    confidence_score=0.75,
                    created_at=datetime.utcnow()
                ))
        
        return insights
    
    def _analyze_timing_patterns(self, threads: List[ThreadAnalytics]) -> List[Insight]:
        """Analyze optimal timing patterns"""
        insights = []
        
        posted_threads = [t for t in threads if t.posted_at]
        if len(posted_threads) < 10:
            return insights
        
        # Analyze day of week performance
        day_performance = defaultdict(list)
        for thread in posted_threads:
            day = thread.posted_at.weekday()
            day_performance[day].append(thread.engagement_rate)
        
        day_averages = {
            day: statistics.mean(rates) 
            for day, rates in day_performance.items() 
            if len(rates) >= 2
        }
        
        if len(day_averages) >= 3:
            best_day = max(day_averages.items(), key=lambda x: x[1])
            worst_day = min(day_averages.items(), key=lambda x: x[1])
            
            if best_day[1] > worst_day[1] * 1.3:  # 30% difference
                day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                insights.append(Insight(
                    id=f"timing_day_{datetime.utcnow().timestamp()}",
                    type=InsightType.TIMING,
                    priority=InsightPriority.MEDIUM,
                    title="Optimal Posting Day Identified",
                    message=f"{day_names[best_day[0]]} is your best performing day with {best_day[1]:.1f}% avg engagement.",
                    impact_description=f"Posting on optimal days could improve engagement by {((best_day[1] - worst_day[1]) / worst_day[1] * 100):.1f}%",
                    recommended_actions=[
                        f"Schedule more important threads for {day_names[best_day[0]]}",
                        f"Avoid posting on {day_names[worst_day[0]]} unless necessary",
                        "Test posting at different times on your best day",
                        "Plan your content calendar around optimal days"
                    ],
                    supporting_data={
                        "day_performance": {day_names[k]: v for k, v in day_averages.items()},
                        "best_day": day_names[best_day[0]],
                        "improvement_potential": (best_day[1] - worst_day[1]) / worst_day[1] * 100
                    },
                    confidence_score=0.7,
                    created_at=datetime.utcnow()
                ))
        
        # Analyze hour performance
        hour_performance = defaultdict(list)
        for thread in posted_threads:
            hour = thread.posted_at.hour
            hour_performance[hour].append(thread.engagement_rate)
        
        hour_averages = {
            hour: statistics.mean(rates) 
            for hour, rates in hour_performance.items() 
            if len(rates) >= 2
        }
        
        if len(hour_averages) >= 5:
            best_hour = max(hour_averages.items(), key=lambda x: x[1])
            
            insights.append(Insight(
                id=f"timing_hour_{datetime.utcnow().timestamp()}",
                type=InsightType.TIMING,
                priority=InsightPriority.LOW,
                title="Peak Engagement Hour",
                message=f"{best_hour[0]:02d}:00 is your peak engagement hour with {best_hour[1]:.1f}% avg engagement.",
                impact_description="Posting at optimal times increases visibility and engagement",
                recommended_actions=[
                    f"Schedule important threads around {best_hour[0]:02d}:00",
                    "Use scheduling tools to post at consistent optimal times",
                    "Test posting 1-2 hours before and after your peak time"
                ],
                supporting_data={
                    "hour_performance": hour_averages,
                    "optimal_hour": best_hour[0]
                },
                confidence_score=0.6,
                created_at=datetime.utcnow()
            ))
        
        return insights
    
    def _analyze_content_patterns(self, threads: List[ThreadAnalytics]) -> List[Insight]:
        """Analyze content patterns and optimization opportunities"""
        insights = []
        
        # Thread length analysis
        if len(threads) >= 10:
            length_performance = {}
            for thread in threads:
                length_bucket = self._get_length_bucket(thread.thread_length)
                if length_bucket not in length_performance:
                    length_performance[length_bucket] = []
                length_performance[length_bucket].append(thread.engagement_rate)
            
            # Find optimal length
            avg_by_length = {
                length: statistics.mean(rates) 
                for length, rates in length_performance.items() 
                if len(rates) >= 3
            }
            
            if len(avg_by_length) >= 2:
                best_length = max(avg_by_length.items(), key=lambda x: x[1])
                insights.append(Insight(
                    id=f"content_length_{datetime.utcnow().timestamp()}",
                    type=InsightType.CONTENT,
                    priority=InsightPriority.MEDIUM,
                    title="Optimal Thread Length",
                    message=f"{best_length[0]} threads perform best with {best_length[1]:.1f}% avg engagement.",
                    impact_description="Optimizing thread length can significantly improve engagement",
                    recommended_actions=[
                        f"Target {best_length[0].lower()} for your threads",
                        "Break longer content into multiple shorter threads",
                        "Combine short threads if they're underperforming"
                    ],
                    supporting_data={
                        "length_performance": avg_by_length,
                        "optimal_length": best_length[0]
                    },
                    confidence_score=0.7,
                    created_at=datetime.utcnow()
                ))
        
        # Hook performance analysis
        if self.tweet_data:
            user_hooks = [t for t in self.tweet_data if t.is_hook]
            if len(user_hooks) >= 5:
                hook_engagement = [t.engagement_rate for t in user_hooks]
                avg_hook_engagement = statistics.mean(hook_engagement)
                
                # Find high-performing hooks
                top_hooks = sorted(user_hooks, key=lambda x: x.engagement_rate, reverse=True)[:3]
                
                if avg_hook_engagement < 3.0:  # Low hook performance
                    insights.append(Insight(
                        id=f"hook_performance_{datetime.utcnow().timestamp()}",
                        type=InsightType.CONTENT,
                        priority=InsightPriority.HIGH,
                        title="Weak Thread Hooks",
                        message=f"Your first tweets average only {avg_hook_engagement:.1f}% engagement.",
                        impact_description="Strong hooks are crucial for thread success - they determine if people continue reading",
                        recommended_actions=[
                            "Start with a compelling question or surprising statement",
                            "Use numbers or statistics to grab attention",
                            "Promise value ('Here's how to...', 'The secret to...')",
                            "Create curiosity gaps that make people want to read more"
                        ],
                        supporting_data={
                            "avg_hook_engagement": avg_hook_engagement,
                            "hooks_analyzed": len(user_hooks),
                            "top_hooks": [h.content[:100] + "..." for h in top_hooks]
                        },
                        confidence_score=0.8,
                        created_at=datetime.utcnow()
                    ))
        
        return insights
    
    def _analyze_audience_behavior(self, threads: List[ThreadAnalytics]) -> List[Insight]:
        """Analyze audience engagement patterns"""
        insights = []
        
        # Reply-to-like ratio analysis
        threads_with_engagement = [t for t in threads if t.likes > 0]
        if len(threads_with_engagement) >= 5:
            reply_ratios = [t.replies / max(t.likes, 1) for t in threads_with_engagement]
            avg_reply_ratio = statistics.mean(reply_ratios)
            
            if avg_reply_ratio > 0.3:  # High discussion threads
                insights.append(Insight(
                    id=f"audience_discussion_{datetime.utcnow().timestamp()}",
                    type=InsightType.AUDIENCE,
                    priority=InsightPriority.MEDIUM,
                    title="High Discussion Engagement",
                    message=f"Your threads generate {avg_reply_ratio:.1f} replies per like - great for discussions!",
                    impact_description="High reply ratios indicate engaged audience and algorithm boost",
                    recommended_actions=[
                        "Ask more questions to encourage replies",
                        "Share controversial (but respectful) opinions",
                        "End threads with calls-to-action for engagement",
                        "Respond to replies quickly to boost discussion"
                    ],
                    supporting_data={
                        "avg_reply_ratio": avg_reply_ratio,
                        "threads_analyzed": len(threads_with_engagement)
                    },
                    confidence_score=0.7,
                    created_at=datetime.utcnow()
                ))
            elif avg_reply_ratio < 0.1:  # Low discussion
                insights.append(Insight(
                    id=f"audience_low_discussion_{datetime.utcnow().timestamp()}",
                    type=InsightType.AUDIENCE,
                    priority=InsightPriority.MEDIUM,
                    title="Low Discussion Engagement",
                    message=f"Your threads only generate {avg_reply_ratio:.2f} replies per like.",
                    impact_description="Low reply rates suggest passive audience - missing engagement opportunities",
                    recommended_actions=[
                        "Ask specific questions in your threads",
                        "Share personal experiences people can relate to",
                        "Create polls or ask for opinions",
                        "End with 'What do you think?' or similar CTAs"
                    ],
                    supporting_data={
                        "avg_reply_ratio": avg_reply_ratio,
                        "threads_analyzed": len(threads_with_engagement)
                    },
                    confidence_score=0.7,
                    created_at=datetime.utcnow()
                ))
        
        return insights
    
    def _analyze_benchmark_performance(self, user_id: str) -> List[Insight]:
        """Compare user performance to industry benchmarks"""
        insights = []
        
        benchmarks = self.comparison_service.get_industry_benchmarks(user_id)
        
        for benchmark in benchmarks:
            if benchmark.user_percentile <= 25:  # Bottom quartile
                insights.append(Insight(
                    id=f"benchmark_{benchmark.metric_name}_{datetime.utcnow().timestamp()}",
                    type=InsightType.BENCHMARK,
                    priority=InsightPriority.HIGH,
                    title=f"Below Industry Average: {benchmark.metric_name.title()}",
                    message=f"Your {benchmark.metric_name.replace('_', ' ')} is in the bottom 25% of creators.",
                    impact_description=f"Significant room for improvement - industry median is {benchmark.industry_median:.1f}%",
                    recommended_actions=[
                        f"Study top performers in your niche",
                        f"Focus on improving {benchmark.metric_name.replace('_', ' ')}",
                        "Consider hiring a social media consultant",
                        "Join creator communities for tips and feedback"
                    ],
                    supporting_data={
                        "user_percentile": benchmark.user_percentile,
                        "industry_median": benchmark.industry_median,
                        "industry_top_25": benchmark.industry_top_25_percent
                    },
                    confidence_score=0.9,
                    created_at=datetime.utcnow()
                ))
            elif benchmark.user_percentile >= 90:  # Top decile
                insights.append(Insight(
                    id=f"benchmark_top_{benchmark.metric_name}_{datetime.utcnow().timestamp()}",
                    type=InsightType.BENCHMARK,
                    priority=InsightPriority.LOW,
                    title=f"Top Performer: {benchmark.metric_name.title()}",
                    message=f"Your {benchmark.metric_name.replace('_', ' ')} is in the top 10% of creators!",
                    impact_description="Excellent performance - consider sharing your knowledge",
                    recommended_actions=[
                        "Document your successful strategies", 
                        "Consider creating educational content about your methods",
                        "Maintain consistency in what's working",
                        "Help other creators in your community"
                    ],
                    supporting_data={
                        "user_percentile": benchmark.user_percentile,
                        "industry_top_10": benchmark.industry_top_10_percent
                    },
                    confidence_score=0.95,
                    created_at=datetime.utcnow()
                ))
        
        return insights
    
    def _analyze_trends(self, threads: List[ThreadAnalytics]) -> List[Insight]:
        """Analyze performance trends over time"""
        insights = []
        
        if len(threads) < 15:
            return insights
        
        # Sort by creation date
        sorted_threads = sorted(threads, key=lambda x: x.created_at)
        
        # Split into three periods
        period_size = len(sorted_threads) // 3
        early_period = sorted_threads[:period_size]
        middle_period = sorted_threads[period_size:2*period_size]
        recent_period = sorted_threads[2*period_size:]
        
        early_avg = statistics.mean([t.engagement_rate for t in early_period])
        middle_avg = statistics.mean([t.engagement_rate for t in middle_period])
        recent_avg = statistics.mean([t.engagement_rate for t in recent_period])
        
        # Identify trend
        if recent_avg > early_avg * 1.2:  # 20% improvement
            insights.append(Insight(
                id=f"trend_improving_{datetime.utcnow().timestamp()}",
                type=InsightType.TREND,
                priority=InsightPriority.LOW,
                title="Improving Performance Trend",
                message=f"Your engagement has improved {((recent_avg - early_avg) / early_avg * 100):.1f}% over time!",
                impact_description="Positive trend indicates effective learning and optimization",
                recommended_actions=[
                    "Continue with your current strategy",
                    "Document what changes led to improvement",
                    "Consider increasing posting frequency",
                    "Share your growth story with your audience"
                ],
                supporting_data={
                    "early_avg": early_avg,
                    "recent_avg": recent_avg,
                    "improvement": (recent_avg - early_avg) / early_avg * 100
                },
                confidence_score=0.8,
                created_at=datetime.utcnow()
            ))
        
        return insights
    
    # Helper Methods
    
    def _get_length_bucket(self, length: int) -> str:
        """Categorize thread length into buckets"""
        if length <= 3:
            return "Short (1-3 tweets)"
        elif length <= 7:
            return "Medium (4-7 tweets)"
        elif length <= 12:
            return "Long (8-12 tweets)"
        else:
            return "Very Long (13+ tweets)"
    
    def _calculate_performance_score(self, insights: List[Insight]) -> float:
        """Calculate overall performance score based on insights"""
        if not insights:
            return 75.0
        
        # Start with base score
        score = 75.0
        
        # Penalize for critical and high priority issues
        critical_penalty = sum(10 for i in insights if i.priority == InsightPriority.CRITICAL)
        high_penalty = sum(5 for i in insights if i.priority == InsightPriority.HIGH)
        
        # Bonus for positive insights (benchmarks, trends)
        positive_bonus = sum(5 for i in insights if "top performer" in i.title.lower() or "improving" in i.title.lower())
        
        final_score = max(0, min(100, score - critical_penalty - high_penalty + positive_bonus))
        
        return final_score