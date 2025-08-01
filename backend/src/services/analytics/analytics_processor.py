"""
Analytics processing architecture for Threadr.
Handles both real-time streaming and batch processing of thread metrics.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

from ..models.analytics import ThreadAnalytics, TweetMetrics, AnalyticsSnapshot


class ProcessingMode(str, Enum):
    """Processing modes for analytics data"""
    REAL_TIME = "real_time"
    BATCH = "batch"
    HYBRID = "hybrid"


class DataSource(str, Enum):
    """Sources of analytics data"""
    TWITTER_API = "twitter_api"
    WEBHOOK = "webhook"
    MANUAL_IMPORT = "manual_import"
    SCHEDULED_SYNC = "scheduled_sync"


@dataclass
class ProcessingJob:
    """Represents a data processing job"""
    job_id: str
    source: DataSource
    mode: ProcessingMode
    data_type: str  # "thread", "tweet", "snapshot"
    payload: Dict[str, Any]
    priority: int = 5  # 1=highest, 10=lowest
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class AnalyticsProcessor:
    """
    Central processor for all analytics data.
    Handles real-time streams, batch jobs, and hybrid processing.
    """
    
    def __init__(self, redis_client=None, database_client=None):
        self.redis_client = redis_client
        self.database_client = database_client
        self.logger = logging.getLogger(__name__)
        
        # Processing queues
        self.real_time_queue = asyncio.Queue(maxsize=1000)
        self.batch_queue = asyncio.Queue(maxsize=10000)
        
        # Processing stats
        self.stats = {
            "real_time_processed": 0,
            "batch_processed": 0,
            "errors": 0,
            "last_batch_run": None,
            "processing_rate": 0.0  # items per second
        }
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Processing workers
        self.real_time_workers = []
        self.batch_workers = []
        self.is_running = False
    
    async def start(self):
        """Start the analytics processor"""
        if self.is_running:
            return
        
        self.is_running = True
        self.logger.info("Starting analytics processor...")
        
        # Start real-time workers (multiple for high throughput)
        for i in range(3):  # 3 real-time workers
            worker = asyncio.create_task(self._real_time_worker(f"rt_worker_{i}"))
            self.real_time_workers.append(worker)
        
        # Start batch worker
        batch_worker = asyncio.create_task(self._batch_worker())
        self.batch_workers.append(batch_worker)
        
        # Start periodic tasks
        asyncio.create_task(self._stats_reporter())
        asyncio.create_task(self._scheduled_batch_sync())
        
        self.logger.info("Analytics processor started successfully")
    
    async def stop(self):
        """Stop the analytics processor"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.logger.info("Stopping analytics processor...")
        
        # Cancel all workers
        for worker in self.real_time_workers + self.batch_workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.real_time_workers, *self.batch_workers, return_exceptions=True)
        
        self.logger.info("Analytics processor stopped")
    
    # Real-time Processing
    
    async def process_real_time_event(self, event_type: str, data: Dict[str, Any], 
                                    source: DataSource = DataSource.WEBHOOK):
        """Process a real-time analytics event"""
        
        job = ProcessingJob(
            job_id=f"rt_{datetime.utcnow().timestamp()}_{event_type}",
            source=source,
            mode=ProcessingMode.REAL_TIME,
            data_type=event_type,
            payload=data,
            priority=1  # High priority for real-time
        )
        
        try:
            await self.real_time_queue.put(job)
            self.logger.debug(f"Queued real-time job: {job.job_id}")
        except asyncio.QueueFull:
            self.logger.error("Real-time queue full, dropping event")
            self.stats["errors"] += 1
    
    async def _real_time_worker(self, worker_id: str):
        """Worker that processes real-time events"""
        
        self.logger.info(f"Started real-time worker: {worker_id}")
        
        while self.is_running:
            try:
                # Get job from queue with timeout
                job = await asyncio.wait_for(self.real_time_queue.get(), timeout=1.0)
                
                await self._process_job(job)
                self.stats["real_time_processed"] += 1
                
                # Mark task as done
                self.real_time_queue.task_done()
                
            except asyncio.TimeoutError:
                # No jobs available, continue
                continue
            except Exception as e:
                self.logger.error(f"Real-time worker {worker_id} error: {e}")
                self.stats["errors"] += 1
    
    # Batch Processing
    
    async def schedule_batch_job(self, job_type: str, data: Dict[str, Any], 
                               source: DataSource = DataSource.SCHEDULED_SYNC,
                               priority: int = 5):
        """Schedule a batch processing job"""
        
        job = ProcessingJob(
            job_id=f"batch_{datetime.utcnow().timestamp()}_{job_type}",
            source=source,
            mode=ProcessingMode.BATCH,
            data_type=job_type,
            payload=data,
            priority=priority
        )
        
        await self.batch_queue.put(job)
        self.logger.debug(f"Scheduled batch job: {job.job_id}")
    
    async def _batch_worker(self):
        """Worker that processes batch jobs"""
        
        self.logger.info("Started batch worker")
        
        while self.is_running:
            try:
                # Process jobs in batches for efficiency
                jobs = []
                
                # Collect up to 50 jobs or wait 5 seconds
                timeout = 5.0
                for _ in range(50):
                    try:
                        job = await asyncio.wait_for(self.batch_queue.get(), timeout=timeout)
                        jobs.append(job)
                        timeout = 0.1  # Shorter timeout for subsequent jobs
                    except asyncio.TimeoutError:
                        break
                
                if jobs:
                    await self._process_job_batch(jobs)
                    self.stats["batch_processed"] += len(jobs)
                    
                    # Mark all tasks as done
                    for _ in jobs:
                        self.batch_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Batch worker error: {e}")
                self.stats["errors"] += 1
    
    async def _process_job_batch(self, jobs: List[ProcessingJob]):
        """Process a batch of jobs efficiently"""
        
        self.logger.info(f"Processing batch of {len(jobs)} jobs")
        
        # Group jobs by type for batch processing
        jobs_by_type = defaultdict(list)
        for job in jobs:
            jobs_by_type[job.data_type].append(job)
        
        # Process each type as a batch
        for data_type, type_jobs in jobs_by_type.items():
            try:
                if data_type == "thread_sync":
                    await self._batch_sync_threads(type_jobs)
                elif data_type == "metrics_aggregation":
                    await self._batch_aggregate_metrics(type_jobs)
                elif data_type == "insights_generation":
                    await self._batch_generate_insights(type_jobs)
                else:
                    # Process individually
                    for job in type_jobs:
                        await self._process_job(job)
                        
            except Exception as e:
                self.logger.error(f"Batch processing error for {data_type}: {e}")
                for job in type_jobs:
                    job.error = str(e)
    
    # Job Processing
    
    async def _process_job(self, job: ProcessingJob):
        """Process an individual job"""
        
        job.started_at = datetime.utcnow()
        
        try:
            if job.data_type == "thread_update":
                await self._process_thread_update(job)
            elif job.data_type == "tweet_metrics":
                await self._process_tweet_metrics(job)
            elif job.data_type == "engagement_event":
                await self._process_engagement_event(job)
            elif job.data_type == "follower_change":
                await self._process_follower_change(job)
            else:
                self.logger.warning(f"Unknown job type: {job.data_type}")
            
            job.completed_at = datetime.utcnow()
            
            # Trigger event handlers
            await self._trigger_event_handlers(job.data_type, job.payload)
            
        except Exception as e:
            job.error = str(e)
            self.logger.error(f"Job processing error {job.job_id}: {e}")
            raise
    
    async def _process_thread_update(self, job: ProcessingJob):
        """Process thread analytics update"""
        
        data = job.payload
        thread_id = data.get("thread_id")
        
        if not thread_id:
            raise ValueError("Missing thread_id in payload")
        
        # Update thread analytics in database
        if self.database_client:
            await self._update_thread_analytics(thread_id, data)
        
        # Update real-time cache
        if self.redis_client:
            cache_key = f"thread_analytics:{thread_id}"
            await self.redis_client.hset(cache_key, mapping=data)
            await self.redis_client.expire(cache_key, 3600)  # 1 hour TTL
        
        # Create time-series snapshot
        await self._create_analytics_snapshot(thread_id, data, job.source)
        
        self.logger.debug(f"Updated thread analytics: {thread_id}")
    
    async def _process_tweet_metrics(self, job: ProcessingJob):
        """Process individual tweet metrics"""
        
        data = job.payload
        tweet_id = data.get("tweet_id")
        thread_id = data.get("thread_id")
        
        if not tweet_id or not thread_id:
            raise ValueError("Missing tweet_id or thread_id in payload")
        
        # Update tweet metrics
        if self.database_client:
            await self._update_tweet_metrics(tweet_id, data)
        
        # Update aggregated thread metrics
        await self._update_thread_aggregates(thread_id)
        
        self.logger.debug(f"Updated tweet metrics: {tweet_id}")
    
    async def _process_engagement_event(self, job: ProcessingJob):
        """Process real-time engagement events (likes, retweets, etc.)"""
        
        data = job.payload
        event_type = data.get("event_type")  # "like", "retweet", "reply", etc.
        tweet_id = data.get("tweet_id")
        thread_id = data.get("thread_id")
        
        if not all([event_type, tweet_id, thread_id]):
            raise ValueError("Missing required fields in engagement event")
        
        # Update counters in real-time cache
        if self.redis_client:
            tweet_key = f"tweet_metrics:{tweet_id}"
            thread_key = f"thread_analytics:{thread_id}"
            
            # Increment counters
            if event_type == "like":
                await self.redis_client.hincrby(tweet_key, "likes", 1)
                await self.redis_client.hincrby(thread_key, "likes", 1)
            elif event_type == "retweet":
                await self.redis_client.hincrby(tweet_key, "retweets", 1)
                await self.redis_client.hincrby(thread_key, "retweets", 1)
            elif event_type == "reply":
                await self.redis_client.hincrby(tweet_key, "replies", 1)
                await self.redis_client.hincrby(thread_key, "replies", 1)
        
        # Schedule batch update for database persistence
        await self.schedule_batch_job("metrics_sync", {
            "tweet_id": tweet_id,
            "thread_id": thread_id,
            "event_type": event_type
        }, priority=3)
        
        self.logger.debug(f"Processed engagement event: {event_type} on {tweet_id}")
    
    async def _process_follower_change(self, job: ProcessingJob):
        """Process follower growth/loss events"""
        
        data = job.payload
        user_id = data.get("user_id")
        change = data.get("change")  # +1 or -1
        attributed_thread_id = data.get("thread_id")  # Optional attribution
        
        if not user_id or change is None:
            raise ValueError("Missing user_id or change in follower event")
        
        # Update user follower count
        if self.redis_client:
            user_key = f"user_stats:{user_id}"
            await self.redis_client.hincrby(user_key, "followers", change)
        
        # Attribute to specific thread if provided
        if attributed_thread_id and self.redis_client:
            thread_key = f"thread_analytics:{attributed_thread_id}"
            await self.redis_client.hincrby(thread_key, "follower_growth", change)
        
        self.logger.debug(f"Processed follower change: {change} for user {user_id}")
    
    # Batch Processing Methods
    
    async def _batch_sync_threads(self, jobs: List[ProcessingJob]):
        """Sync multiple threads with Twitter API"""
        
        thread_ids = [job.payload.get("thread_id") for job in jobs]
        self.logger.info(f"Batch syncing {len(thread_ids)} threads")
        
        # In production, this would make batch API calls to Twitter
        # For now, simulate the process
        for job in jobs:
            await asyncio.sleep(0.01)  # Simulate API call
            job.completed_at = datetime.utcnow()
    
    async def _batch_aggregate_metrics(self, jobs: List[ProcessingJob]):
        """Aggregate metrics for multiple entities"""
        
        self.logger.info(f"Batch aggregating metrics for {len(jobs)} entities")
        
        # Group by aggregation type
        for job in jobs:
            aggregation_type = job.payload.get("type")
            
            if aggregation_type == "daily":
                await self._aggregate_daily_metrics(job.payload)
            elif aggregation_type == "weekly":
                await self._aggregate_weekly_metrics(job.payload)
            elif aggregation_type == "user_summary":
                await self._aggregate_user_summary(job.payload)
            
            job.completed_at = datetime.utcnow()
    
    async def _batch_generate_insights(self, jobs: List[ProcessingJob]):
        """Generate insights for multiple users"""
        
        self.logger.info(f"Batch generating insights for {len(jobs)} users")
        
        for job in jobs:
            user_id = job.payload.get("user_id")
            if user_id:
                # Generate insights (this would use the InsightsEngine)
                await self._generate_user_insights(user_id)
            
            job.completed_at = datetime.utcnow()
    
    # Helper Methods
    
    async def _update_thread_analytics(self, thread_id: str, data: Dict[str, Any]):
        """Update thread analytics in database"""
        # In production, this would update the database
        pass
    
    async def _update_tweet_metrics(self, tweet_id: str, data: Dict[str, Any]):
        """Update tweet metrics in database"""
        # In production, this would update the database
        pass
    
    async def _update_thread_aggregates(self, thread_id: str):
        """Update aggregated thread metrics from individual tweets"""
        # In production, this would recalculate thread totals
        pass
    
    async def _create_analytics_snapshot(self, thread_id: str, data: Dict[str, Any], 
                                       source: DataSource):
        """Create a time-series snapshot"""
        
        snapshot = AnalyticsSnapshot(
            snapshot_id=f"{thread_id}_{datetime.utcnow().timestamp()}",
            thread_id=thread_id,
            timestamp=datetime.utcnow(),
            metrics=data,
            data_source=source.value,
            day_of_week=datetime.utcnow().weekday(),
            hour_of_day=datetime.utcnow().hour
        )
        
        # Store snapshot (in production, this would go to time-series database)
        if self.redis_client:
            key = f"snapshots:{thread_id}"
            await self.redis_client.lpush(key, json.dumps(asdict(snapshot), default=str))
            await self.redis_client.ltrim(key, 0, 1000)  # Keep last 1000 snapshots
    
    async def _aggregate_daily_metrics(self, payload: Dict[str, Any]):
        """Aggregate daily metrics"""
        # Implementation for daily aggregation
        pass
    
    async def _aggregate_weekly_metrics(self, payload: Dict[str, Any]):
        """Aggregate weekly metrics"""
        # Implementation for weekly aggregation
        pass
    
    async def _aggregate_user_summary(self, payload: Dict[str, Any]):
        """Aggregate user summary metrics"""
        # Implementation for user summary aggregation
        pass
    
    async def _generate_user_insights(self, user_id: str):
        """Generate insights for a user"""
        # This would use the InsightsEngine
        pass
    
    # Event System
    
    def add_event_handler(self, event_type: str, handler: Callable):
        """Add an event handler for specific event types"""
        self.event_handlers[event_type].append(handler)
    
    async def _trigger_event_handlers(self, event_type: str, payload: Dict[str, Any]):
        """Trigger event handlers for processed events"""
        handlers = self.event_handlers.get(event_type, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    handler(payload)
            except Exception as e:
                self.logger.error(f"Event handler error for {event_type}: {e}")
    
    # Scheduled Tasks
    
    async def _scheduled_batch_sync(self):
        """Periodic batch sync with external APIs"""
        
        while self.is_running:
            try:
                # Run every 15 minutes
                await asyncio.sleep(900)
                
                # Schedule batch sync jobs
                await self.schedule_batch_job("thread_sync", {
                    "sync_type": "periodic",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                await self.schedule_batch_job("metrics_aggregation", {
                    "type": "daily",
                    "date": datetime.utcnow().date().isoformat()
                })
                
                self.stats["last_batch_run"] = datetime.utcnow()
                
            except Exception as e:
                self.logger.error(f"Scheduled batch sync error: {e}")
    
    async def _stats_reporter(self):
        """Report processing statistics"""
        
        last_processed = 0
        
        while self.is_running:
            await asyncio.sleep(60)  # Report every minute
            
            current_processed = self.stats["real_time_processed"] + self.stats["batch_processed"]
            rate = (current_processed - last_processed) / 60.0  # per second
            
            self.stats["processing_rate"] = rate
            last_processed = current_processed
            
            self.logger.info(
                f"Analytics processor stats - "
                f"RT: {self.stats['real_time_processed']}, "
                f"Batch: {self.stats['batch_processed']}, "
                f"Errors: {self.stats['errors']}, "
                f"Rate: {rate:.2f}/sec"
            )
    
    # Public API
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        return {
            **self.stats,
            "real_time_queue_size": self.real_time_queue.qsize(),
            "batch_queue_size": self.batch_queue.qsize(),
            "is_running": self.is_running,
            "workers": {
                "real_time": len(self.real_time_workers),
                "batch": len(self.batch_workers)
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the processor"""
        
        is_healthy = (
            self.is_running and 
            len(self.real_time_workers) > 0 and 
            len(self.batch_workers) > 0 and
            self.stats["errors"] < 100  # Error threshold
        )
        
        return {
            "healthy": is_healthy,
            "status": "running" if self.is_running else "stopped",
            "uptime": datetime.utcnow(),  # In production, track actual uptime
            "error_rate": self.stats["errors"] / max(1, self.stats["real_time_processed"] + self.stats["batch_processed"]),
            "queue_health": {
                "real_time_full": self.real_time_queue.full(),
                "batch_full": self.batch_queue.full()
            }
        }


# Processing Architecture Documentation
PROCESSING_ARCHITECTURE_DOC = """
# Threadr Analytics Processing Architecture

## Overview
The analytics processing system handles both real-time streaming data and batch processing
for optimal performance and data consistency.

## Processing Modes

### Real-time Processing
- **Use Cases**: 
  * Live engagement events (likes, retweets, replies)
  * Immediate metric updates
  * Real-time dashboard updates
  * User notifications

- **Characteristics**:
  * Low latency (< 100ms)
  * High throughput (1000+ events/sec)
  * Eventually consistent
  * Memory-based caching (Redis)

### Batch Processing
- **Use Cases**:
  * Daily/weekly aggregations
  * Historical data backfills
  * Complex analytics computations
  * Report generation
  * Data warehouse updates

- **Characteristics**:
  * High throughput (10,000+ records/batch)
  * Resource efficient
  * Strongly consistent
  * Database persistence

### Hybrid Processing
- **Approach**: Real-time events update cache, batch jobs ensure persistence
- **Benefits**: Speed + reliability
- **Consistency**: Eventually consistent with periodic reconciliation

## Data Flow

1. **Ingestion**:
   * Webhooks from Twitter API
   * Scheduled API polling
   * Manual data imports
   * User-triggered updates

2. **Processing**:
   * Real-time queue (in-memory)
   * Batch queue (persistent)
   * Multiple worker processes
   * Error handling and retries

3. **Storage**:
   * Redis (real-time cache)
   * PostgreSQL (persistent storage)
   * Time-series database (optional)

4. **Output**:
   * API responses
   * Dashboard updates
   * Notifications
   * Reports

## Scaling Considerations

### Horizontal Scaling
- Multiple processor instances
- Queue-based distribution
- Load balancing
- Service discovery

### Vertical Scaling
- Configurable worker counts
- Memory/CPU optimization
- Connection pooling
- Caching strategies

## Monitoring & Observability

### Metrics
- Processing rates
- Queue sizes
- Error rates
- Latency percentiles

### Alerts
- Queue overflow
- Processing failures
- API rate limits
- Performance degradation

### Health Checks
- Worker status
- Database connectivity
- External API availability
- Resource utilization

## Deployment Architecture

### Production Setup
```
Load Balancer
    ↓
API Gateway
    ↓
Analytics Processor (Multiple Instances)
    ↓
Redis Cluster (Cache) + PostgreSQL (Persistence)
```

### Development Setup
```
Single Processor Instance
    ↓
Local Redis + Local PostgreSQL
```

## Configuration Examples

### High Volume (>10k threads/day)
- Real-time workers: 5-10
- Batch workers: 2-3
- Queue sizes: 5000+ each
- Redis cluster: 3+ nodes
- Database: Read replicas

### Medium Volume (1k-10k threads/day)
- Real-time workers: 3-5
- Batch workers: 1-2
- Queue sizes: 1000+ each
- Redis: Single instance
- Database: Single instance

### Low Volume (<1k threads/day)
- Real-time workers: 1-2
- Batch workers: 1
- Queue sizes: 100-500 each
- Redis: Single instance
- Database: Single instance
"""