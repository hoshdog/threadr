"""
Threadr Pricing Configuration
Centralized configuration for subscription tiers, features, and Stripe integration
"""

import os
from typing import Dict, List, Any
from enum import Enum

class SubscriptionTier(Enum):
    """Subscription tier levels for easy comparison"""
    FREE = 0
    STARTER = 1
    PRO = 2
    TEAM = 3

class FeatureFlag(Enum):
    """Available features across subscription tiers"""
    BASIC_THREADS = "basic_threads"
    BASIC_ANALYTICS = "basic_analytics"
    EMAIL_SUPPORT = "email_support"
    UNLIMITED_THREADS = "unlimited_threads"
    ADVANCED_ANALYTICS = "advanced_analytics"
    PREMIUM_TEMPLATES = "premium_templates"
    PRIORITY_SUPPORT = "priority_support"
    CUSTOM_SCHEDULING = "custom_scheduling"
    EXPORT_THREADS = "export_threads"
    TEAM_COLLABORATION = "team_collaboration"
    ADMIN_DASHBOARD = "admin_dashboard"
    DEDICATED_SUPPORT = "dedicated_support"
    CUSTOM_BRANDING = "custom_branding"
    API_ACCESS = "api_access"
    BULK_PROCESSING = "bulk_processing"
    ANALYTICS_EXPORT = "analytics_export"
    WHITE_LABELING = "white_labeling"

# Core pricing configuration
PRICING_CONFIG = {
    "free": {
        "name": "Free",
        "display_name": "Free",
        "tier_level": SubscriptionTier.FREE.value,
        "monthly_price": 0,
        "annual_price": 0,
        "thread_limit": 5,
        "daily_limit": 5,
        "monthly_limit": 20,
        "features": [
            FeatureFlag.BASIC_THREADS.value
        ],
        "description": "Perfect for trying out Threadr",
        "stripe_price_ids": {
            "monthly": None,
            "annual": None
        }
    },
    "threadr_starter": {
        "name": "Threadr Starter",
        "display_name": "Starter",
        "tier_level": SubscriptionTier.STARTER.value,
        "monthly_price": 999,  # $9.99
        "annual_price": 9590,  # $95.90 (20% discount)
        "thread_limit": 100,
        "daily_limit": -1,  # Unlimited daily
        "monthly_limit": 100,
        "features": [
            FeatureFlag.BASIC_THREADS.value,
            FeatureFlag.BASIC_ANALYTICS.value,
            FeatureFlag.EMAIL_SUPPORT.value,
            FeatureFlag.PREMIUM_TEMPLATES.value
        ],
        "description": "Great for individuals and small creators",
        "stripe_price_ids": {
            "monthly": os.getenv("STRIPE_THREADR_STARTER_MONTHLY_PRICE_ID"),
            "annual": os.getenv("STRIPE_THREADR_STARTER_ANNUAL_PRICE_ID")
        }
    },
    "threadr_pro": {
        "name": "Threadr Pro",
        "display_name": "Pro",
        "tier_level": SubscriptionTier.PRO.value,
        "monthly_price": 1999,  # $19.99
        "annual_price": 19190,  # $191.90 (20% discount)
        "thread_limit": -1,  # Unlimited
        "daily_limit": -1,  # Unlimited
        "monthly_limit": -1,  # Unlimited
        "features": [
            FeatureFlag.UNLIMITED_THREADS.value,
            FeatureFlag.ADVANCED_ANALYTICS.value,
            FeatureFlag.PREMIUM_TEMPLATES.value,
            FeatureFlag.PRIORITY_SUPPORT.value,
            FeatureFlag.CUSTOM_SCHEDULING.value,
            FeatureFlag.EXPORT_THREADS.value
        ],
        "description": "Perfect for content creators and marketers",
        "stripe_price_ids": {
            "monthly": os.getenv("STRIPE_THREADR_PRO_MONTHLY_PRICE_ID"),
            "annual": os.getenv("STRIPE_THREADR_PRO_ANNUAL_PRICE_ID")
        }
    },
    "threadr_team": {
        "name": "Threadr Team",
        "display_name": "Team",
        "tier_level": SubscriptionTier.TEAM.value,
        "monthly_price": 4999,  # $49.99
        "annual_price": 47990,  # $479.90 (20% discount)
        "thread_limit": -1,  # Unlimited
        "daily_limit": -1,  # Unlimited
        "monthly_limit": -1,  # Unlimited
        "features": [
            FeatureFlag.UNLIMITED_THREADS.value,
            FeatureFlag.TEAM_COLLABORATION.value,
            FeatureFlag.ADMIN_DASHBOARD.value,
            FeatureFlag.DEDICATED_SUPPORT.value,
            FeatureFlag.CUSTOM_BRANDING.value,
            FeatureFlag.API_ACCESS.value,
            FeatureFlag.BULK_PROCESSING.value,
            FeatureFlag.ANALYTICS_EXPORT.value,
            FeatureFlag.WHITE_LABELING.value
        ],
        "description": "Built for teams and agencies",
        "stripe_price_ids": {
            "monthly": os.getenv("STRIPE_THREADR_TEAM_MONTHLY_PRICE_ID"),
            "annual": os.getenv("STRIPE_THREADR_TEAM_ANNUAL_PRICE_ID")
        }
    }
}

