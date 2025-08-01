"""
Mock analytics data generator for Threadr development and testing.
Generates realistic thread performance data for dashboard development.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
from faker import Faker

from ..models.analytics import ThreadAnalytics, TweetMetrics, AnalyticsSnapshot


fake = Faker()


class MockAnalyticsGenerator:
    """Generate realistic mock analytics data for development"""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        fake.seed_instance(seed)
        
        # Common thread topics for realistic titles
        self.thread_topics = [
            "How to build a successful startup",
            "The future of artificial intelligence",
            "10 productivity tips that changed my life",
            "Why remote work is here to stay",
            "The psychology of social media addiction",
            "Lessons learned from my biggest failure",
            "Building habits that stick",
            "The art of effective communication",
            "Understanding cryptocurrency and blockchain",
            "My journey from zero to $1M revenue",
            "The importance of work-life balance",
            "How to learn anything faster",
            "The hidden costs of perfectionism",
            "Building a personal brand on social media",
            "The science of happiness and fulfillment",
            "Navigating career transitions successfully",
            "The power of compound interest",
            "Why storytelling matters in business",
            "Creating content that resonates",
            "The art of saying no and setting boundaries"
        ]
        
        # Content sources for variety
        self.content_sources = [
            "https://medium.com/@user/article-title",
            "https://dev.to/user/post-title",
            "https://substack.com/user/newsletter-title",  
            "https://blog.example.com/post-title",
            None  # Original content
        ]
    
    def generate_user_threads(self, user_id: str, num_threads: int = 50, 
                            days_back: int = 90) -> List[ThreadAnalytics]:
        """Generate realistic thread analytics for a user"""
        
        threads = []
        base_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Simulate user's improving performance over time
        skill_progression = self._generate_skill_progression(num_threads)
        
        for i in range(num_threads):
            thread_id = str(uuid.uuid4())
            created_at = base_date + timedelta(
                days=random.uniform(0, days_back),
                hours=random.uniform(0, 23)
            )
            
            # Some threads are posted later than created
            posted_at = None
            if random.random() > 0.1:  # 90% are posted
                posted_at = created_at + timedelta(
                    hours=random.uniform(0.5, 24),
                    minutes=random.uniform(0, 59)
                )
            
            # Generate performance based on skill level and various factors
            skill_factor = skill_progression[i]
            thread_length = self._generate_thread_length()
            topic = random.choice(self.thread_topics)
            
            # Base metrics influenced by skill and thread characteristics
            base_impressions = self._generate_impressions(skill_factor, thread_length, posted_at)
            engagement_metrics = self._generate_engagement_metrics(base_impressions, skill_factor, thread_length)
            
            thread = ThreadAnalytics(
                thread_id=thread_id,
                user_id=user_id,
                twitter_thread_id=f"tw_{random.randint(1000000000000000000, 9999999999999999999)}" if posted_at else None,
                title=topic,
                created_at=created_at,
                posted_at=posted_at,
                thread_length=thread_length,
                content_source=random.choice(self.content_sources),
                
                # Engagement metrics
                impressions=base_impressions,
                reach=int(base_impressions * random.uniform(0.6, 0.9)),
                likes=engagement_metrics['likes'],
                retweets=engagement_metrics['retweets'], 
                replies=engagement_metrics['replies'],
                bookmarks=engagement_metrics['bookmarks'],
                quotes=engagement_metrics['quotes'],
                
                # Calculated metrics
                engagement_rate=engagement_metrics['engagement_rate'],
                completion_rate=self._generate_completion_rate(thread_length, skill_factor),
                click_through_rate=random.uniform(0.5, 4.0),
                
                # Business impact
                profile_visits=int(base_impressions * random.uniform(0.01, 0.05)),
                link_clicks=int(base_impressions * random.uniform(0.005, 0.03)) if random.choice(self.content_sources) else 0,
                follower_growth=self._generate_follower_growth(engagement_metrics['engagement_rate'], base_impressions),
                
                # Performance metadata
                peak_engagement_hour=posted_at.hour if posted_at else None,
                hook_performance=random.uniform(0.8, 2.5),
                drop_off_points=self._generate_drop_off_points(thread_length),
                best_performing_tweet=random.randint(1, min(thread_length, 3))
            )
            
            threads.append(thread)
        
        return sorted(threads, key=lambda x: x.created_at)
    
    def generate_tweet_metrics(self, thread: ThreadAnalytics) -> List[TweetMetrics]:
        """Generate individual tweet metrics for a thread"""
        
        tweets = []
        total_thread_engagement = thread.likes + thread.retweets + thread.replies + thread.bookmarks
        
        for position in range(1, thread.thread_length + 1):
            tweet_id = f"{thread.thread_id}_tweet_{position}"
            
            # First tweet (hook) typically performs better
            if position == 1:
                impression_share = random.uniform(0.3, 0.5)
                engagement_multiplier = random.uniform(1.2, 2.0)
            elif position <= 3:
                impression_share = random.uniform(0.15, 0.25)
                engagement_multiplier = random.uniform(0.8, 1.2)
            else:
                # Later tweets get progressively less engagement
                impression_share = random.uniform(0.05, 0.15) * (1 / position * 2)
                engagement_multiplier = random.uniform(0.5, 0.9) * (1 / position * 3)
            
            tweet_impressions = int(thread.impressions * impression_share)
            
            # Distribute thread engagement across tweets
            base_engagement = int(total_thread_engagement * impression_share * engagement_multiplier)
            
            tweet_likes = int(base_engagement * random.uniform(0.6, 0.8))
            tweet_retweets = int(base_engagement * random.uniform(0.1, 0.2))
            tweet_replies = int(base_engagement * random.uniform(0.05, 0.15))
            tweet_bookmarks = int(base_engagement * random.uniform(0.05, 0.1))
            
            tweet_engagement_rate = (tweet_likes + tweet_retweets + tweet_replies + tweet_bookmarks) / max(tweet_impressions, 1) * 100
            
            # Generate realistic tweet content
            content = self._generate_tweet_content(position, thread.thread_length)
            
            tweet = TweetMetrics(
                tweet_id=tweet_id,
                thread_id=thread.thread_id,
                position=position,
                content=content,
                character_count=len(content),
                has_media=random.random() < 0.3,  # 30% have media
                has_links=random.random() < 0.2,  # 20% have links
                has_hashtags=random.random() < 0.4,  # 40% have hashtags
                
                impressions=tweet_impressions,
                likes=tweet_likes,
                retweets=tweet_retweets,
                replies=tweet_replies,
                bookmarks=tweet_bookmarks,
                engagement_rate=tweet_engagement_rate,
                
                is_hook=(position == 1),
                is_cta=(position == thread.thread_length and random.random() < 0.6)  # 60% of last tweets are CTAs
            )
            
            tweets.append(tweet)
        
        return tweets
    
    def generate_time_series_data(self, thread: ThreadAnalytics, 
                                hours_to_track: int = 72) -> List[AnalyticsSnapshot]:
        """Generate time-series snapshots showing performance over time"""
        
        if not thread.posted_at:
            return []
        
        snapshots = []
        current_metrics = {
            'impressions': 0,
            'likes': 0,
            'retweets': 0,
            'replies': 0,
            'bookmarks': 0
        }
        
        # Generate snapshots for each hour after posting
        for hour in range(hours_to_track):
            snapshot_time = thread.posted_at + timedelta(hours=hour)
            
            # Simulate organic growth curve (fast initial growth, then tapering)
            growth_factor = self._calculate_growth_factor(hour, hours_to_track)
            
            # Update metrics based on growth
            current_metrics['impressions'] = int(thread.impressions * growth_factor)
            current_metrics['likes'] = int(thread.likes * growth_factor)
            current_metrics['retweets'] = int(thread.retweets * growth_factor)
            current_metrics['replies'] = int(thread.replies * growth_factor)
            current_metrics['bookmarks'] = int(thread.bookmarks * growth_factor)
            
            snapshot = AnalyticsSnapshot(
                snapshot_id=f"{thread.thread_id}_snapshot_{hour}",
                thread_id=thread.thread_id,
                timestamp=snapshot_time,
                metrics=current_metrics.copy(),
                data_source="twitter_api",
                hours_since_posted=float(hour),
                day_of_week=snapshot_time.weekday(),
                hour_of_day=snapshot_time.hour
            )
            
            snapshots.append(snapshot)
        
        return snapshots
    
    def generate_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Generate complete dashboard data for testing"""
        
        # Generate threads for the user
        threads = self.generate_user_threads(user_id, num_threads=30, days_back=90)
        
        # Generate tweet metrics for some threads
        all_tweets = []
        for thread in threads[:10]:  # Generate tweet data for first 10 threads
            tweets = self.generate_tweet_metrics(thread)
            all_tweets.extend(tweets)
        
        # Calculate summary metrics
        posted_threads = [t for t in threads if t.posted_at]
        total_impressions = sum(t.impressions for t in posted_threads)
        total_engagement = sum(t.likes + t.retweets + t.replies + t.bookmarks for t in posted_threads)
        avg_engagement_rate = sum(t.engagement_rate for t in posted_threads) / len(posted_threads) if posted_threads else 0
        total_follower_growth = sum(t.follower_growth for t in posted_threads)
        
        # Generate comparison data (previous period)
        prev_period_threads = self.generate_user_threads(
            user_id, num_threads=20, days_back=180
        )[-20:]  # Last 20 from previous period
        
        prev_impressions = sum(t.impressions for t in prev_period_threads if t.posted_at)
        prev_engagement_rate = sum(t.engagement_rate for t in prev_period_threads if t.posted_at) / len([t for t in prev_period_threads if t.posted_at]) if prev_period_threads else 0
        
        # Calculate changes
        impressions_change = ((total_impressions - prev_impressions) / prev_impressions * 100) if prev_impressions > 0 else 0
        engagement_change = ((avg_engagement_rate - prev_engagement_rate) / prev_engagement_rate * 100) if prev_engagement_rate > 0 else 0
        
        # Generate chart data
        chart_data = self._generate_chart_data(threads)
        
        # Generate insights data
        insights = self._generate_mock_insights()
        
        return {
            "summary": {
                "totalImpressions": total_impressions,
                "avgEngagementRate": round(avg_engagement_rate, 2),
                "totalThreads": len(posted_threads),
                "followerGrowth": total_follower_growth,
                "impressionsChange": round(impressions_change, 1),
                "engagementChange": round(engagement_change, 1),
                "threadsChange": len(posted_threads) - len([t for t in prev_period_threads if t.posted_at]),
                "followerChange": total_follower_growth - sum(t.follower_growth for t in prev_period_threads if t.posted_at)
            },
            "threads": [self._thread_to_dict(t) for t in threads if t.posted_at],
            "charts": chart_data,
            "insights": insights
        }
    
    # Helper Methods
    
    def _generate_skill_progression(self, num_threads: int) -> List[float]:
        """Generate realistic skill progression over time"""
        skill_levels = []
        base_skill = random.uniform(0.3, 0.6)  # Starting skill level
        
        for i in range(num_threads):
            # Gradual improvement with some randomness
            progress = i / num_threads
            skill_improvement = progress * random.uniform(0.2, 0.5)
            daily_variance = random.uniform(-0.1, 0.1)
            
            current_skill = min(1.0, base_skill + skill_improvement + daily_variance)
            skill_levels.append(current_skill)
        
        return skill_levels
    
    def _generate_thread_length(self) -> int:
        """Generate realistic thread lengths"""
        # Most threads are 3-8 tweets, some longer
        weights = [5, 15, 25, 25, 15, 10, 3, 2]  # Weights for lengths 1-8+
        length = random.choices(range(1, 9), weights=weights)[0]
        
        if length == 8:  # Sometimes make it longer
            length = random.randint(8, 20)
        
        return length
    
    def _generate_impressions(self, skill_factor: float, thread_length: int, 
                            posted_at: datetime = None) -> int:
        """Generate realistic impression counts"""
        
        base_impressions = random.randint(500, 2000)
        
        # Skill factor influence
        skill_multiplier = 0.5 + (skill_factor * 2)
        
        # Thread length influence (longer threads sometimes get more impressions)
        length_multiplier = 1 + (thread_length - 5) * 0.05
        
        # Time of day influence
        time_multiplier = 1.0
        if posted_at:
            hour = posted_at.hour
            if 9 <= hour <= 11 or 14 <= hour <= 16 or 19 <= hour <= 21:  # Peak hours
                time_multiplier = random.uniform(1.2, 1.8)
            elif 0 <= hour <= 6:  # Low activity hours
                time_multiplier = random.uniform(0.3, 0.7)
        
        final_impressions = int(base_impressions * skill_multiplier * length_multiplier * time_multiplier)
        
        # Add some high-performing outliers
        if random.random() < 0.05:  # 5% chance of viral content
            final_impressions *= random.randint(5, 20)
        
        return max(100, final_impressions)
    
    def _generate_engagement_metrics(self, impressions: int, skill_factor: float, 
                                   thread_length: int) -> Dict[str, Any]:
        """Generate realistic engagement metrics"""
        
        # Base engagement rate influenced by skill
        base_rate = 1.0 + (skill_factor * 4)  # 1-5% base rate
        rate_variance = random.uniform(0.7, 1.3)
        engagement_rate = base_rate * rate_variance
        
        # Thread length can affect engagement (sweet spot around 5-8 tweets)
        if 5 <= thread_length <= 8:
            engagement_rate *= random.uniform(1.1, 1.3)
        elif thread_length > 12:
            engagement_rate *= random.uniform(0.8, 0.9)
        
        total_engagement = int(impressions * (engagement_rate / 100))
        
        # Distribute engagement across types (realistic ratios)
        likes = int(total_engagement * random.uniform(0.65, 0.75))
        retweets = int(total_engagement * random.uniform(0.15, 0.25))
        replies = int(total_engagement * random.uniform(0.05, 0.15))
        bookmarks = int(total_engagement * random.uniform(0.05, 0.12))
        quotes = int(total_engagement * random.uniform(0.02, 0.08))
        
        # Ensure totals are consistent
        actual_total = likes + retweets + replies + bookmarks + quotes
        if actual_total > 0:
            actual_rate = (actual_total / impressions) * 100
        else:
            actual_rate = 0
        
        return {
            'likes': likes,
            'retweets': retweets,
            'replies': replies,
            'bookmarks': bookmarks,
            'quotes': quotes,
            'engagement_rate': round(actual_rate, 2)
        }
    
    def _generate_completion_rate(self, thread_length: int, skill_factor: float) -> float:
        """Generate realistic completion rates"""
        
        # Base completion rate decreases with length
        if thread_length <= 3:
            base_rate = random.uniform(80, 95)
        elif thread_length <= 7:
            base_rate = random.uniform(60, 80)
        elif thread_length <= 12:
            base_rate = random.uniform(40, 65)
        else:
            base_rate = random.uniform(25, 45)
        
        # Skill factor helps retention
        skill_bonus = skill_factor * 15
        
        final_rate = min(95, base_rate + skill_bonus + random.uniform(-5, 5))
        
        return round(max(10, final_rate), 1)
    
    def _generate_follower_growth(self, engagement_rate: float, impressions: int) -> int:
        """Generate realistic follower growth"""
        
        # Higher engagement and impressions lead to more followers
        base_growth = (engagement_rate / 100) * (impressions / 1000) * random.uniform(0.1, 0.3)
        
        # Add some randomness
        variance = random.uniform(0.5, 1.5)
        growth = int(base_growth * variance)
        
        # Occasionally negative growth (unfollows)
        if random.random() < 0.1:
            growth = -random.randint(0, 3)
        
        return growth
    
    def _generate_drop_off_points(self, thread_length: int) -> List[int]:
        """Generate realistic drop-off points in threads"""
        
        drop_offs = []
        
        # Common drop-off points
        if thread_length > 3:
            if random.random() < 0.4:  # 40% chance of drop-off after tweet 3
                drop_offs.append(3)
        
        if thread_length > 7:
            if random.random() < 0.6:  # 60% chance of drop-off after tweet 7
                drop_offs.append(7)
        
        if thread_length > 12:
            if random.random() < 0.8:  # 80% chance of drop-off after tweet 12
                drop_offs.append(12)
        
        return drop_offs
    
    def _generate_tweet_content(self, position: int, thread_length: int) -> str:
        """Generate realistic tweet content"""
        
        if position == 1:  # Hook
            hooks = [
                "Here's what I learned from building my first startup 👇",
                "Most people get this wrong. Here's the right way:",
                "I made a $50k mistake so you don't have to. Thread:",
                "The secret that changed everything for me:",
                "Why everyone is talking about this (and why you should care):"
            ]
            return random.choice(hooks)
        
        elif position == thread_length:  # Conclusion/CTA
            conclusions = [
                "That's a wrap! What questions do you have about this?",
                "Hope this helps! Retweet the first tweet if you found this valuable 🙏",
                "What's your experience with this? Let me know in the replies!",
                "Follow me @username for more content like this 📈",
                "Thanks for reading! What topic should I cover next?"
            ]
            return random.choice(conclusions)
        
        else:  # Middle content
            content_types = [
                f"{position}. {fake.sentence()} This is why it matters: {fake.sentence()}",
                f"Key insight #{position}: {fake.sentence()}",
                f"Here's the thing most people miss: {fake.sentence()}",
                f"Step {position}: {fake.sentence()} Here's how to do it:",
                f"The data shows {fake.sentence()} This means:"
            ]
            return random.choice(content_types)
    
    def _calculate_growth_factor(self, hour: int, total_hours: int) -> float:
        """Calculate organic growth factor over time"""
        
        # Typical viral content curve: fast growth, then plateau
        if hour <= 6:  # First 6 hours - rapid growth
            return (hour / 6) * 0.7
        elif hour <= 24:  # Next 18 hours - continued growth
            return 0.7 + ((hour - 6) / 18) * 0.25
        else:  # After 24 hours - slow growth to final values
            return 0.95 + ((hour - 24) / (total_hours - 24)) * 0.05
    
    def _generate_chart_data(self, threads: List[ThreadAnalytics]) -> Dict[str, Any]:
        """Generate chart data for dashboard"""
        
        # Last 30 days of data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # Daily aggregations
        daily_data = {}
        for i in range(30):
            date = start_date + timedelta(days=i)
            daily_data[date.strftime('%Y-%m-%d')] = {
                'engagement_rate': 0,
                'impressions': 0,
                'likes': 0,
                'retweets': 0,
                'count': 0
            }
        
        # Aggregate thread data by day
        for thread in threads:
            if thread.posted_at and start_date <= thread.posted_at <= end_date:
                date_key = thread.posted_at.strftime('%Y-%m-%d')
                if date_key in daily_data:
                    daily_data[date_key]['engagement_rate'] += thread.engagement_rate
                    daily_data[date_key]['impressions'] += thread.impressions
                    daily_data[date_key]['likes'] += thread.likes
                    daily_data[date_key]['retweets'] += thread.retweets
                    daily_data[date_key]['count'] += 1
        
        # Calculate averages
        dates = []
        engagement_rates = []
        impressions = []
        likes = []
        retweets = []
        
        for date_key in sorted(daily_data.keys()):
            data = daily_data[date_key]
            dates.append(date_key)
            
            if data['count'] > 0:
                engagement_rates.append(round(data['engagement_rate'] / data['count'], 1))
                impressions.append(data['impressions'])
                likes.append(data['likes'])
                retweets.append(data['retweets'])
            else:
                engagement_rates.append(0)
                impressions.append(0)
                likes.append(0)
                retweets.append(0)
        
        # Performance distribution
        if threads:
            high_performers = sum(1 for t in threads if t.engagement_rate >= 5)
            medium_performers = sum(1 for t in threads if 2 <= t.engagement_rate < 5)
            low_performers = sum(1 for t in threads if t.engagement_rate < 2)
        else:
            high_performers = medium_performers = low_performers = 0
        
        return {
            'dates': dates,
            'engagement_rate': engagement_rates,
            'impressions': impressions,
            'likes': likes,
            'retweets': retweets,
            'performance_distribution': [high_performers, medium_performers, low_performers]
        }
    
    def _generate_mock_insights(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate mock insights for dashboard"""
        
        performance_insights = [
            {
                "id": "insight_1",
                "message": "Your threads posted on Tuesday perform 23% better than average",
                "impact": "Optimal timing can increase reach by up to 2,500 impressions"
            },
            {
                "id": "insight_2", 
                "message": "Threads with 5-7 tweets have the highest completion rate (78%)",
                "impact": "Thread length optimization could improve engagement by 15%"
            }
        ]
        
        optimization_tips = [
            {
                "id": "tip_1",
                "message": "Add more questions to your threads to boost reply rates",
                "priority": "High"
            },
            {
                "id": "tip_2",
                "message": "Your hooks perform best when they include numbers or statistics",
                "priority": "Medium"
            }
        ]
        
        return {
            "performance": performance_insights,
            "optimization": optimization_tips
        }
    
    def _thread_to_dict(self, thread: ThreadAnalytics) -> Dict[str, Any]:
        """Convert ThreadAnalytics to dictionary for JSON serialization"""
        
        return {
            "thread_id": thread.thread_id,
            "title": thread.title,
            "posted_at": thread.posted_at.isoformat() if thread.posted_at else None,
            "thread_length": thread.thread_length,
            "content_source": thread.content_source,
            "impressions": thread.impressions,
            "likes": thread.likes,
            "retweets": thread.retweets,
            "replies": thread.replies,
            "engagement_rate": thread.engagement_rate,
            "follower_growth": thread.follower_growth
        }


# Usage example and test data generation
if __name__ == "__main__":
    generator = MockAnalyticsGenerator()
    
    # Generate data for a test user
    user_id = "test_user_123"
    dashboard_data = generator.generate_dashboard_data(user_id)
    
    print("Generated dashboard data:")
    print(f"Total threads: {dashboard_data['summary']['totalThreads']}")
    print(f"Total impressions: {dashboard_data['summary']['totalImpressions']:,}")
    print(f"Avg engagement rate: {dashboard_data['summary']['avgEngagementRate']}%")
    print(f"Follower growth: {dashboard_data['summary']['followerGrowth']}")