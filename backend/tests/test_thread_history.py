"""
Test script for Thread History functionality
Tests the thread models, service, and API endpoints
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the src directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the required modules
from thread_models import SavedThread, ThreadTweet, ThreadMetadata, ThreadHistoryFilter
from thread_service import ThreadHistoryService
from redis_manager import initialize_redis, get_redis_manager


async def test_thread_models():
    """Test thread model creation and validation"""
    print("=== Testing Thread Models ===")
    
    # Test ThreadTweet
    tweet = ThreadTweet(
        content="This is a test tweet for the Threadr app!",
        order=1,
        character_count=42
    )
    print(f"[OK] Created tweet: {tweet.content} (ID: {tweet.id})")
    
    # Test ThreadMetadata
    metadata = ThreadMetadata(
        source_url="https://example.com/article",
        source_type="url",
        ai_model="gpt-3.5-turbo",
        content_length=1000,
        tags=["test", "threadr"]
    )
    print(f"[OK] Created metadata: {metadata.source_type} from {metadata.source_url}")
    
    # Test SavedThread
    saved_thread = SavedThread(
        user_id="test-user-123",
        title="Test Thread from Example Article",
        original_content="This is the original content from the article...",
        tweets=[tweet],
        metadata=metadata
    )
    print(f"[OK] Created saved thread: {saved_thread.title} (ID: {saved_thread.id})")
    print(f"  - Tweet count: {saved_thread.tweet_count}")
    print(f"  - Total characters: {saved_thread.total_characters}")
    print(f"  - Preview: {saved_thread.get_preview_text(50)}")
    
    return saved_thread


async def test_thread_service():
    """Test thread service operations"""
    print("\n=== Testing Thread Service ===")
    
    # Initialize Redis manager
    redis_manager = get_redis_manager()
    if not redis_manager:
        print("[WARN] Redis not available - initializing new manager")
        redis_manager = initialize_redis()
    
    if not redis_manager or not redis_manager.is_available:
        print("[ERROR] Redis not available - cannot test thread service")
        return None
    
    print(f"[OK] Redis connected: {redis_manager.is_available}")
    
    # Initialize thread service
    thread_service = ThreadHistoryService(redis_manager)
    print("[OK] Thread service initialized")
    
    # Test saving a thread
    user_id = "test-user-123"
    title = "Test Thread - API Integration"
    original_content = "This is a test thread created for testing the thread history API. It contains multiple tweets that will be split properly."
    tweets_data = [
        {"content": "This is the first tweet in our test thread!"},
        {"content": "This is the second tweet with some more content to test the threading functionality."},
        {"content": "And this is the final tweet to complete our test thread!"}
    ]
    metadata = {
        "source_type": "text",
        "ai_model": "test",
        "content_length": len(original_content),
        "tags": ["test", "api"]
    }
    
    try:
        saved_thread = await thread_service.save_thread(
            user_id=user_id,
            title=title,
            original_content=original_content,
            tweets=tweets_data,
            metadata=metadata,
            client_ip="127.0.0.1"
        )
        
        print(f"[OK] Thread saved successfully: {saved_thread.id}")
        print(f"  - Title: {saved_thread.title}")
        print(f"  - Tweets: {len(saved_thread.tweets)}")
        
        # Test retrieving the thread
        retrieved_thread = await thread_service.get_thread_by_id(
            thread_id=saved_thread.id,
            user_id=user_id,
            increment_view=True
        )
        
        if retrieved_thread:
            print(f"[OK] Thread retrieved successfully: {retrieved_thread.id}")
            print(f"  - View count: {retrieved_thread.view_count}")
        else:
            print("[ERROR] Failed to retrieve saved thread")
        
        # Test getting user thread history
        history = await thread_service.get_user_threads(
            user_id=user_id,
            page=1,
            page_size=10
        )
        
        print(f"[OK] Thread history retrieved: {history.total_count} threads")
        for thread_dict in history.threads:
            print(f"  - {thread_dict['title']} ({thread_dict['tweet_count']} tweets)")
        
        # Test thread count
        thread_count = await thread_service.get_user_thread_count(user_id)
        print(f"[OK] User thread count: {thread_count}")
        
        return saved_thread
        
    except Exception as e:
        print(f"[ERROR] Thread service test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_filters_and_search():
    """Test filtering and search functionality"""
    print("\n=== Testing Filters and Search ===")
    
    redis_manager = get_redis_manager()
    if not redis_manager or not redis_manager.is_available:
        print("[ERROR] Redis not available - skipping filter tests")
        return
    
    thread_service = ThreadHistoryService(redis_manager)
    user_id = "test-user-123"
    
    # Create a few more test threads with different properties
    test_threads = [
        {
            "title": "URL Thread from Medium",
            "original_content": "Content from a Medium article about tech trends",
            "tweets": [{"content": "Tech trends are fascinating! Here's what I learned from this Medium article..."}],
            "metadata": {"source_type": "url", "source_url": "https://medium.com/example", "tags": ["tech", "trends"]}
        },
        {
            "title": "Text Thread about Programming",
            "original_content": "A discussion about programming best practices and clean code",
            "tweets": [{"content": "Let's talk about programming best practices and why clean code matters!"}],
            "metadata": {"source_type": "text", "tags": ["programming", "clean-code"]}
        }
    ]
    
    saved_ids = []
    for thread_data in test_threads:
        try:
            saved_thread = await thread_service.save_thread(
                user_id=user_id,
                title=thread_data["title"],
                original_content=thread_data["original_content"],
                tweets=thread_data["tweets"],
                metadata=thread_data["metadata"],
                client_ip="127.0.0.1"
            )
            saved_ids.append(saved_thread.id)
            print(f"[OK] Created test thread: {saved_thread.title}")
        except Exception as e:
            print(f"[ERROR] Failed to create test thread: {e}")
    
    # Test search functionality
    search_filter = ThreadHistoryFilter(search_query="programming")
    history = await thread_service.get_user_threads(
        user_id=user_id,
        page=1,
        page_size=10,
        filters=search_filter
    )
    
    print(f"[OK] Search results for 'programming': {history.total_count} threads")
    for thread_dict in history.threads:
        print(f"  - {thread_dict['title']}")
    
    # Test source type filter
    url_filter = ThreadHistoryFilter(source_type="url")
    url_history = await thread_service.get_user_threads(
        user_id=user_id,
        page=1,
        page_size=10,
        filters=url_filter
    )
    
    print(f"[OK] URL threads: {url_history.total_count} threads")
    for thread_dict in url_history.threads:
        print(f"  - {thread_dict['title']} (source: {thread_dict['metadata']['source_type']})")


async def main():
    """Run all tests"""
    print("Thread History System Test Suite")
    print("=" * 50)
    
    # Test models
    test_thread = await test_thread_models()
    
    # Test service
    saved_thread = await test_thread_service()
    
    # Test filters
    await test_filters_and_search()
    
    print("\n" + "=" * 50)
    print("Thread History Test Suite Completed!")
    
    if saved_thread:
        print(f"\nTest thread created: {saved_thread.id}")
        print("You can test the API endpoints with this thread ID.")


if __name__ == "__main__":
    asyncio.run(main())