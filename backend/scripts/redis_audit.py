#!/usr/bin/env python3
"""
Redis Data Audit Script for Threadr
Analyzes existing Redis data structures and volumes before PostgreSQL migration
"""

import asyncio
import redis
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
from collections import defaultdict

# Add src to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from core.redis_manager import RedisManager
except ImportError:
    print("ERROR: Could not import RedisManager. Make sure you're running from the correct directory.")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RedisAuditTool:
    """Tool to audit Redis data before migration to PostgreSQL"""
    
    def __init__(self):
        self.redis_manager = RedisManager()
        self.audit_results = {
            'timestamp': datetime.now().isoformat(),
            'redis_available': False,
            'total_keys': 0,
            'data_by_category': {},
            'key_patterns': {},
            'memory_usage': {},
            'expiration_analysis': {},
            'data_samples': {},
            'migration_priorities': {}
        }
    
    async def run_full_audit(self) -> Dict[str, Any]:
        """Run comprehensive audit of Redis data"""
        try:
            logger.info("Starting Redis data audit...")
            
            # Check Redis availability
            if not self.redis_manager.is_available:
                logger.error("Redis is not available. Cannot perform audit.")
                return self.audit_results
            
            self.audit_results['redis_available'] = True
            logger.info("Redis connection confirmed")
            
            # Run all audit components
            await self._audit_key_patterns()
            await self._audit_premium_users()
            await self._audit_email_subscriptions()
            await self._audit_usage_tracking()
            await self._audit_rate_limiting()
            await self._audit_cache_data()
            await self._audit_session_data()
            await self._analyze_memory_usage()
            await self._analyze_expirations()
            await self._prioritize_migration_data()
            
            logger.info("Redis audit completed successfully")
            return self.audit_results
            
        except Exception as e:
            logger.error(f"Error during Redis audit: {e}", exc_info=True)
            self.audit_results['error'] = str(e)
            return self.audit_results
    
    async def _audit_key_patterns(self):
        """Analyze Redis key patterns and distribution"""
        logger.info("Analyzing Redis key patterns...")
        
        def _scan_keys():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return {}
                
                patterns = defaultdict(int)
                total_keys = 0
                
                # Scan all keys and categorize by pattern
                for key in r.scan_iter(count=1000):
                    total_keys += 1
                    
                    # Categorize keys by prefix pattern
                    if key.startswith('threadr:premium:'):
                        patterns['premium_access'] += 1
                    elif key.startswith('threadr:email:'):
                        patterns['email_data'] += 1
                    elif key.startswith('threadr:emails:list'):
                        patterns['email_lists'] += 1
                    elif key.startswith('threadr:usage:'):
                        patterns['usage_tracking'] += 1
                    elif key.startswith('threadr:ratelimit:'):
                        patterns['rate_limiting'] += 1
                    elif key.startswith('threadr:cache:'):
                        patterns['thread_cache'] += 1
                    elif key.startswith('threadr:subscription:'):
                        patterns['subscriptions'] += 1
                    elif key.startswith('threadr:session:'):
                        patterns['user_sessions'] += 1
                    else:
                        patterns['unknown'] += 1
                
                return {
                    'total_keys': total_keys,
                    'patterns': dict(patterns)
                }
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        key_data = await loop.run_in_executor(self.redis_manager.executor, _scan_keys)
        
        self.audit_results['total_keys'] = key_data['total_keys']
        self.audit_results['key_patterns'] = key_data['patterns']
        
        logger.info(f"Found {key_data['total_keys']} total keys across {len(key_data['patterns'])} categories")
    
    async def _audit_premium_users(self):
        """Audit premium user data (CRITICAL for revenue)"""
        logger.info("Auditing premium user data...")
        
        def _scan_premium():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return {}
                
                premium_data = {
                    'ip_based_premium': 0,
                    'email_based_premium': 0,
                    'user_subscriptions': 0,
                    'active_premium': 0,
                    'expired_premium': 0,
                    'samples': []
                }
                
                # Scan IP-based premium access
                for key in r.scan_iter(f"{self.redis_manager.premium_prefix}ip:*"):
                    premium_data['ip_based_premium'] += 1
                    
                    # Get sample data
                    if len(premium_data['samples']) < 5:
                        data = r.get(key)
                        if data:
                            try:
                                parsed = json.loads(data)
                                premium_data['samples'].append({
                                    'key': key,
                                    'type': 'ip_premium',
                                    'data': parsed
                                })
                            except json.JSONDecodeError:
                                pass
                
                # Scan email-based premium access
                for key in r.scan_iter(f"{self.redis_manager.premium_prefix}email:*"):
                    premium_data['email_based_premium'] += 1
                    
                    # Get sample data
                    if len(premium_data['samples']) < 10:
                        data = r.get(key)
                        if data:
                            try:
                                parsed = json.loads(data)
                                premium_data['samples'].append({
                                    'key': key,
                                    'type': 'email_premium',
                                    'data': parsed
                                })
                                
                                # Check if active or expired
                                expires_at = parsed.get('expires_at')
                                if expires_at:
                                    try:
                                        expiry_date = datetime.fromisoformat(expires_at)
                                        if expiry_date > datetime.now():
                                            premium_data['active_premium'] += 1
                                        else:
                                            premium_data['expired_premium'] += 1
                                    except ValueError:
                                        pass
                                        
                            except json.JSONDecodeError:
                                pass
                
                # Scan user subscriptions (new format)
                for key in r.scan_iter("threadr:subscription:user:*"):
                    premium_data['user_subscriptions'] += 1
                    
                    # Get sample data
                    if len(premium_data['samples']) < 15:
                        data = r.get(key)
                        if data:
                            try:
                                parsed = json.loads(data)
                                premium_data['samples'].append({
                                    'key': key,
                                    'type': 'user_subscription',
                                    'data': parsed
                                })
                            except json.JSONDecodeError:
                                pass
                
                return premium_data
        
        loop = asyncio.get_event_loop()
        premium_data = await loop.run_in_executor(self.redis_manager.executor, _scan_premium)
        
        self.audit_results['data_by_category']['premium_users'] = premium_data
        
        total_premium = premium_data['ip_based_premium'] + premium_data['email_based_premium'] + premium_data['user_subscriptions']
        logger.info(f"Found {total_premium} premium access records ({premium_data['active_premium']} active, {premium_data['expired_premium']} expired)")
    
    async def _audit_email_subscriptions(self):
        """Audit email subscription data"""
        logger.info("Auditing email subscription data...")
        
        # Use existing email stats method
        email_stats = await self.redis_manager.get_email_stats()
        
        def _get_email_samples():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return []
                
                samples = []
                emails = list(r.sscan_iter(self.redis_manager.email_list_key, count=10))
                
                for email in emails[:5]:  # Get 5 samples
                    email_key = f"{self.redis_manager.email_prefix}{email}"
                    data = r.get(email_key)
                    if data:
                        try:
                            parsed = json.loads(data)
                            samples.append({
                                'email': email,
                                'data': parsed
                            })
                        except json.JSONDecodeError:
                            pass
                
                return samples
        
        loop = asyncio.get_event_loop()
        samples = await loop.run_in_executor(self.redis_manager.executor, _get_email_samples)
        
        email_data = {
            **email_stats,
            'samples': samples
        }
        
        self.audit_results['data_by_category']['email_subscriptions'] = email_data
        logger.info(f"Found {email_stats.get('total_emails', 0)} email subscriptions")
    
    async def _audit_usage_tracking(self):
        """Audit usage tracking data"""
        logger.info("Auditing usage tracking data...")
        
        def _scan_usage():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return {}
                
                usage_data = {
                    'ip_daily_counters': 0,
                    'ip_monthly_counters': 0,
                    'email_daily_counters': 0,
                    'email_monthly_counters': 0,
                    'user_daily_counters': 0,
                    'user_monthly_counters': 0,
                    'usage_logs': 0,
                    'global_stats': {},
                    'samples': []
                }
                
                # Count different usage tracking patterns
                for key in r.scan_iter(f"{self.redis_manager.usage_prefix}*"):
                    if ':ip:' in key:
                        if ':daily:' in key:
                            usage_data['ip_daily_counters'] += 1
                        elif ':monthly:' in key:
                            usage_data['ip_monthly_counters'] += 1
                    elif ':email:' in key:
                        if ':daily:' in key:
                            usage_data['email_daily_counters'] += 1
                        elif ':monthly:' in key:
                            usage_data['email_monthly_counters'] += 1
                    elif ':user:' in key:
                        if ':daily:' in key:
                            usage_data['user_daily_counters'] += 1
                        elif ':monthly:' in key:
                            usage_data['user_monthly_counters'] += 1
                    elif ':log:' in key:
                        usage_data['usage_logs'] += 1
                        
                        # Get sample log data
                        if len(usage_data['samples']) < 5:
                            data = r.get(key)
                            if data:
                                try:
                                    parsed = json.loads(data)
                                    usage_data['samples'].append({
                                        'key': key,
                                        'type': 'usage_log',
                                        'data': parsed
                                    })
                                except json.JSONDecodeError:
                                    pass
                
                # Get global usage stats
                stats = r.hgetall(self.redis_manager.usage_stats_key)
                if stats:
                    usage_data['global_stats'] = stats
                
                return usage_data
        
        loop = asyncio.get_event_loop()
        usage_data = await loop.run_in_executor(self.redis_manager.executor, _scan_usage)
        
        self.audit_results['data_by_category']['usage_tracking'] = usage_data
        
        total_usage_keys = (usage_data['ip_daily_counters'] + usage_data['ip_monthly_counters'] + 
                           usage_data['email_daily_counters'] + usage_data['email_monthly_counters'] +
                           usage_data['user_daily_counters'] + usage_data['user_monthly_counters'] +
                           usage_data['usage_logs'])
        logger.info(f"Found {total_usage_keys} usage tracking records")
    
    async def _audit_rate_limiting(self):
        """Audit rate limiting data"""
        logger.info("Auditing rate limiting data...")
        
        def _scan_rate_limits():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return {}
                
                rate_data = {
                    'active_rate_limits': 0,
                    'samples': []
                }
                
                for key in r.scan_iter(f"{self.redis_manager.rate_limit_prefix}*"):
                    rate_data['active_rate_limits'] += 1
                    
                    # Get sample data with TTL
                    if len(rate_data['samples']) < 5:
                        value = r.get(key)
                        ttl = r.ttl(key)
                        if value:
                            rate_data['samples'].append({
                                'key': key,
                                'value': value,
                                'ttl_seconds': ttl,
                                'ip_address': key.replace(self.redis_manager.rate_limit_prefix, '')
                            })
                
                return rate_data
        
        loop = asyncio.get_event_loop()
        rate_data = await loop.run_in_executor(self.redis_manager.executor, _scan_rate_limits)
        
        self.audit_results['data_by_category']['rate_limiting'] = rate_data
        logger.info(f"Found {rate_data['active_rate_limits']} active rate limit records")
    
    async def _audit_cache_data(self):
        """Audit thread cache data"""
        logger.info("Auditing thread cache data...")
        
        def _scan_cache():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return {}
                
                cache_data = {
                    'cached_threads': 0,
                    'total_cache_size_bytes': 0,
                    'samples': []
                }
                
                for key in r.scan_iter(f"{self.redis_manager.cache_prefix}*"):
                    cache_data['cached_threads'] += 1
                    
                    # Get sample data
                    if len(cache_data['samples']) < 3:
                        data = r.get(key)
                        if data:
                            cache_data['total_cache_size_bytes'] += len(data)
                            try:
                                parsed = json.loads(data)
                                # Remove large content for sample
                                if 'tweets' in parsed:
                                    parsed['tweets'] = f"[{len(parsed['tweets'])} tweets]"
                                if 'original_content' in parsed:
                                    parsed['original_content'] = parsed['original_content'][:200] + "..."
                                    
                                cache_data['samples'].append({
                                    'key': key,
                                    'data': parsed,
                                    'size_bytes': len(data)
                                })
                            except json.JSONDecodeError:
                                pass
                
                return cache_data
        
        loop = asyncio.get_event_loop()
        cache_data = await loop.run_in_executor(self.redis_manager.executor, _scan_cache)
        
        self.audit_results['data_by_category']['thread_cache'] = cache_data
        logger.info(f"Found {cache_data['cached_threads']} cached threads")
    
    async def _audit_session_data(self):
        """Audit user session data (if any)"""
        logger.info("Auditing session data...")
        
        def _scan_sessions():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return {}
                
                session_data = {
                    'total_sessions': 0,
                    'samples': []
                }
                
                # Look for session-related keys
                patterns = ['threadr:session:*', 'threadr:jwt:*', 'session:*', 'user:session:*']
                
                for pattern in patterns:
                    for key in r.scan_iter(pattern):
                        session_data['total_sessions'] += 1
                        
                        if len(session_data['samples']) < 3:
                            data = r.get(key)
                            ttl = r.ttl(key)
                            session_data['samples'].append({
                                'key': key,
                                'has_data': bool(data),
                                'ttl_seconds': ttl
                            })
                
                return session_data
        
        loop = asyncio.get_event_loop()
        session_data = await loop.run_in_executor(self.redis_manager.executor, _scan_sessions)
        
        self.audit_results['data_by_category']['sessions'] = session_data
        logger.info(f"Found {session_data['total_sessions']} session records")
    
    async def _analyze_memory_usage(self):
        """Analyze Redis memory usage"""
        logger.info("Analyzing Redis memory usage...")
        
        cache_stats = await self.redis_manager.get_cache_stats()
        self.audit_results['memory_usage'] = cache_stats
        
        if cache_stats.get('available'):
            logger.info(f"Redis memory usage: {cache_stats.get('memory_used', 'unknown')}")
        else:
            logger.warning("Could not retrieve Redis memory stats")
    
    async def _analyze_expirations(self):
        """Analyze key expiration patterns"""
        logger.info("Analyzing key expiration patterns...")
        
        def _scan_expirations():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return {}
                
                exp_data = {
                    'keys_with_ttl': 0,
                    'keys_without_ttl': 0,
                    'expiration_buckets': {
                        'less_than_1_hour': 0,
                        '1_hour_to_1_day': 0,
                        '1_day_to_1_week': 0,
                        '1_week_to_1_month': 0,
                        'more_than_1_month': 0
                    }
                }
                
                # Sample keys to check TTL patterns
                sample_count = 0
                for key in r.scan_iter(count=1000):  # Sample first 1000 keys
                    sample_count += 1
                    if sample_count > 1000:
                        break
                    
                    ttl = r.ttl(key)
                    
                    if ttl == -1:  # No expiration
                        exp_data['keys_without_ttl'] += 1
                    elif ttl > 0:  # Has expiration
                        exp_data['keys_with_ttl'] += 1
                        
                        # Categorize by time bucket
                        if ttl < 3600:  # < 1 hour
                            exp_data['expiration_buckets']['less_than_1_hour'] += 1
                        elif ttl < 86400:  # < 1 day
                            exp_data['expiration_buckets']['1_hour_to_1_day'] += 1
                        elif ttl < 604800:  # < 1 week
                            exp_data['expiration_buckets']['1_day_to_1_week'] += 1
                        elif ttl < 2592000:  # < 1 month
                            exp_data['expiration_buckets']['1_week_to_1_month'] += 1
                        else:
                            exp_data['expiration_buckets']['more_than_1_month'] += 1
                
                exp_data['total_sampled'] = sample_count
                return exp_data
        
        loop = asyncio.get_event_loop()
        exp_data = await loop.run_in_executor(self.redis_manager.executor, _scan_expirations)
        
        self.audit_results['expiration_analysis'] = exp_data
        logger.info(f"Analyzed {exp_data.get('total_sampled', 0)} keys for expiration patterns")
    
    async def _prioritize_migration_data(self):
        """Determine migration priorities based on business importance"""
        logger.info("Analyzing migration priorities...")
        
        priorities = {
            'critical': {
                'description': 'Data loss would impact revenue immediately',
                'categories': ['premium_users'],
                'estimated_records': 0,
                'migration_complexity': 'medium'
            },
            'high': {
                'description': 'Important for user experience and analytics',
                'categories': ['email_subscriptions', 'usage_tracking'],
                'estimated_records': 0,
                'migration_complexity': 'high'
            },
            'medium': {
                'description': 'Performance optimization data',
                'categories': ['thread_cache', 'rate_limiting'],
                'estimated_records': 0,
                'migration_complexity': 'low'
            },
            'low': {
                'description': 'Session data (can be recreated)',
                'categories': ['sessions'],
                'estimated_records': 0,
                'migration_complexity': 'low'
            }
        }
        
        # Calculate estimated records for each priority
        for priority_level, info in priorities.items():
            total_records = 0
            for category in info['categories']:
                category_data = self.audit_results['data_by_category'].get(category, {})
                
                if category == 'premium_users':
                    total_records += (category_data.get('ip_based_premium', 0) + 
                                    category_data.get('email_based_premium', 0) + 
                                    category_data.get('user_subscriptions', 0))
                elif category == 'email_subscriptions':
                    total_records += category_data.get('total_emails', 0)
                elif category == 'usage_tracking':
                    total_records += (category_data.get('ip_daily_counters', 0) + 
                                    category_data.get('ip_monthly_counters', 0) + 
                                    category_data.get('usage_logs', 0))
                elif category == 'thread_cache':
                    total_records += category_data.get('cached_threads', 0)
                elif category == 'rate_limiting':
                    total_records += category_data.get('active_rate_limits', 0)
                elif category == 'sessions':
                    total_records += category_data.get('total_sessions', 0)
            
            priorities[priority_level]['estimated_records'] = total_records
        
        self.audit_results['migration_priorities'] = priorities
        
        for level, info in priorities.items():
            logger.info(f"{level.upper()} priority: {info['estimated_records']} records in {len(info['categories'])} categories")
    
    def save_audit_report(self, filepath: str = None):
        """Save audit results to file"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"redis_audit_report_{timestamp}.json"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.audit_results, f, indent=2, default=str)
            
            logger.info(f"Audit report saved to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving audit report: {e}")
            return None
    
    def print_summary(self):
        """Print a human-readable summary of audit results"""
        print("\n" + "="*80)
        print("REDIS DATA AUDIT SUMMARY")
        print("="*80)
        
        if not self.audit_results['redis_available']:
            print("❌ Redis is not available - cannot perform audit")
            return
        
        print(f"📅 Audit Date: {self.audit_results['timestamp']}")
        print(f"🔑 Total Keys: {self.audit_results['total_keys']:,}")
        
        print("\n📊 KEY DISTRIBUTION:")
        for pattern, count in self.audit_results['key_patterns'].items():
            percentage = (count / self.audit_results['total_keys'] * 100) if self.audit_results['total_keys'] else 0
            print(f"  {pattern:.<20} {count:>8,} keys ({percentage:>5.1f}%)")
        
        print("\n💰 CRITICAL BUSINESS DATA:")
        premium_data = self.audit_results['data_by_category'].get('premium_users', {})
        if premium_data:
            total_premium = (premium_data.get('ip_based_premium', 0) + 
                           premium_data.get('email_based_premium', 0) + 
                           premium_data.get('user_subscriptions', 0))
            print(f"  Premium Users: {total_premium:,} records")
            print(f"    ├─ IP-based: {premium_data.get('ip_based_premium', 0):,}")
            print(f"    ├─ Email-based: {premium_data.get('email_based_premium', 0):,}")
            print(f"    ├─ User Subscriptions: {premium_data.get('user_subscriptions', 0):,}")
            print(f"    ├─ Active: {premium_data.get('active_premium', 0):,}")
            print(f"    └─ Expired: {premium_data.get('expired_premium', 0):,}")
        
        print("\n📧 EMAIL & USAGE DATA:")
        email_data = self.audit_results['data_by_category'].get('email_subscriptions', {})
        if email_data:
            print(f"  Email Subscriptions: {email_data.get('total_emails', 0):,}")
        
        usage_data = self.audit_results['data_by_category'].get('usage_tracking', {})
        if usage_data:
            total_usage = (usage_data.get('ip_daily_counters', 0) + 
                          usage_data.get('ip_monthly_counters', 0) + 
                          usage_data.get('usage_logs', 0))
            print(f"  Usage Records: {total_usage:,}")
        
        print("\n🚀 MIGRATION PRIORITIES:")
        for level, info in self.audit_results.get('migration_priorities', {}).items():
            print(f"  {level.upper():.<12} {info['estimated_records']:>8,} records ({info['migration_complexity']} complexity)")
        
        print("\n💾 MEMORY USAGE:")
        memory_data = self.audit_results.get('memory_usage', {})
        if memory_data.get('available'):
            print(f"  Used Memory: {memory_data.get('memory_used', 'unknown')}")
            print(f"  Cache Entries: {memory_data.get('cache_entries', 0):,}")
            print(f"  Rate Limit Entries: {memory_data.get('rate_limit_entries', 0):,}")
        else:
            print("  Memory stats unavailable")
        
        print("\n" + "="*80)

async def main():
    """Main function to run Redis audit"""
    print("🔍 Starting Redis Data Audit for PostgreSQL Migration...")
    
    audit_tool = RedisAuditTool()
    
    try:
        # Run full audit
        results = await audit_tool.run_full_audit()
        
        # Print summary
        audit_tool.print_summary()
        
        # Save detailed report
        report_file = audit_tool.save_audit_report()
        
        print(f"\n✅ Audit completed! Detailed report saved to: {report_file}")
        print("\n📝 Next steps:")
        print("1. Review the detailed audit report")
        print("2. Run the migration mapping script")
        print("3. Execute the data migration with validation")
        
    except KeyboardInterrupt:
        print("\n❌ Audit interrupted by user")
    except Exception as e:
        print(f"\n❌ Audit failed: {e}")
        logger.error("Audit failed", exc_info=True)
    
    finally:
        # Clean up
        if audit_tool.redis_manager:
            audit_tool.redis_manager.close()

if __name__ == "__main__":
    asyncio.run(main())