"""
Thread History Service for Threadr
Handles thread storage, retrieval, and management using Redis
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
import logging
import json
import uuid
import os
try:
    from ...models.thread import (
        SavedThread, ThreadTweet, ThreadMetadata, ThreadHistoryFilter,
        ThreadHistoryResponse, ThreadNotFoundError, ThreadAccessDeniedError,
        ThreadStorageError
    )
except ImportError:
    from src.models.thread import (
        SavedThread, ThreadTweet, ThreadMetadata, ThreadHistoryFilter,
        ThreadHistoryResponse, ThreadNotFoundError, ThreadAccessDeniedError,
        ThreadStorageError
    )

logger = logging.getLogger(__name__)


class ThreadHistoryService:
    """Service for managing thread history in Redis"""
    
    def __init__(self, redis_manager):
        """Initialize thread service with Redis manager"""
        self.redis_manager = redis_manager
        self.thread_prefix = "threadr:thread:"
        self.user_threads_prefix = "threadr:user_threads:"
        self.thread_index_prefix = "threadr:thread_index:"
        self.thread_stats_key = "threadr:thread_stats"
        
        # Configuration
        self.max_threads_per_user = int(os.getenv("MAX_THREADS_PER_USER", "1000"))
        self.thread_ttl_days = int(os.getenv("THREAD_TTL_DAYS", "365"))  # 1 year default
        self.default_page_size = 10
        self.max_page_size = 50
    
    async def save_thread(self, user_id: str, title: str, original_content: str, 
                         tweets: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None,
                         client_ip: str = "") -> SavedThread:
        """Save a new thread for a user"""
        try:
            # Validate input
            if not user_id or not title or not tweets:
                raise ThreadStorageError("Missing required fields")
            
            if len(tweets) == 0:
                raise ThreadStorageError("Thread must have at least one tweet")
            
            # Check user's thread count limit
            user_thread_count = await self.get_user_thread_count(user_id)
            if user_thread_count >= self.max_threads_per_user:
                raise ThreadStorageError(f"Maximum thread limit ({self.max_threads_per_user}) reached")
            
            # Create thread tweets
            thread_tweets = []
            for i, tweet_data in enumerate(tweets):
                if isinstance(tweet_data, dict):
                    tweet = ThreadTweet(
                        content=tweet_data.get('content', ''),
                        order=i + 1,
                        character_count=len(tweet_data.get('content', ''))
                    )
                else:
                    # Handle string tweets
                    tweet = ThreadTweet(
                        content=str(tweet_data),
                        order=i + 1,
                        character_count=len(str(tweet_data))
                    )
                thread_tweets.append(tweet)
            
            # Create metadata
            thread_metadata = ThreadMetadata()
            if metadata:
                thread_metadata = ThreadMetadata(**metadata)
            
            # Create saved thread
            thread_id = str(uuid.uuid4())
            saved_thread = SavedThread(
                id=thread_id,
                user_id=user_id,
                title=title,
                original_content=original_content,
                tweets=thread_tweets,
                metadata=thread_metadata
            )
            
            # Store in Redis
            success = await self._store_thread(saved_thread)
            if not success:
                raise ThreadStorageError("Failed to store thread")
            
            # Update user's thread list
            await self._add_thread_to_user_list(user_id, thread_id)
            
            # Update stats
            await self._update_thread_stats(user_id, "created")
            
            logger.info(f"Thread saved successfully: {thread_id} for user {user_id}")
            return saved_thread
            
        except ThreadStorageError:
            raise
        except Exception as e:
            logger.error(f"Error saving thread: {e}")
            raise ThreadStorageError("Failed to save thread")
    
    async def get_thread_by_id(self, thread_id: str, user_id: str, 
                              increment_view: bool = True) -> Optional[SavedThread]:
        """Get a specific thread by ID"""
        try:
            thread = await self._get_thread_from_redis(thread_id)
            if not thread:
                return None
            
            # Check access permissions
            if thread.user_id != user_id:
                raise ThreadAccessDeniedError("Access denied to this thread")
            
            # Increment view count if requested
            if increment_view:
                thread.view_count += 1
                await self._store_thread(thread)
                await self._update_thread_stats(user_id, "viewed")
            
            return thread
            
        except ThreadAccessDeniedError:
            raise
        except Exception as e:
            logger.error(f"Error getting thread {thread_id}: {e}")
            return None
    
    async def get_user_threads(self, user_id: str, page: int = 1, page_size: int = 10,
                             filters: Optional[ThreadHistoryFilter] = None,
                             sort_by: str = "created_at", sort_order: str = "desc") -> ThreadHistoryResponse:
        """Get paginated thread history for a user"""
        try:
            # Validate pagination parameters
            page = max(1, page)
            page_size = min(max(1, page_size), self.max_page_size)
            
            # Get user's thread IDs
            thread_ids = await self._get_user_thread_ids(user_id)
            if not thread_ids:
                return ThreadHistoryResponse(
                    threads=[],
                    total_count=0,
                    page=page,
                    page_size=page_size,
                    has_next=False,
                    has_previous=False
                )
            
            # Load threads
            threads = []
            for thread_id in thread_ids:
                thread = await self._get_thread_from_redis(thread_id)
                if thread and thread.user_id == user_id:
                    threads.append(thread)
            
            # Apply filters
            if filters:
                threads = self._apply_filters(threads, filters)
            
            # Sort threads
            threads = self._sort_threads(threads, sort_by, sort_order)
            
            # Apply pagination
            total_count = len(threads)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_threads = threads[start_idx:end_idx]
            
            # Convert to dictionaries
            thread_dicts = [thread.to_dict() for thread in paginated_threads]
            
            return ThreadHistoryResponse(
                threads=thread_dicts,
                total_count=total_count,
                page=page,
                page_size=page_size,
                has_next=end_idx < total_count,
                has_previous=page > 1
            )
            
        except Exception as e:
            logger.error(f"Error getting user threads for {user_id}: {e}")
            return ThreadHistoryResponse(
                threads=[],
                total_count=0,
                page=page,
                page_size=page_size,
                has_next=False,
                has_previous=False
            )
    
    async def update_thread(self, thread_id: str, user_id: str, 
                          updates: Dict[str, Any]) -> Optional[SavedThread]:
        """Update an existing thread"""
        try:
            # Get existing thread
            thread = await self._get_thread_from_redis(thread_id)
            if not thread:
                raise ThreadNotFoundError("Thread not found")
            
            # Check permissions
            if thread.user_id != user_id:
                raise ThreadAccessDeniedError("Access denied to this thread")
            
            # Apply updates
            if "title" in updates:
                thread.title = updates["title"]
            if "is_favorite" in updates:
                thread.is_favorite = updates["is_favorite"]
            if "is_archived" in updates:
                thread.is_archived = updates["is_archived"]
            if "tags" in updates and hasattr(thread.metadata, 'tags'):
                thread.metadata.tags = updates["tags"]
            
            thread.updated_at = datetime.utcnow()
            
            # Store updated thread
            success = await self._store_thread(thread)
            if not success:
                raise ThreadStorageError("Failed to update thread")
            
            await self._update_thread_stats(user_id, "updated")
            
            logger.info(f"Thread updated successfully: {thread_id}")
            return thread
            
        except (ThreadNotFoundError, ThreadAccessDeniedError, ThreadStorageError):
            raise
        except Exception as e:
            logger.error(f"Error updating thread {thread_id}: {e}")
            raise ThreadStorageError("Failed to update thread")
    
    async def delete_thread(self, thread_id: str, user_id: str) -> bool:
        """Delete a thread"""
        try:
            # Get thread to verify ownership
            thread = await self._get_thread_from_redis(thread_id)
            if not thread:
                raise ThreadNotFoundError("Thread not found")
            
            # Check permissions
            if thread.user_id != user_id:
                raise ThreadAccessDeniedError("Access denied to this thread")
            
            # Delete from Redis
            success = await self._delete_thread_from_redis(thread_id)
            if not success:
                raise ThreadStorageError("Failed to delete thread")
            
            # Remove from user's thread list
            await self._remove_thread_from_user_list(user_id, thread_id)
            
            # Update stats
            await self._update_thread_stats(user_id, "deleted")
            
            logger.info(f"Thread deleted successfully: {thread_id}")
            return True
            
        except (ThreadNotFoundError, ThreadAccessDeniedError, ThreadStorageError):
            raise
        except Exception as e:
            logger.error(f"Error deleting thread {thread_id}: {e}")
            return False
    
    async def get_user_thread_count(self, user_id: str) -> int:
        """Get the number of threads for a user"""
        try:
            thread_ids = await self._get_user_thread_ids(user_id)
            return len(thread_ids)
        except Exception as e:
            logger.error(f"Error getting thread count for user {user_id}: {e}")
            return 0
    
    async def increment_copy_count(self, thread_id: str, user_id: str) -> bool:
        """Increment the copy count for a thread"""
        try:
            thread = await self._get_thread_from_redis(thread_id)
            if thread and thread.user_id == user_id:
                thread.copy_count += 1
                thread.updated_at = datetime.utcnow()
                await self._store_thread(thread)
                await self._update_thread_stats(user_id, "copied")
                return True
            return False
        except Exception as e:
            logger.error(f"Error incrementing copy count for thread {thread_id}: {e}")
            return False
    
    # Private methods for Redis operations
    
    async def _store_thread(self, thread: SavedThread) -> bool:
        """Store thread in Redis"""
        thread_key = f"{self.thread_prefix}{thread.id}"
        
        def _store():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return False
                try:
                    # Store thread data with TTL
                    thread_ttl = self.thread_ttl_days * 24 * 3600
                    r.setex(thread_key, thread_ttl, thread.model_dump_json())
                    return True
                except Exception as e:
                    logger.error(f"Error storing thread in Redis: {e}")
                    return False
        
        # Run in thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.redis_manager.executor, _store)
    
    async def _get_thread_from_redis(self, thread_id: str) -> Optional[SavedThread]:
        """Get thread from Redis by ID"""
        thread_key = f"{self.thread_prefix}{thread_id}"
        
        def _get():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return None
                try:
                    thread_data = r.get(thread_key)
                    if thread_data:
                        data = json.loads(thread_data)
                        return SavedThread(**data)
                    return None
                except Exception as e:
                    logger.error(f"Error getting thread from Redis: {e}")
                    return None
        
        # Run in thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.redis_manager.executor, _get)
    
    async def _delete_thread_from_redis(self, thread_id: str) -> bool:
        """Delete thread from Redis"""
        thread_key = f"{self.thread_prefix}{thread_id}"
        
        def _delete():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return False
                try:
                    r.delete(thread_key)
                    return True
                except Exception as e:
                    logger.error(f"Error deleting thread from Redis: {e}")
                    return False
        
        # Run in thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.redis_manager.executor, _delete)
    
    async def _get_user_thread_ids(self, user_id: str) -> List[str]:
        """Get list of thread IDs for a user"""
        user_threads_key = f"{self.user_threads_prefix}{user_id}"
        
        def _get():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return []
                try:
                    thread_ids_data = r.get(user_threads_key)
                    if thread_ids_data:
                        return json.loads(thread_ids_data)
                    return []
                except Exception as e:
                    logger.error(f"Error getting user thread IDs: {e}")
                    return []
        
        # Run in thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.redis_manager.executor, _get)
    
    async def _add_thread_to_user_list(self, user_id: str, thread_id: str) -> bool:
        """Add thread ID to user's thread list"""
        user_threads_key = f"{self.user_threads_prefix}{user_id}"
        
        def _add():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return False
                try:
                    # Get current list
                    thread_ids_data = r.get(user_threads_key)
                    if thread_ids_data:
                        thread_ids = json.loads(thread_ids_data)
                    else:
                        thread_ids = []
                    
                    # Add new thread ID at the beginning (most recent first)
                    if thread_id not in thread_ids:
                        thread_ids.insert(0, thread_id)
                    
                    # Store updated list with TTL
                    list_ttl = self.thread_ttl_days * 24 * 3600
                    r.setex(user_threads_key, list_ttl, json.dumps(thread_ids))
                    return True
                except Exception as e:
                    logger.error(f"Error adding thread to user list: {e}")
                    return False
        
        # Run in thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.redis_manager.executor, _add)
    
    async def _remove_thread_from_user_list(self, user_id: str, thread_id: str) -> bool:
        """Remove thread ID from user's thread list"""
        user_threads_key = f"{self.user_threads_prefix}{user_id}"
        
        def _remove():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return False
                try:
                    # Get current list
                    thread_ids_data = r.get(user_threads_key)
                    if thread_ids_data:
                        thread_ids = json.loads(thread_ids_data)
                        if thread_id in thread_ids:
                            thread_ids.remove(thread_id)
                            # Store updated list
                            list_ttl = self.thread_ttl_days * 24 * 3600
                            r.setex(user_threads_key, list_ttl, json.dumps(thread_ids))
                    return True
                except Exception as e:
                    logger.error(f"Error removing thread from user list: {e}")
                    return False
        
        # Run in thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.redis_manager.executor, _remove)
    
    async def _update_thread_stats(self, user_id: str, action: str) -> bool:
        """Update thread statistics"""
        stats_key = f"{self.thread_stats_key}:{user_id}"
        
        def _update():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return False
                try:
                    # Get current stats
                    stats_data = r.get(stats_key)
                    if stats_data:
                        stats = json.loads(stats_data)
                    else:
                        stats = {"created": 0, "viewed": 0, "updated": 0, "deleted": 0, "copied": 0}
                    
                    # Update counter
                    if action in stats:
                        stats[action] += 1
                    
                    # Store updated stats with 30-day TTL
                    stats_ttl = 30 * 24 * 3600
                    r.setex(stats_key, stats_ttl, json.dumps(stats))
                    return True
                except Exception as e:
                    logger.error(f"Error updating thread stats: {e}")
                    return False
        
        # Run in thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.redis_manager.executor, _update)
    
    def _apply_filters(self, threads: List[SavedThread], filters: ThreadHistoryFilter) -> List[SavedThread]:
        """Apply filters to thread list"""
        filtered_threads = threads
        
        # Search query filter
        if filters.search_query:
            query = filters.search_query.lower()
            filtered_threads = [
                t for t in filtered_threads 
                if query in t.title.lower() or 
                   query in t.original_content.lower() or
                   any(query in tweet.content.lower() for tweet in t.tweets)
            ]
        
        # Source type filter
        if filters.source_type:
            filtered_threads = [
                t for t in filtered_threads 
                if t.metadata.source_type == filters.source_type
            ]
        
        # Favorite filter
        if filters.is_favorite is not None:
            filtered_threads = [
                t for t in filtered_threads 
                if t.is_favorite == filters.is_favorite
            ]
        
        # Archived filter
        if filters.is_archived is not None:
            filtered_threads = [
                t for t in filtered_threads 
                if t.is_archived == filters.is_archived
            ]
        
        # Date filters
        if filters.date_from:
            filtered_threads = [
                t for t in filtered_threads 
                if t.created_at >= filters.date_from
            ]
        
        if filters.date_to:
            filtered_threads = [
                t for t in filtered_threads 
                if t.created_at <= filters.date_to
            ]
        
        return filtered_threads
    
    def _sort_threads(self, threads: List[SavedThread], sort_by: str, sort_order: str) -> List[SavedThread]:
        """Sort thread list"""
        reverse = sort_order == "desc"
        
        if sort_by == "created_at":
            return sorted(threads, key=lambda t: t.created_at, reverse=reverse)
        elif sort_by == "updated_at":
            return sorted(threads, key=lambda t: t.updated_at, reverse=reverse)
        elif sort_by == "title":
            return sorted(threads, key=lambda t: t.title.lower(), reverse=reverse)
        elif sort_by == "tweet_count":
            return sorted(threads, key=lambda t: t.tweet_count, reverse=reverse)
        else:
            # Default to created_at desc
            return sorted(threads, key=lambda t: t.created_at, reverse=True)
    
    def __del__(self):
        """Cleanup when service is destroyed"""
        if hasattr(self, 'redis_manager') and hasattr(self.redis_manager, 'executor'):
            self.redis_manager.executor.shutdown(wait=False)


# Import os at the top level
import os