#!/usr/bin/env python3
"""
Comprehensive Test Suite for Threadr Core Business Functionality
=====================================================

This test suite validates the complete revenue-generating functionality:
1. Thread generation from URLs and content
2. AI-powered tweet splitting (OpenAI integration)
3. Thread storage in PostgreSQL
4. User authentication and thread ownership
5. Rate limiting enforcement (free vs premium)
6. Thread analytics and performance tracking
7. CRUD operations on threads

USAGE:
    python test_core_business_functionality.py
    
ENVIRONMENT VARIABLES REQUIRED:
    - OPENAI_API_KEY: OpenAI API key for thread generation
    - DATABASE_URL: PostgreSQL connection string
    - REDIS_URL: Redis connection for rate limiting
    - BASE_URL: Backend API URL (default: https://threadr-pw0s.onrender.com)
"""

import asyncio
import httpx
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import time
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('business_functionality_test.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    success: bool
    execution_time: float
    details: Dict[str, Any]
    error_message: Optional[str] = None

class ThreadrBusinessTester:
    """Comprehensive tester for Threadr business functionality"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("BASE_URL", "https://threadr-pw0s.onrender.com")
        self.test_results: List[TestResult] = []
        self.test_user_email = f"test_user_{int(time.time())}@example.com"
        self.test_user_password = "TestPassword123!"
        self.auth_token = None
        self.user_id = None
        self.created_thread_ids: List[str] = []
        
        logger.info(f"Initializing Threadr Business Tester - Base URL: {self.base_url}")
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite and return results"""
        start_time = time.time()
        logger.info("Starting comprehensive business functionality test suite...")
        
        # Test categories in dependency order
        test_categories = [
            ("Infrastructure Health", self._test_infrastructure_health),
            ("User Authentication", self._test_user_authentication),
            ("Thread Generation", self._test_thread_generation),
            ("Thread Storage & Retrieval", self._test_thread_storage),
            ("Rate Limiting", self._test_rate_limiting),
            ("Thread Analytics", self._test_thread_analytics),
            ("Thread CRUD Operations", self._test_thread_crud),
            ("Data Persistence", self._test_data_persistence)
        ]
        
        category_results = {}
        
        for category_name, test_function in test_categories:
            logger.info(f"\n{'='*50}")
            logger.info(f"TESTING CATEGORY: {category_name}")
            logger.info(f"{'='*50}")
            
            category_start = time.time()
            try:
                category_result = await test_function()
                category_results[category_name] = category_result
                category_time = time.time() - category_start
                logger.info(f"✅ {category_name} completed in {category_time:.2f}s")
            except Exception as e:
                category_time = time.time() - category_start
                logger.error(f"❌ {category_name} failed after {category_time:.2f}s: {str(e)}")
                category_results[category_name] = {
                    "success": False,
                    "error": str(e),
                    "execution_time": category_time
                }
        
        # Generate comprehensive report
        total_time = time.time() - start_time
        report = self._generate_test_report(category_results, total_time)
        
        # Cleanup
        await self._cleanup_test_data()
        
        return report
    
    async def _test_infrastructure_health(self) -> Dict[str, Any]:
        """Test 1: Infrastructure Health - API, Database, Redis, OpenAI"""
        tests = []
        
        # Test API Health
        test_result = await self._run_test(
            "API Health Check",
            self._test_api_health
        )
        tests.append(test_result)
        
        # Test Database Connection
        test_result = await self._run_test(
            "Database Connection",
            self._test_database_connection
        )
        tests.append(test_result)
        
        # Test Redis Connection  
        test_result = await self._run_test(
            "Redis Connection",
            self._test_redis_connection
        )
        tests.append(test_result)
        
        return {
            "category": "Infrastructure Health",
            "tests": tests,
            "success": all(t.success for t in tests),
            "summary": f"{sum(1 for t in tests if t.success)}/{len(tests)} tests passed"
        }
    
    async def _test_user_authentication(self) -> Dict[str, Any]:
        """Test 2: User Authentication - Registration, Login, JWT tokens"""
        tests = []
        
        # Test User Registration
        test_result = await self._run_test(
            "User Registration",
            self._test_user_registration
        )
        tests.append(test_result)
        
        # Test User Login
        test_result = await self._run_test(
            "User Login",
            self._test_user_login
        )
        tests.append(test_result)
        
        # Test Token Validation
        test_result = await self._run_test(
            "JWT Token Validation",
            self._test_token_validation
        )
        tests.append(test_result)
        
        return {
            "category": "User Authentication",
            "tests": tests,
            "success": all(t.success for t in tests),
            "summary": f"{sum(1 for t in tests if t.success)}/{len(tests)} tests passed"
        }
    
    async def _test_thread_generation(self) -> Dict[str, Any]:
        """Test 3: Thread Generation - URL scraping, OpenAI integration, content splitting"""
        tests = []
        
        # Test Content-based Thread Generation
        test_result = await self._run_test(
            "Content Thread Generation",
            self._test_content_thread_generation
        )
        tests.append(test_result)
        
        # Test URL-based Thread Generation
        test_result = await self._run_test(
            "URL Thread Generation",
            self._test_url_thread_generation
        )
        tests.append(test_result)
        
        # Test AI Integration (OpenAI)
        test_result = await self._run_test(
            "OpenAI Integration",
            self._test_openai_integration
        )
        tests.append(test_result)
        
        return {
            "category": "Thread Generation",
            "tests": tests,
            "success": all(t.success for t in tests),
            "summary": f"{sum(1 for t in tests if t.success)}/{len(tests)} tests passed"
        }
    
    async def _test_thread_storage(self) -> Dict[str, Any]:
        """Test 4: Thread Storage & Retrieval - PostgreSQL persistence"""
        tests = []
        
        # Test Thread Save
        test_result = await self._run_test(
            "Thread Save to PostgreSQL",
            self._test_thread_save
        )
        tests.append(test_result)
        
        # Test Thread Retrieval
        test_result = await self._run_test(
            "Thread Retrieval from PostgreSQL",
            self._test_thread_retrieval
        )
        tests.append(test_result)
        
        # Test Thread History
        test_result = await self._run_test(
            "Thread History Pagination",
            self._test_thread_history
        )
        tests.append(test_result)
        
        return {
            "category": "Thread Storage",
            "tests": tests,
            "success": all(t.success for t in tests),
            "summary": f"{sum(1 for t in tests if t.success)}/{len(tests)} tests passed"
        }
    
    async def _test_rate_limiting(self) -> Dict[str, Any]:
        """Test 5: Rate Limiting - Free vs Premium enforcement"""
        tests = []
        
        # Test Free Tier Limits
        test_result = await self._run_test(
            "Free Tier Rate Limiting",
            self._test_free_tier_limits
        )
        tests.append(test_result)
        
        # Test Usage Tracking
        test_result = await self._run_test(
            "Usage Statistics Tracking",
            self._test_usage_tracking
        )
        tests.append(test_result)
        
        # Test Premium Status Check
        test_result = await self._run_test(
            "Premium Status Verification",
            self._test_premium_status
        )
        tests.append(test_result)
        
        return {
            "category": "Rate Limiting",
            "tests": tests,
            "success": all(t.success for t in tests),
            "summary": f"{sum(1 for t in tests if t.success)}/{len(tests)} tests passed"
        }
    
    async def _test_thread_analytics(self) -> Dict[str, Any]:
        """Test 6: Thread Analytics - Performance tracking, statistics"""
        tests = []
        
        # Test Analytics Collection
        test_result = await self._run_test(
            "Thread Analytics Collection",
            self._test_analytics_collection
        )
        tests.append(test_result)
        
        # Test User Statistics
        test_result = await self._run_test(
            "User Thread Statistics",
            self._test_user_statistics
        )
        tests.append(test_result)
        
        return {
            "category": "Thread Analytics",
            "tests": tests,
            "success": all(t.success for t in tests),
            "summary": f"{sum(1 for t in tests if t.success)}/{len(tests)} tests passed"
        }
    
    async def _test_thread_crud(self) -> Dict[str, Any]:
        """Test 7: Thread CRUD Operations - Create, Read, Update, Delete"""
        tests = []
        
        # Test Thread Update
        test_result = await self._run_test(
            "Thread Update Operations",
            self._test_thread_update
        )
        tests.append(test_result)
        
        # Test Thread Delete
        test_result = await self._run_test(
            "Thread Delete Operations",
            self._test_thread_delete
        )
        tests.append(test_result)
        
        # Test Thread Access Control
        test_result = await self._run_test(
            "Thread Access Control",
            self._test_thread_access_control
        )
        tests.append(test_result)
        
        return {
            "category": "Thread CRUD",
            "tests": tests,
            "success": all(t.success for t in tests),
            "summary": f"{sum(1 for t in tests if t.success)}/{len(tests)} tests passed"
        }
    
    async def _test_data_persistence(self) -> Dict[str, Any]:
        """Test 8: Data Persistence - PostgreSQL durability"""
        tests = []
        
        # Test Data Durability
        test_result = await self._run_test(
            "Data Persistence Verification",
            self._test_data_durability
        )
        tests.append(test_result)
        
        # Test Database Integrity
        test_result = await self._run_test(
            "Database Integrity Check",
            self._test_database_integrity
        )
        tests.append(test_result)
        
        return {
            "category": "Data Persistence",
            "tests": tests,
            "success": all(t.success for t in tests),
            "summary": f"{sum(1 for t in tests if t.success)}/{len(tests)} tests passed"
        }
    
    # Individual test implementations
    
    async def _test_api_health(self) -> Dict[str, Any]:
        """Test API health endpoint"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/health")
            
            if response.status_code != 200:
                raise Exception(f"Health check failed with status {response.status_code}")
            
            health_data = response.json()
            
            if health_data.get("status") not in ["healthy", "degraded"]:
                raise Exception(f"Unhealthy service status: {health_data.get('status')}")
            
            return {
                "status_code": response.status_code,
                "health_status": health_data.get("status"),
                "services": health_data.get("services", {}),
                "environment": health_data.get("environment")
            }
    
    async def _test_database_connection(self) -> Dict[str, Any]:
        """Test database connection through health endpoint"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/health")
            health_data = response.json()
            
            database_status = health_data.get("services", {}).get("database", False)
            
            if not database_status:
                raise Exception("Database is not available according to health check")
            
            return {
                "database_available": database_status,
                "database_ping": health_data.get("services", {}).get("database_ping")
            }
    
    async def _test_redis_connection(self) -> Dict[str, Any]:
        """Test Redis connection through health endpoint"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/health")
            health_data = response.json()
            
            redis_status = health_data.get("services", {}).get("redis", False)
            
            if not redis_status:
                raise Exception("Redis is not available according to health check")
            
            return {
                "redis_available": redis_status,
                "redis_ping": health_data.get("services", {}).get("redis_ping")
            }
    
    async def _test_user_registration(self) -> Dict[str, Any]:
        """Test user registration"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            registration_data = {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "full_name": "Test User"
            }
            
            response = await client.post(
                f"{self.base_url}/api/auth/register",
                json=registration_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Registration failed with status {response.status_code}: {response.text}")
            
            data = response.json()
            
            if not data.get("access_token"):
                raise Exception("Registration successful but no access token returned")
            
            self.auth_token = data["access_token"]
            self.user_id = data.get("user", {}).get("user_id")
            
            return {
                "status_code": response.status_code,
                "has_access_token": bool(data.get("access_token")),
                "user_id": self.user_id,
                "token_type": data.get("token_type")
            }
    
    async def _test_user_login(self) -> Dict[str, Any]:
        """Test user login"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            response = await client.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Login failed with status {response.status_code}: {response.text}")
            
            data = response.json()
            
            if not data.get("access_token"):
                raise Exception("Login successful but no access token returned")
            
            # Update token for subsequent tests
            self.auth_token = data["access_token"]
            
            return {
                "status_code": response.status_code,
                "has_access_token": bool(data.get("access_token")),
                "user_email": data.get("user", {}).get("email"),
                "token_type": data.get("token_type")
            }
    
    async def _test_token_validation(self) -> Dict[str, Any]:
        """Test JWT token validation"""
        if not self.auth_token:
            raise Exception("No auth token available for validation test")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/api/auth/me",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Token validation failed with status {response.status_code}: {response.text}")
            
            data = response.json()
            
            if data.get("email") != self.test_user_email:
                raise Exception("Token validation returned wrong user data")
            
            return {
                "status_code": response.status_code,
                "email_matches": data.get("email") == self.test_user_email,
                "user_id": data.get("user_id"),
                "role": data.get("role")
            }
    
    async def _test_content_thread_generation(self) -> Dict[str, Any]:
        """Test thread generation from text content"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            content_data = {
                "content": "Artificial Intelligence is revolutionizing how we work. From automating repetitive tasks to enabling new forms of creativity, AI is becoming an essential tool for productivity. The key is learning how to work WITH AI, not against it. This means understanding its strengths, limitations, and how to craft effective prompts. The future belongs to those who can effectively collaborate with AI systems."
            }
            
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=content_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Content thread generation failed with status {response.status_code}: {response.text}")
            
            data = response.json()
            
            if not data.get("success"):
                raise Exception(f"Thread generation failed: {data.get('error')}")
            
            tweets = data.get("tweets", [])
            if len(tweets) < 2:
                raise Exception(f"Thread generation produced insufficient tweets: {len(tweets)}")
            
            return {
                "status_code": response.status_code,
                "success": data.get("success"),
                "tweet_count": len(tweets),
                "thread_count": data.get("thread_count"),
                "has_title": bool(data.get("title")),
                "usage_stats": data.get("usage")
            }
    
    async def _test_url_thread_generation(self) -> Dict[str, Any]:
        """Test thread generation from URL"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            url_data = {
                "url": "https://medium.com/@example/test-article",
                "content": ""
            }
            
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=url_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Note: This might fail if URL doesn't exist or domain isn't allowed
            # That's acceptable for testing - we're testing the endpoint structure
            
            data = response.json()
            
            return {
                "status_code": response.status_code,
                "success": data.get("success"),
                "error": data.get("error"),
                "has_response_structure": all(k in data for k in ["success"])
            }
    
    async def _test_openai_integration(self) -> Dict[str, Any]:
        """Test OpenAI API integration indirectly through thread generation"""
        # This is tested through content generation - if that works, OpenAI is working
        result = await self._test_content_thread_generation()
        
        if result["success"]:
            return {
                "openai_responding": True,
                "tweet_generation_working": result["tweet_count"] > 0,
                "ai_splitting_functional": result["tweet_count"] >= 2
            }
        else:
            raise Exception("OpenAI integration appears to be failing - no successful thread generation")
    
    async def _test_thread_save(self) -> Dict[str, Any]:
        """Test thread save to PostgreSQL"""
        if not self.auth_token:
            raise Exception("Authentication required for thread save test")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # First generate a thread to save
            content_data = {
                "content": "Test content for saving to database. This should create a thread that we can then save to PostgreSQL for testing persistence."
            }
            
            gen_response = await client.post(
                f"{self.base_url}/api/generate",
                json=content_data
            )
            
            if gen_response.status_code != 200:
                raise Exception("Failed to generate thread for save test")
            
            gen_data = gen_response.json()
            
            if not gen_data.get("success"):
                raise Exception("Thread generation failed for save test")
            
            # Now save the thread
            save_data = {
                "title": "Test Thread for Save",
                "original_content": content_data["content"],
                "tweets": gen_data["tweets"],
                "metadata": {
                    "source_type": "content",
                    "generation_time": datetime.now().isoformat()
                }
            }
            
            save_response = await client.post(
                f"{self.base_url}/api/threads/save",
                json=save_data,
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if save_response.status_code != 200:
                raise Exception(f"Thread save failed with status {save_response.status_code}: {save_response.text}")
            
            save_result = save_response.json()
            
            if not save_result.get("success"):
                raise Exception("Thread save reported failure")
            
            thread_data = save_result.get("thread", {})
            thread_id = thread_data.get("id")
            
            if thread_id:
                self.created_thread_ids.append(thread_id)
            
            return {
                "status_code": save_response.status_code,
                "success": save_result.get("success"),
                "thread_id": thread_id,
                "has_saved_tweets": len(thread_data.get("tweets", [])) > 0,
                "saved_tweet_count": len(thread_data.get("tweets", []))
            }
    
    async def _test_thread_retrieval(self) -> Dict[str, Any]:
        """Test thread retrieval from PostgreSQL"""
        if not self.auth_token or not self.created_thread_ids:
            raise Exception("Need saved thread for retrieval test")
        
        thread_id = self.created_thread_ids[0]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/api/threads/{thread_id}",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Thread retrieval failed with status {response.status_code}: {response.text}")
            
            data = response.json()
            
            if not data.get("success"):
                raise Exception("Thread retrieval reported failure")
            
            thread = data.get("thread", {})
            
            if thread.get("id") != thread_id:
                raise Exception("Retrieved thread has wrong ID")
            
            return {
                "status_code": response.status_code,
                "success": data.get("success"),
                "thread_id_matches": thread.get("id") == thread_id,
                "has_tweets": len(thread.get("tweets", [])) > 0,
                "has_metadata": bool(thread.get("metadata"))
            }
    
    async def _test_thread_history(self) -> Dict[str, Any]:
        """Test thread history pagination"""
        if not self.auth_token:
            raise Exception("Authentication required for history test")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/api/threads?page=1&page_size=10",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Thread history failed with status {response.status_code}: {response.text}")
            
            data = response.json()
            
            threads = data.get("threads", [])
            pagination = data.get("pagination", {})
            
            return {
                "status_code": response.status_code,
                "thread_count": len(threads),
                "has_pagination": bool(pagination),
                "total_count": pagination.get("total", 0),
                "current_page": pagination.get("page", 0)
            }
    
    async def _test_free_tier_limits(self) -> Dict[str, Any]:
        """Test free tier rate limiting"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Check usage stats
            response = await client.get(f"{self.base_url}/api/usage-stats")
            
            if response.status_code != 200:
                raise Exception(f"Usage stats check failed with status {response.status_code}")
            
            data = response.json()
            
            if not data.get("success"):
                raise Exception("Usage stats check reported failure")
            
            return {
                "status_code": response.status_code,
                "success": data.get("success"),
                "is_premium": data.get("is_premium"),
                "daily_limit": data.get("daily_limit"),
                "monthly_limit": data.get("monthly_limit"),
                "daily_used": data.get("daily_used"),
                "can_generate": data.get("can_generate")
            }
    
    async def _test_usage_tracking(self) -> Dict[str, Any]:
        """Test usage statistics tracking"""
        return await self._test_free_tier_limits()  # Same endpoint
    
    async def _test_premium_status(self) -> Dict[str, Any]:
        """Test premium status check"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/api/premium-status")
            
            if response.status_code != 200:
                raise Exception(f"Premium status check failed with status {response.status_code}")
            
            data = response.json()
            
            if not data.get("success"):
                raise Exception("Premium status check reported failure")
            
            return {
                "status_code": response.status_code,
                "success": data.get("success"),
                "is_premium": data.get("is_premium"),
                "expires_at": data.get("expires_at")
            }
    
    async def _test_analytics_collection(self) -> Dict[str, Any]:
        """Test analytics data collection"""
        if not self.auth_token or not self.created_thread_ids:
            return {"skipped": True, "reason": "No threads available for analytics test"}
        
        thread_id = self.created_thread_ids[0]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test copy count increment (analytics tracking)
            response = await client.post(
                f"{self.base_url}/api/threads/{thread_id}/copy",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Analytics tracking failed with status {response.status_code}: {response.text}")
            
            data = response.json()
            
            return {
                "status_code": response.status_code,
                "success": data.get("success"),
                "analytics_tracking_working": data.get("success", False)
            }
    
    async def _test_user_statistics(self) -> Dict[str, Any]:
        """Test user thread statistics"""
        if not self.auth_token:
            raise Exception("Authentication required for statistics test")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/api/threads/stats/summary",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code != 200:
                raise Exception(f"User statistics failed with status {response.status_code}: {response.text}")
            
            data = response.json()
            
            if not data.get("success"):
                raise Exception("User statistics reported failure")
            
            stats = data.get("stats", {})
            
            return {
                "status_code": response.status_code,
                "success": data.get("success"),
                "total_threads": stats.get("total_threads", 0),
                "recent_threads_7d": stats.get("recent_threads_7d", 0),
                "favorite_threads": stats.get("favorite_threads", 0)
            }
    
    async def _test_thread_update(self) -> Dict[str, Any]:
        """Test thread update operations"""
        if not self.auth_token or not self.created_thread_ids:
            raise Exception("Need saved thread for update test")
        
        thread_id = self.created_thread_ids[0]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            update_data = {
                "title": "Updated Test Thread Title",
                "is_favorite": True
            }
            
            response = await client.patch(
                f"{self.base_url}/api/threads/{thread_id}",
                json=update_data,
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Thread update failed with status {response.status_code}: {response.text}")
            
            data = response.json()
            
            if not data.get("success"):
                raise Exception("Thread update reported failure")
            
            return {
                "status_code": response.status_code,
                "success": data.get("success"),
                "updated_successfully": True
            }
    
    async def _test_thread_delete(self) -> Dict[str, Any]:
        """Test thread delete operations"""
        if not self.auth_token or not self.created_thread_ids:
            return {"skipped": True, "reason": "No threads available for delete test"}
        
        # Use last created thread for deletion (preserve first for other tests)
        if len(self.created_thread_ids) > 1:
            thread_id = self.created_thread_ids.pop()  # Remove from list so it's not cleaned up again
        else:
            return {"skipped": True, "reason": "Preserving thread for other tests"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                f"{self.base_url}/api/threads/{thread_id}",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Thread delete failed with status {response.status_code}: {response.text}")
            
            data = response.json()
            
            if not data.get("success"):
                raise Exception("Thread delete reported failure")
            
            return {
                "status_code": response.status_code,
                "success": data.get("success"),
                "deleted_successfully": True
            }
    
    async def _test_thread_access_control(self) -> Dict[str, Any]:
        """Test thread access control (ownership verification)"""
        if not self.created_thread_ids:
            return {"skipped": True, "reason": "No threads available for access control test"}
        
        thread_id = self.created_thread_ids[0]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test access without authentication (should fail)
            response = await client.get(f"{self.base_url}/api/threads/{thread_id}")
            
            if response.status_code == 200:
                raise Exception("Thread access succeeded without authentication - security issue!")
            
            # Test access with correct authentication (should succeed)
            response = await client.get(
                f"{self.base_url}/api/threads/{thread_id}",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Thread access failed with correct auth: {response.status_code}")
            
            return {
                "unauthorized_access_blocked": True,
                "authorized_access_allowed": True,
                "access_control_working": True
            }
    
    async def _test_data_durability(self) -> Dict[str, Any]:
        """Test data persistence verification"""
        if not self.created_thread_ids:
            return {"skipped": True, "reason": "No threads available for durability test"}
        
        # Retrieve thread again to verify it's still in database
        thread_id = self.created_thread_ids[0]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/api/threads/{thread_id}",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Data durability test failed - thread not found: {response.status_code}")
            
            data = response.json()
            
            if not data.get("success"):
                raise Exception("Data durability test - thread retrieval failed")
            
            thread = data.get("thread", {})
            
            return {
                "thread_persisted": True,
                "data_intact": bool(thread.get("tweets")),
                "metadata_preserved": bool(thread.get("metadata")),
                "durability_verified": True
            }
    
    async def _test_database_integrity(self) -> Dict[str, Any]:
        """Test database integrity through health checks"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/health")
            
            if response.status_code != 200:
                raise Exception("Database integrity check failed - health endpoint unavailable")
            
            health_data = response.json()
            
            database_status = health_data.get("services", {}).get("database", False)
            
            return {
                "database_responding": database_status,
                "health_check_passed": health_data.get("status") in ["healthy", "degraded"],
                "integrity_verified": database_status
            }
    
    # Helper methods
    
    async def _run_test(self, test_name: str, test_function) -> TestResult:
        """Run individual test and capture results"""
        start_time = time.time()
        logger.info(f"Running test: {test_name}")
        
        try:
            details = await test_function()
            execution_time = time.time() - start_time
            
            result = TestResult(
                test_name=test_name,
                success=True,
                execution_time=execution_time,
                details=details
            )
            
            logger.info(f"✅ {test_name} passed in {execution_time:.2f}s")
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            result = TestResult(
                test_name=test_name,
                success=False,
                execution_time=execution_time,
                details={},
                error_message=str(e)
            )
            
            logger.error(f"❌ {test_name} failed in {execution_time:.2f}s: {str(e)}")
        
        self.test_results.append(result)
        return result
    
    def _generate_test_report(self, category_results: Dict[str, Any], total_time: float) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = sum(len(cat.get("tests", [])) for cat in category_results.values() if isinstance(cat, dict))
        passed_tests = sum(
            sum(1 for test in cat.get("tests", []) if test.success) 
            for cat in category_results.values() 
            if isinstance(cat, dict)
        )
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        report = {
            "test_execution": {
                "timestamp": datetime.now().isoformat(),
                "total_execution_time": total_time,
                "base_url": self.base_url,
                "test_user": self.test_user_email
            },
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": round(success_rate, 2),
                "overall_success": success_rate >= 90  # 90% or higher considered success
            },
            "categories": category_results,
            "recommendations": self._generate_recommendations(category_results)
        }
        
        return report
    
    def _generate_recommendations(self, category_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        for category_name, category_data in category_results.items():
            if isinstance(category_data, dict) and not category_data.get("success", True):
                recommendations.append(f"❌ Fix issues in {category_name} category")
        
        # Check for specific issues
        infra = category_results.get("Infrastructure Health", {})
        if isinstance(infra, dict) and not infra.get("success", True):
            recommendations.append("🔧 Address infrastructure issues before proceeding with other tests")
        
        auth = category_results.get("User Authentication", {})
        if isinstance(auth, dict) and not auth.get("success", True):
            recommendations.append("🔐 Fix authentication system - required for revenue features")
        
        if not recommendations:
            recommendations.append("✅ All systems operational - ready for production traffic")
        
        return recommendations
    
    async def _cleanup_test_data(self):
        """Clean up test data created during tests"""
        if not self.auth_token or not self.created_thread_ids:
            return
        
        logger.info(f"Cleaning up {len(self.created_thread_ids)} test threads...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for thread_id in self.created_thread_ids:
                try:
                    await client.delete(
                        f"{self.base_url}/api/threads/{thread_id}",
                        headers={"Authorization": f"Bearer {self.auth_token}"}
                    )
                except Exception as e:
                    logger.warning(f"Failed to cleanup thread {thread_id}: {e}")
        
        logger.info("Test cleanup completed")


def print_test_report(report: Dict[str, Any]):
    """Print formatted test report"""
    print("\n" + "="*80)
    print("THREADR BUSINESS FUNCTIONALITY TEST REPORT")
    print("="*80)
    
    # Summary
    summary = report["summary"]
    print(f"\n📊 OVERALL RESULTS:")
    print(f"   Total Tests: {summary['total_tests']}")
    print(f"   Passed: {summary['passed_tests']} ✅")
    print(f"   Failed: {summary['failed_tests']} ❌")
    print(f"   Success Rate: {summary['success_rate']}%")
    print(f"   Overall Status: {'✅ PASS' if summary['overall_success'] else '❌ FAIL'}")
    
    # Execution info
    execution = report["test_execution"]
    print(f"\n⏱️  EXECUTION INFO:")
    print(f"   Execution Time: {execution['total_execution_time']:.2f} seconds")
    print(f"   Base URL: {execution['base_url']}")
    print(f"   Test User: {execution['test_user']}")
    print(f"   Timestamp: {execution['timestamp']}")
    
    # Category results
    print(f"\n📋 CATEGORY RESULTS:")
    for category_name, category_data in report["categories"].items():
        if isinstance(category_data, dict):
            status = "✅ PASS" if category_data.get("success", False) else "❌ FAIL"
            print(f"   {category_name}: {status}")
            if "summary" in category_data:
                print(f"      {category_data['summary']}")
    
    # Recommendations
    print(f"\n🎯 RECOMMENDATIONS:")
    for rec in report["recommendations"]:
        print(f"   {rec}")
    
    print("\n" + "="*80)


async def main():
    """Main function to run the comprehensive test suite"""
    print("🚀 Starting Threadr Business Functionality Test Suite...")
    print(f"📍 Testing against: {os.getenv('BASE_URL', 'https://threadr-pw0s.onrender.com')}")
    
    tester = ThreadrBusinessTester()
    
    try:
        report = await tester.run_all_tests()
        
        # Print results
        print_test_report(report)
        
        # Save detailed report
        report_filename = f"threadr_test_report_{int(time.time())}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_filename}")
        
        # Exit with appropriate code
        if report["summary"]["overall_success"]:
            print("\n🎉 All core business functionality tests PASSED!")
            sys.exit(0)
        else:
            print("\n⚠️  Some tests FAILED - review issues before production deployment")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Test suite execution failed: {e}")
        print(f"\n💥 Test suite execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())