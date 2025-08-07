#!/usr/bin/env python3
"""
Redis to PostgreSQL Migration Mapping
Defines how Redis data structures map to PostgreSQL schema for Threadr
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class MigrationMapping:
    """Defines how a Redis data pattern maps to PostgreSQL"""
    redis_pattern: str
    postgres_table: str
    priority: str  # critical, high, medium, low
    complexity: str  # low, medium, high
    description: str
    transform_function: str  # Name of transformation function
    validation_rules: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # Other mappings this depends on
    estimated_volume: int = 0
    
class RedisToPostgresMigrationMapper:
    """Maps Redis data structures to PostgreSQL tables"""
    
    def __init__(self):
        self.mappings = self._define_mappings()
        self.transformers = self._create_transformers()
    
    def _define_mappings(self) -> List[MigrationMapping]:
        """Define all Redis to PostgreSQL mappings"""
        return [
            # CRITICAL: Premium Access (Revenue Impact)
            MigrationMapping(
                redis_pattern="threadr:premium:ip:*",
                postgres_table="subscriptions",
                priority="critical",
                complexity="medium",
                description="Legacy IP-based premium access records",
                transform_function="transform_ip_premium_to_subscription",
                validation_rules=[
                    "expires_at_is_valid_datetime",
                    "payment_info_exists",
                    "ip_address_is_valid"
                ]
            ),
            
            MigrationMapping(
                redis_pattern="threadr:premium:email:*",
                postgres_table="subscriptions",
                priority="critical",
                complexity="medium",
                description="Legacy email-based premium access records",
                transform_function="transform_email_premium_to_subscription",
                validation_rules=[
                    "expires_at_is_valid_datetime",
                    "email_is_valid",
                    "payment_info_exists"
                ]
            ),
            
            MigrationMapping(
                redis_pattern="threadr:subscription:user:*",
                postgres_table="subscriptions",
                priority="critical",
                complexity="low",
                description="Modern user subscription records",
                transform_function="transform_user_subscription",
                validation_rules=[
                    "subscription_id_exists",
                    "plan_name_is_valid",
                    "status_is_valid"
                ]
            ),
            
            # HIGH: User & Email Data
            MigrationMapping(
                redis_pattern="threadr:email:*",
                postgres_table="users",
                priority="high",
                complexity="medium",
                description="Email subscription data -> user records",
                transform_function="transform_email_to_user",
                validation_rules=[
                    "email_is_valid",
                    "subscribed_at_exists"
                ]
            ),
            
            MigrationMapping(
                redis_pattern="threadr:emails:list",
                postgres_table="users",
                priority="high",
                complexity="low",
                description="Email list for cross-validation",
                transform_function="validate_email_list",
                validation_rules=["all_emails_processed"]
            ),
            
            # HIGH: Usage Tracking Data
            MigrationMapping(
                redis_pattern="threadr:usage:ip:*:daily:*",
                postgres_table="usage_tracking",
                priority="high",
                complexity="high",
                description="IP-based daily usage counters",
                transform_function="transform_ip_daily_usage",
                validation_rules=[
                    "ip_address_is_valid",
                    "date_is_valid",
                    "count_is_positive"
                ]
            ),
            
            MigrationMapping(
                redis_pattern="threadr:usage:ip:*:monthly:*",
                postgres_table="usage_tracking",
                priority="high",
                complexity="high",
                description="IP-based monthly usage counters",
                transform_function="transform_ip_monthly_usage",
                validation_rules=[
                    "ip_address_is_valid",
                    "month_is_valid",
                    "count_is_positive"
                ]
            ),
            
            MigrationMapping(
                redis_pattern="threadr:usage:email:*:daily:*",
                postgres_table="usage_tracking",
                priority="high",
                complexity="high",
                description="Email-based daily usage counters",
                transform_function="transform_email_daily_usage",
                validation_rules=[
                    "email_is_valid",
                    "date_is_valid",
                    "count_is_positive"
                ],
                dependencies=["threadr:email:*"]  # Needs email->user mapping first
            ),
            
            MigrationMapping(
                redis_pattern="threadr:usage:user:*:daily:*",
                postgres_table="usage_tracking",
                priority="high",
                complexity="medium",
                description="User-based daily usage counters",
                transform_function="transform_user_daily_usage",
                validation_rules=[
                    "user_id_is_valid",
                    "date_is_valid",
                    "count_is_positive"
                ]
            ),
            
            MigrationMapping(
                redis_pattern="threadr:usage:log:*",
                postgres_table="usage_tracking",
                priority="high",
                complexity="medium",
                description="Detailed usage logs",
                transform_function="transform_usage_log",
                validation_rules=[
                    "timestamp_is_valid",
                    "client_ip_exists",
                    "log_data_is_valid"
                ]
            ),
            
            MigrationMapping(
                redis_pattern="threadr:usage:stats",
                postgres_table="analytics_timeseries",
                priority="high",
                complexity="medium",
                description="Global usage statistics",
                transform_function="transform_global_stats",
                validation_rules=["stats_data_is_valid"]
            ),
            
            # MEDIUM: Performance Data (Can be recreated)
            MigrationMapping(
                redis_pattern="threadr:cache:*",
                postgres_table="threads",
                priority="medium",
                complexity="low",
                description="Cached thread responses (can be regenerated)",
                transform_function="transform_cached_thread",
                validation_rules=[
                    "thread_data_is_valid",
                    "tweets_array_exists"
                ]
            ),
            
            # LOW: Session/Rate Limiting Data (Temporary)
            MigrationMapping(
                redis_pattern="threadr:ratelimit:*",
                postgres_table=None,  # Don't migrate - temporary data
                priority="low",
                complexity="low",
                description="Rate limiting counters (temporary, don't migrate)",
                transform_function="skip_rate_limiting",
                validation_rules=[]
            ),
            
            MigrationMapping(
                redis_pattern="threadr:session:*",
                postgres_table="user_sessions",
                priority="low",
                complexity="medium",
                description="User session data",
                transform_function="transform_user_session",
                validation_rules=[
                    "session_token_exists",
                    "user_id_is_valid",
                    "expires_at_exists"
                ]
            )
        ]
    
    def _create_transformers(self) -> Dict[str, Callable]:
        """Create transformation functions for each mapping"""
        return {
            'transform_ip_premium_to_subscription': self._transform_ip_premium_to_subscription,
            'transform_email_premium_to_subscription': self._transform_email_premium_to_subscription,
            'transform_user_subscription': self._transform_user_subscription,
            'transform_email_to_user': self._transform_email_to_user,
            'validate_email_list': self._validate_email_list,
            'transform_ip_daily_usage': self._transform_ip_daily_usage,
            'transform_ip_monthly_usage': self._transform_ip_monthly_usage,
            'transform_email_daily_usage': self._transform_email_daily_usage,
            'transform_user_daily_usage': self._transform_user_daily_usage,
            'transform_usage_log': self._transform_usage_log,
            'transform_global_stats': self._transform_global_stats,
            'transform_cached_thread': self._transform_cached_thread,
            'skip_rate_limiting': self._skip_rate_limiting,
            'transform_user_session': self._transform_user_session
        }
    
    def get_migration_plan(self) -> Dict[str, Any]:
        """Generate comprehensive migration plan"""
        # Sort by priority and dependencies
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_mappings = sorted(self.mappings, key=lambda m: (priority_order[m.priority], len(m.dependencies)))
        
        return {
            'total_mappings': len(self.mappings),
            'migration_phases': {
                'phase_1_critical': [m for m in sorted_mappings if m.priority == 'critical'],
                'phase_2_high': [m for m in sorted_mappings if m.priority == 'high'],
                'phase_3_medium': [m for m in sorted_mappings if m.priority == 'medium'],
                'phase_4_low': [m for m in sorted_mappings if m.priority == 'low']
            },
            'table_targets': self._get_table_mapping(),
            'validation_requirements': self._get_validation_requirements(),
            'dependency_graph': self._build_dependency_graph()
        }
    
    def _get_table_mapping(self) -> Dict[str, List[str]]:
        """Get which Redis patterns map to which PostgreSQL tables"""
        table_map = {}
        for mapping in self.mappings:
            if mapping.postgres_table:
                if mapping.postgres_table not in table_map:
                    table_map[mapping.postgres_table] = []
                table_map[mapping.postgres_table].append(mapping.redis_pattern)
        return table_map
    
    def _get_validation_requirements(self) -> Dict[str, List[str]]:
        """Get all validation rules organized by table"""
        validations = {}
        for mapping in self.mappings:
            if mapping.postgres_table and mapping.validation_rules:
                if mapping.postgres_table not in validations:
                    validations[mapping.postgres_table] = []
                validations[mapping.postgres_table].extend(mapping.validation_rules)
        
        # Remove duplicates
        for table in validations:
            validations[table] = list(set(validations[table]))
        
        return validations
    
    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """Build dependency graph for migration ordering"""
        graph = {}
        for mapping in self.mappings:
            graph[mapping.redis_pattern] = mapping.dependencies
        return graph
    
    # TRANSFORMATION FUNCTIONS
    
    def _transform_ip_premium_to_subscription(self, redis_key: str, redis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform IP-based premium access to subscription record"""
        ip_address = redis_key.split(':')[-1]  # Extract IP from key
        
        # Parse the premium data
        granted_at = datetime.fromisoformat(redis_data.get('granted_at', datetime.now().isoformat()))
        expires_at = datetime.fromisoformat(redis_data.get('expires_at', 
                                                         (datetime.now() + timedelta(days=30)).isoformat()))
        
        return {
            'id': str(uuid.uuid4()),
            'user_id': None,  # Will need to link to user later or create anonymous user
            'team_id': None,
            'stripe_subscription_id': None,  # Legacy data
            'stripe_customer_id': f"legacy_ip_{ip_address}",
            'stripe_price_id': 'legacy_premium',
            'stripe_product_id': 'legacy_premium',
            'status': 'active' if expires_at > datetime.now() else 'canceled',
            'plan_name': redis_data.get('plan', 'legacy_premium'),
            'billing_cycle': 'one_time',
            'amount_cents': 499,  # $4.99 legacy price
            'currency': 'USD',
            'current_period_start': granted_at,
            'current_period_end': expires_at,
            'cancel_at_period_end': True,  # One-time payment
            'premium_expires_at': expires_at,
            'metadata': {
                'source': 'redis_ip_premium',
                'original_key': redis_key,
                'ip_address': ip_address,
                'client_ip': redis_data.get('client_ip', ip_address),
                'email': redis_data.get('email'),
                'payment_info': redis_data.get('payment_info', {}),
                'migration_timestamp': datetime.now().isoformat()
            },
            'created_at': granted_at,
            'updated_at': datetime.now()
        }
    
    def _transform_email_premium_to_subscription(self, redis_key: str, redis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform email-based premium access to subscription record"""
        email = redis_key.split(':')[-1]  # Extract email from key
        
        granted_at = datetime.fromisoformat(redis_data.get('granted_at', datetime.now().isoformat()))
        expires_at = datetime.fromisoformat(redis_data.get('expires_at', 
                                                         (datetime.now() + timedelta(days=30)).isoformat()))
        
        return {
            'id': str(uuid.uuid4()),
            'user_id': None,  # Will link when user is created from email data
            'team_id': None,
            'stripe_subscription_id': None,
            'stripe_customer_id': f"legacy_email_{email.replace('@', '_at_')}",
            'stripe_price_id': 'legacy_premium',
            'stripe_product_id': 'legacy_premium',
            'status': 'active' if expires_at > datetime.now() else 'canceled',
            'plan_name': redis_data.get('plan', 'legacy_premium'),
            'billing_cycle': 'one_time',
            'amount_cents': 499,
            'currency': 'USD',
            'current_period_start': granted_at,
            'current_period_end': expires_at,
            'cancel_at_period_end': True,
            'premium_expires_at': expires_at,
            'metadata': {
                'source': 'redis_email_premium',
                'original_key': redis_key,
                'email': email,
                'client_ip': redis_data.get('client_ip'),
                'payment_info': redis_data.get('payment_info', {}),
                'migration_timestamp': datetime.now().isoformat()
            },
            'created_at': granted_at,
            'updated_at': datetime.now()
        }
    
    def _transform_user_subscription(self, redis_key: str, redis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform modern user subscription data"""
        user_id = redis_key.split(':')[-1]
        
        current_period_start = redis_data.get('current_period_start')
        if isinstance(current_period_start, str):
            current_period_start = datetime.fromisoformat(current_period_start)
        
        current_period_end = redis_data.get('current_period_end')
        if isinstance(current_period_end, str):
            current_period_end = datetime.fromisoformat(current_period_end)
        
        return {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'team_id': None,
            'stripe_subscription_id': redis_data.get('subscription_id'),
            'stripe_customer_id': redis_data.get('customer_id', f"user_{user_id}"),
            'stripe_price_id': redis_data.get('price_id', 'unknown'),
            'stripe_product_id': redis_data.get('product_id', 'threadr_pro'),
            'status': redis_data.get('status', 'active'),
            'plan_name': redis_data.get('plan_name', 'pro'),
            'billing_cycle': 'yearly' if redis_data.get('is_annual', False) else 'monthly',
            'amount_cents': redis_data.get('monthly_price', 1999) if not redis_data.get('is_annual') else redis_data.get('annual_price', 19190),
            'currency': 'USD',
            'current_period_start': current_period_start,
            'current_period_end': current_period_end,
            'cancel_at_period_end': redis_data.get('cancel_at_period_end', False),
            'premium_expires_at': current_period_end,
            'metadata': {
                'source': 'redis_user_subscription',
                'original_key': redis_key,
                'tier_level': redis_data.get('tier_level', 1),
                'thread_limit': redis_data.get('thread_limit', -1),
                'features': redis_data.get('features', []),
                'migration_timestamp': datetime.now().isoformat()
            },
            'created_at': current_period_start or datetime.now(),
            'updated_at': datetime.now()
        }
    
    def _transform_email_to_user(self, redis_key: str, redis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform email subscription data to user record"""
        email = redis_key.split(':')[-1]
        
        subscribed_at = redis_data.get('subscribed_at')
        if isinstance(subscribed_at, str):
            subscribed_at = datetime.fromisoformat(subscribed_at)
        else:
            subscribed_at = datetime.now()
        
        return {
            'id': str(uuid.uuid4()),
            'email': email,
            'password_hash': '',  # Will need to be set when user first logs in
            'role': 'user',
            'status': 'active',
            'login_count': 0,
            'failed_login_attempts': 0,
            'is_email_verified': False,  # Assume not verified initially
            'metadata': {
                'source': 'redis_email_subscription',
                'original_key': redis_key,
                'subscription_source': redis_data.get('source', 'unknown'),
                'user_agent': redis_data.get('user_agent'),
                'referrer': redis_data.get('referrer'),
                'utm_source': redis_data.get('utm_source'),
                'migration_timestamp': datetime.now().isoformat()
            },
            'created_at': subscribed_at,
            'updated_at': datetime.now()
        }
    
    def _transform_ip_daily_usage(self, redis_key: str, redis_value: str) -> Dict[str, Any]:
        """Transform IP daily usage counter"""
        parts = redis_key.split(':')
        ip_address = parts[3]  # threadr:usage:ip:{IP}:daily:{date}
        date_str = parts[5]
        
        return {
            'id': str(uuid.uuid4()),
            'user_id': None,  # Will need to link if user exists for this IP
            'ip_address': ip_address,
            'endpoint': '/api/generate',
            'action': 'generate_thread',
            'daily_count': int(redis_value),
            'monthly_count': 0,  # Will be calculated from monthly keys
            'date_bucket': datetime.strptime(date_str, '%Y-%m-%d').date(),
            'month_bucket': datetime.strptime(date_str, '%Y-%m-%d').replace(day=1).date(),
            'metadata': {
                'source': 'redis_ip_daily_usage',
                'original_key': redis_key
            },
            'first_request_at': datetime.strptime(date_str, '%Y-%m-%d'),
            'last_request_at': datetime.strptime(date_str, '%Y-%m-%d') + timedelta(hours=23, minutes=59)
        }
    
    def _transform_ip_monthly_usage(self, redis_key: str, redis_value: str) -> Dict[str, Any]:
        """Transform IP monthly usage counter"""
        parts = redis_key.split(':')
        ip_address = parts[3]  # threadr:usage:ip:{IP}:monthly:{month}
        month_str = parts[5]  # YYYY-MM
        
        month_date = datetime.strptime(f"{month_str}-01", '%Y-%m-%d')
        
        return {
            'id': str(uuid.uuid4()),
            'user_id': None,
            'ip_address': ip_address,
            'endpoint': '/api/generate',
            'action': 'generate_thread',
            'daily_count': 0,
            'monthly_count': int(redis_value),
            'date_bucket': month_date.date(),
            'month_bucket': month_date.replace(day=1).date(),
            'metadata': {
                'source': 'redis_ip_monthly_usage',
                'original_key': redis_key
            },
            'first_request_at': month_date,
            'last_request_at': month_date.replace(day=28) + timedelta(days=4)  # End of month approx
        }
    
    def _transform_email_daily_usage(self, redis_key: str, redis_value: str) -> Dict[str, Any]:
        """Transform email daily usage counter"""
        parts = redis_key.split(':')
        email = parts[3]
        date_str = parts[5]
        
        return {
            'id': str(uuid.uuid4()),
            'user_id': None,  # Will link to user created from email
            'ip_address': None,
            'endpoint': '/api/generate',
            'action': 'generate_thread',
            'daily_count': int(redis_value),
            'monthly_count': 0,
            'date_bucket': datetime.strptime(date_str, '%Y-%m-%d').date(),
            'month_bucket': datetime.strptime(date_str, '%Y-%m-%d').replace(day=1).date(),
            'user_agent': None,
            'metadata': {
                'source': 'redis_email_daily_usage',
                'original_key': redis_key,
                'email': email
            },
            'first_request_at': datetime.strptime(date_str, '%Y-%m-%d'),
            'last_request_at': datetime.strptime(date_str, '%Y-%m-%d') + timedelta(hours=23, minutes=59)
        }
    
    def _transform_user_daily_usage(self, redis_key: str, redis_value: str) -> Dict[str, Any]:
        """Transform user daily usage counter"""
        parts = redis_key.split(':')
        user_id = parts[3]
        date_str = parts[5]
        
        return {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'ip_address': None,
            'endpoint': '/api/generate',
            'action': 'generate_thread',
            'daily_count': int(redis_value),
            'monthly_count': 0,
            'date_bucket': datetime.strptime(date_str, '%Y-%m-%d').date(),
            'month_bucket': datetime.strptime(date_str, '%Y-%m-%d').replace(day=1).date(),
            'metadata': {
                'source': 'redis_user_daily_usage',
                'original_key': redis_key
            },
            'first_request_at': datetime.strptime(date_str, '%Y-%m-%d'),
            'last_request_at': datetime.strptime(date_str, '%Y-%m-%d') + timedelta(hours=23, minutes=59)
        }
    
    def _transform_usage_log(self, redis_key: str, redis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform detailed usage log"""
        timestamp_str = redis_key.split(':')[-1]  # Unix timestamp
        timestamp = datetime.fromtimestamp(float(timestamp_str))
        
        return {
            'id': str(uuid.uuid4()),
            'user_id': None,  # Will link if user exists
            'ip_address': redis_data.get('client_ip'),
            'endpoint': '/api/generate',
            'action': 'generate_thread',
            'daily_count': 1,
            'monthly_count': 1,
            'date_bucket': timestamp.date(),
            'month_bucket': timestamp.replace(day=1).date(),
            'user_agent': None,
            'metadata': {
                'source': 'redis_usage_log',
                'original_key': redis_key,
                'original_data': redis_data
            },
            'first_request_at': timestamp,
            'last_request_at': timestamp
        }
    
    def _transform_global_stats(self, redis_key: str, redis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform global usage statistics to time series data"""
        records = []
        
        for metric_key, value in redis_data.items():
            if metric_key.startswith('threads_'):
                if metric_key == 'total_threads':
                    continue  # Skip total, use dated metrics
                
                # Extract date from metric name
                date_str = metric_key.replace('threads_', '')
                try:
                    metric_date = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    continue
                
                records.append({
                    'id': str(uuid.uuid4()),
                    'user_id': None,  # Global metric
                    'thread_id': None,
                    'metric_name': 'daily_threads',
                    'metric_value': float(value),
                    'timestamp': metric_date,
                    'period_type': 'day',
                    'date_bucket': metric_date.date(),
                    'metadata': {
                        'source': 'redis_global_stats',
                        'original_key': redis_key,
                        'original_metric': metric_key
                    }
                })
        
        return records
    
    def _transform_cached_thread(self, redis_key: str, redis_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Transform cached thread data (optional migration)"""
        # Extract URL or text hash from cache key
        cache_suffix = redis_key.replace('threadr:cache:', '')
        
        if not redis_data.get('tweets'):
            return None  # Invalid thread data
        
        # Only migrate if this represents a complete, valid thread
        return {
            'id': str(uuid.uuid4()),
            'user_id': None,  # Anonymous cached thread
            'team_id': None,
            'title': redis_data.get('title', 'Migrated Thread'),
            'original_content': redis_data.get('original_content', ''),
            'tweets': json.dumps(redis_data.get('tweets', [])),
            'source_url': redis_data.get('source_url') if cache_suffix.startswith('url:') else None,
            'source_type': 'url' if cache_suffix.startswith('url:') else 'text',
            'ai_model': redis_data.get('ai_model', 'gpt-3.5-turbo'),
            'generation_time_ms': redis_data.get('generation_time_ms'),
            'content_length': len(redis_data.get('original_content', '')),
            'metadata': {
                'source': 'redis_cached_thread',
                'original_key': redis_key,
                'cached_at': redis_data.get('_cached_at'),
                'migration_timestamp': datetime.now().isoformat()
            },
            'created_at': datetime.fromtimestamp(redis_data.get('_cached_at', datetime.now().timestamp())),
            'updated_at': datetime.now()
        }
    
    def _transform_user_session(self, redis_key: str, redis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform user session data"""
        return {
            'id': str(uuid.uuid4()),
            'user_id': redis_data.get('user_id'),
            'session_token': redis_data.get('session_token'),
            'refresh_token': redis_data.get('refresh_token'),
            'device_id': redis_data.get('device_id'),
            'ip_address': redis_data.get('ip_address'),
            'user_agent': redis_data.get('user_agent'),
            'device_name': redis_data.get('device_name'),
            'is_active': redis_data.get('is_active', True),
            'is_remember_me': redis_data.get('is_remember_me', False),
            'expires_at': datetime.fromisoformat(redis_data.get('expires_at', 
                                                              (datetime.now() + timedelta(hours=24)).isoformat())),
            'created_at': datetime.fromisoformat(redis_data.get('created_at', datetime.now().isoformat())),
            'last_used_at': datetime.fromisoformat(redis_data.get('last_used_at', datetime.now().isoformat()))
        }
    
    # Skip functions
    def _validate_email_list(self, redis_key: str, redis_data: Any) -> Dict[str, Any]:
        """Validate email list (used for cross-checking)"""
        return {'validation': True, 'skip': True}
    
    def _skip_rate_limiting(self, redis_key: str, redis_data: Any) -> Dict[str, Any]:
        """Skip rate limiting data (temporary)"""
        return {'skip': True, 'reason': 'temporary_data'}
    
    def export_mapping_documentation(self, filepath: str = None) -> str:
        """Export comprehensive mapping documentation"""
        if not filepath:
            filepath = f"redis_postgres_mapping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        plan = self.get_migration_plan()
        documentation = {
            'mapping_overview': {
                'total_patterns': len(self.mappings),
                'target_tables': list(plan['table_targets'].keys()),
                'migration_phases': len(plan['migration_phases']),
                'generated_at': datetime.now().isoformat()
            },
            'detailed_mappings': [
                {
                    'redis_pattern': m.redis_pattern,
                    'postgres_table': m.postgres_table,
                    'priority': m.priority,
                    'complexity': m.complexity,
                    'description': m.description,
                    'validation_rules': m.validation_rules,
                    'dependencies': m.dependencies
                }
                for m in self.mappings
            ],
            'migration_plan': plan,
            'transformation_functions': list(self.transformers.keys()),
            'data_flow': self._generate_data_flow_diagram()
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(documentation, f, indent=2, default=str)
            
            logger.info(f"Migration mapping documentation saved to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving mapping documentation: {e}")
            return None
    
    def _generate_data_flow_diagram(self) -> Dict[str, Any]:
        """Generate data flow visualization data"""
        tables = {}
        for mapping in self.mappings:
            if mapping.postgres_table:
                if mapping.postgres_table not in tables:
                    tables[mapping.postgres_table] = {
                        'sources': [],
                        'total_patterns': 0,
                        'priorities': set()
                    }
                
                tables[mapping.postgres_table]['sources'].append({
                    'pattern': mapping.redis_pattern,
                    'priority': mapping.priority,
                    'complexity': mapping.complexity
                })
                tables[mapping.postgres_table]['total_patterns'] += 1
                tables[mapping.postgres_table]['priorities'].add(mapping.priority)
        
        # Convert sets to lists for JSON serialization
        for table_data in tables.values():
            table_data['priorities'] = list(table_data['priorities'])
        
        return {
            'tables': tables,
            'flow_summary': f"Redis ({len(self.mappings)} patterns) → PostgreSQL ({len(tables)} tables)"
        }

# Example usage and testing
if __name__ == "__main__":
    mapper = RedisToPostgresMigrationMapper()
    
    print("🗺️ Redis to PostgreSQL Migration Mapping")
    print("=" * 50)
    
    plan = mapper.get_migration_plan()
    
    print(f"\n📊 Migration Overview:")
    print(f"  Total Patterns: {plan['total_mappings']}")
    print(f"  Target Tables: {len(plan['table_targets'])}")
    
    print(f"\n🎯 Migration Phases:")
    for phase, mappings in plan['migration_phases'].items():
        print(f"  {phase.replace('_', ' ').title()}: {len(mappings)} mappings")
    
    print(f"\n📋 Target Tables:")
    for table, patterns in plan['table_targets'].items():
        print(f"  {table}: {len(patterns)} Redis patterns")
    
    # Export documentation
    doc_file = mapper.export_mapping_documentation()
    if doc_file:
        print(f"\n✅ Documentation exported to: {doc_file}")