def get_plan_by_name(plan_name: str) -> Dict[str, Any]:
    """Get plan configuration by name"""
    return PRICING_CONFIG.get(plan_name, PRICING_CONFIG["free"])

def get_plan_by_tier_level(tier_level: int) -> Dict[str, Any]:
    """Get plan configuration by tier level"""
    for plan_name, config in PRICING_CONFIG.items():
        if config["tier_level"] == tier_level:
            return config
    return PRICING_CONFIG["free"]

def get_plan_by_price_id(price_id: str) -> tuple[str, bool]:
    """Get plan name and billing frequency by Stripe price ID
    
    Returns:
        tuple: (plan_name, is_annual)
    """
    if not price_id:
        return "free", False
    
    for plan_name, config in PRICING_CONFIG.items():
        stripe_ids = config.get("stripe_price_ids", {})
        if price_id == stripe_ids.get("monthly"):
            return plan_name, False
        elif price_id == stripe_ids.get("annual"):
            return plan_name, True
    
    return "unknown", False

def has_feature(plan_name: str, feature: FeatureFlag) -> bool:
    """Check if a plan has a specific feature"""
    plan = get_plan_by_name(plan_name)
    return feature.value in plan.get("features", [])

def can_access_feature(tier_level: int, feature: FeatureFlag) -> bool:
    """Check if a tier level can access a specific feature"""
    plan = get_plan_by_tier_level(tier_level)
    return feature.value in plan.get("features", [])

def get_thread_limit(plan_name: str) -> int:
    """Get thread limit for a plan (-1 for unlimited)"""
    plan = get_plan_by_name(plan_name)
    return plan.get("thread_limit", 5)

def get_all_plans() -> Dict[str, Any]:
    """Get all available plans"""
    return PRICING_CONFIG

def get_public_plans() -> Dict[str, Any]:
    """Get plans suitable for public display (excludes sensitive info)"""
    public_plans = {}
    for plan_name, config in PRICING_CONFIG.items():
        public_plans[plan_name] = {
            "name": config["name"],
            "display_name": config["display_name"],
            "tier_level": config["tier_level"],
            "monthly_price": config["monthly_price"],
            "annual_price": config["annual_price"],
            "thread_limit": config["thread_limit"],
            "features": config["features"],
            "description": config["description"]
        }
    return public_plans

def validate_stripe_configuration() -> Dict[str, List[str]]:
    """Validate that all required Stripe price IDs are configured"""
    missing_config = {"monthly": [], "annual": []}
    
    for plan_name, config in PRICING_CONFIG.items():
        if plan_name == "free":
            continue
            
        stripe_ids = config.get("stripe_price_ids", {})
        
        if not stripe_ids.get("monthly"):
            missing_config["monthly"].append(plan_name)
        if not stripe_ids.get("annual"):
            missing_config["annual"].append(plan_name)
    
    return missing_config

# Environment variable mapping for easy setup
REQUIRED_ENV_VARS = [
    "STRIPE_THREADR_STARTER_MONTHLY_PRICE_ID",
    "STRIPE_THREADR_STARTER_ANNUAL_PRICE_ID",
    "STRIPE_THREADR_PRO_MONTHLY_PRICE_ID", 
    "STRIPE_THREADR_PRO_ANNUAL_PRICE_ID",
    "STRIPE_THREADR_TEAM_MONTHLY_PRICE_ID",
    "STRIPE_THREADR_TEAM_ANNUAL_PRICE_ID",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET"
]

def check_required_env_vars() -> List[str]:
    """Check which required environment variables are missing"""
    missing_vars = []
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing_vars.append(var)
    return missing_vars