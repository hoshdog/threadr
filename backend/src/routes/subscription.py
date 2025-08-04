#!/usr/bin/env python3
"""
Subscription Management Routes for Threadr
Handles Stripe subscription lifecycle and premium access management
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import stripe
import os
import logging
from datetime import datetime, timedelta
import json

# Import dependencies
try:
    from ..core.redis_manager import get_redis_manager
    from ..middleware.auth import get_current_user_optional, get_current_user
    from ..services.auth.auth_service import AuthService
except ImportError:
    from core.redis_manager import get_redis_manager
    from middleware.auth import get_current_user_optional, get_current_user
    from services.auth.auth_service import AuthService

# Configure logging
logger = logging.getLogger(__name__)

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Subscription plan configuration
SUBSCRIPTION_PLANS = {
    "starter": {
        "name": "Starter",
        "monthly_price": 999,  # $9.99
        "annual_price": 9590,  # $95.90 (20% discount)
        "thread_limit": 100,
        "features": ["basic_analytics", "email_support"]
    },
    "pro": {
        "name": "Pro", 
        "monthly_price": 1999,  # $19.99
        "annual_price": 19190,  # $191.90 (20% discount)
        "thread_limit": -1,  # Unlimited
        "features": ["unlimited_threads", "advanced_analytics", "premium_templates", "priority_support"]
    },
    "team": {
        "name": "Team",
        "monthly_price": 4999,  # $49.99
        "annual_price": 47990,  # $479.90 (20% discount)
        "thread_limit": -1,  # Unlimited
        "features": ["unlimited_threads", "team_collaboration", "admin_dashboard", "dedicated_support", "custom_branding"]
    }
}

# Pydantic models
class SubscriptionInfo(BaseModel):
    subscription_id: Optional[str] = None
    plan_name: Optional[str] = None
    status: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: Optional[bool] = None
    thread_limit: Optional[int] = None
    features: Optional[List[str]] = None

class CreateCheckoutRequest(BaseModel):
    price_id: str
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None

class UpdateSubscriptionRequest(BaseModel):
    new_price_id: str

def create_subscription_router(auth_service: AuthService) -> APIRouter:
    """Create subscription router with auth service dependency"""
    router = APIRouter(prefix="/api/subscription", tags=["subscription"])
    
    @router.get("/plans", response_model=Dict[str, Any])
    async def get_subscription_plans():
        """Get available subscription plans and pricing"""
        try:
            # Add price IDs from environment (set during setup)
            plans_with_prices = {}
            for plan_id, plan_info in SUBSCRIPTION_PLANS.items():
                plans_with_prices[plan_id] = {
                    **plan_info,
                    "monthly_price_id": os.getenv(f"STRIPE_{plan_id.upper()}_MONTHLY_PRICE_ID"),
                    "annual_price_id": os.getenv(f"STRIPE_{plan_id.upper()}_ANNUAL_PRICE_ID")
                }
            
            return {
                "success": True,
                "plans": plans_with_prices
            }
        except Exception as e:
            logger.error(f"Error fetching subscription plans: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to fetch subscription plans")
    
    @router.post("/create-checkout", response_model=Dict[str, Any])
    async def create_checkout_session(
        request: CreateCheckoutRequest,
        current_user = Depends(get_current_user)
    ):
        """Create Stripe checkout session for subscription"""
        try:
            # Default URLs
            success_url = request.success_url or "https://threadr-plum.vercel.app/dashboard?session_id={CHECKOUT_SESSION_ID}"
            cancel_url = request.cancel_url or "https://threadr-plum.vercel.app/pricing"
            
            # Create checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='subscription',
                line_items=[{
                    'price': request.price_id,
                    'quantity': 1,
                }],
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=current_user.get("email"),
                client_reference_id=current_user.get("user_id"),
                metadata={
                    "user_id": current_user.get("user_id"),
                    "email": current_user.get("email")
                }
            )
            
            return {
                "success": True,
                "checkout_url": checkout_session.url,
                "session_id": checkout_session.id
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe checkout error: {str(e)}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating checkout session: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to create checkout session")
    
    @router.get("/status", response_model=SubscriptionInfo)
    async def get_subscription_status(current_user = Depends(get_current_user)):
        """Get current user's subscription status"""
        try:
            redis_manager = await get_redis_manager()
            user_id = current_user.get("user_id")
            
            # Get subscription info from Redis
            subscription_data = await redis_manager.get_user_subscription(user_id)
            
            if not subscription_data:
                return SubscriptionInfo(
                    subscription_id=None,
                    plan_name=None,
                    status="inactive",
                    thread_limit=5,  # Free tier limit
                    features=["basic_threads"]
                )
            
            # Parse subscription data
            return SubscriptionInfo(**subscription_data)
            
        except Exception as e:
            logger.error(f"Error fetching subscription status: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to fetch subscription status")
    
    @router.post("/cancel", response_model=Dict[str, Any])
    async def cancel_subscription(current_user = Depends(get_current_user)):
        """Cancel user's subscription at period end"""
        try:
            redis_manager = await get_redis_manager()
            user_id = current_user.get("user_id")
            
            # Get current subscription
            subscription_data = await redis_manager.get_user_subscription(user_id)
            if not subscription_data or not subscription_data.get("subscription_id"):
                raise HTTPException(status_code=404, detail="No active subscription found")
            
            # Cancel subscription at period end
            subscription = stripe.Subscription.modify(
                subscription_data["subscription_id"],
                cancel_at_period_end=True
            )
            
            # Update subscription data in Redis
            subscription_data["cancel_at_period_end"] = True
            await redis_manager.update_user_subscription(user_id, subscription_data)
            
            return {
                "success": True,
                "message": "Subscription will be cancelled at the end of the current billing period",
                "period_end": subscription.current_period_end
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe cancellation error: {str(e)}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
        except Exception as e:
            logger.error(f"Error cancelling subscription: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to cancel subscription")
    
    @router.post("/reactivate", response_model=Dict[str, Any])
    async def reactivate_subscription(current_user = Depends(get_current_user)):
        """Reactivate a cancelled subscription"""
        try:
            redis_manager = await get_redis_manager()
            user_id = current_user.get("user_id")
            
            # Get current subscription
            subscription_data = await redis_manager.get_user_subscription(user_id)
            if not subscription_data or not subscription_data.get("subscription_id"):
                raise HTTPException(status_code=404, detail="No subscription found")
            
            # Reactivate subscription
            subscription = stripe.Subscription.modify(
                subscription_data["subscription_id"],
                cancel_at_period_end=False
            )
            
            # Update subscription data in Redis
            subscription_data["cancel_at_period_end"] = False
            await redis_manager.update_user_subscription(user_id, subscription_data)
            
            return {
                "success": True,
                "message": "Subscription reactivated successfully"
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe reactivation error: {str(e)}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
        except Exception as e:
            logger.error(f"Error reactivating subscription: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to reactivate subscription")
    
    @router.post("/change-plan", response_model=Dict[str, Any])
    async def change_subscription_plan(
        request: UpdateSubscriptionRequest,
        current_user = Depends(get_current_user)
    ):
        """Change subscription plan (upgrade/downgrade)"""
        try:
            redis_manager = await get_redis_manager()
            user_id = current_user.get("user_id")
            
            # Get current subscription
            subscription_data = await redis_manager.get_user_subscription(user_id)
            if not subscription_data or not subscription_data.get("subscription_id"):
                raise HTTPException(status_code=404, detail="No active subscription found")
            
            # Get current subscription from Stripe
            subscription = stripe.Subscription.retrieve(subscription_data["subscription_id"])
            
            # Update subscription with new price
            updated_subscription = stripe.Subscription.modify(
                subscription.id,
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'price': request.new_price_id,
                }],
                proration_behavior='immediate_change'
            )
            
            # Update subscription data in Redis
            plan_name = get_plan_name_from_price_id(request.new_price_id)
            subscription_data.update({
                "plan_name": plan_name,
                "current_period_start": datetime.fromtimestamp(updated_subscription.current_period_start),
                "current_period_end": datetime.fromtimestamp(updated_subscription.current_period_end),
                "thread_limit": SUBSCRIPTION_PLANS.get(plan_name, {}).get("thread_limit", 5),
                "features": SUBSCRIPTION_PLANS.get(plan_name, {}).get("features", [])
            })
            await redis_manager.update_user_subscription(user_id, subscription_data)
            
            return {
                "success": True,
                "message": f"Plan changed to {plan_name.title()}",
                "new_plan": plan_name
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe plan change error: {str(e)}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
        except Exception as e:
            logger.error(f"Error changing subscription plan: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to change subscription plan")
    
    @router.get("/usage", response_model=Dict[str, Any])
    async def get_subscription_usage(current_user = Depends(get_current_user)):
        """Get current subscription usage statistics"""
        try:
            redis_manager = await get_redis_manager()
            user_id = current_user.get("user_id")
            
            # Get usage data from Redis
            usage_data = await redis_manager.get_user_usage_stats(user_id)
            subscription_data = await redis_manager.get_user_subscription(user_id)
            
            # Calculate limits based on subscription
            thread_limit = 5  # Free tier default
            if subscription_data and subscription_data.get("plan_name"):
                plan_info = SUBSCRIPTION_PLANS.get(subscription_data["plan_name"], {})
                thread_limit = plan_info.get("thread_limit", 5)
            
            return {
                "success": True,
                "usage": {
                    "threads_this_month": usage_data.get("threads_this_month", 0),
                    "threads_today": usage_data.get("threads_today", 0),
                    "thread_limit": thread_limit,
                    "unlimited": thread_limit == -1,
                    "subscription_status": subscription_data.get("status", "inactive") if subscription_data else "inactive"
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching subscription usage: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to fetch subscription usage")
    
    return router

def get_plan_name_from_price_id(price_id: str) -> str:
    """Extract plan name from Stripe price ID using environment variables"""
    for plan_name in SUBSCRIPTION_PLANS.keys():
        monthly_price_id = os.getenv(f"STRIPE_{plan_name.upper()}_MONTHLY_PRICE_ID")
        annual_price_id = os.getenv(f"STRIPE_{plan_name.upper()}_ANNUAL_PRICE_ID")
        
        if price_id in [monthly_price_id, annual_price_id]:
            return plan_name
    
    return "unknown"

async def handle_subscription_webhook(event_type: str, data: Dict[str, Any]) -> bool:
    """Handle subscription-related webhook events"""
    try:
        redis_manager = await get_redis_manager()
        
        if event_type == "customer.subscription.created":
            # New subscription created
            subscription = data["object"]
            customer_id = subscription["customer"]
            
            # Get customer details
            customer = stripe.Customer.retrieve(customer_id)
            user_email = customer.email
            
            # Extract plan information
            price_id = subscription["items"]["data"][0]["price"]["id"]
            plan_name = get_plan_name_from_price_id(price_id)
            plan_info = SUBSCRIPTION_PLANS.get(plan_name, {})
            
            # Store subscription data
            subscription_data = {
                "subscription_id": subscription["id"],
                "plan_name": plan_name,
                "status": subscription["status"],
                "current_period_start": datetime.fromtimestamp(subscription["current_period_start"]),
                "current_period_end": datetime.fromtimestamp(subscription["current_period_end"]),
                "cancel_at_period_end": subscription["cancel_at_period_end"],
                "thread_limit": plan_info.get("thread_limit", 5),
                "features": plan_info.get("features", [])
            }
            
            # Save to Redis (use email as key for now, update when user_id available)
            await redis_manager.create_user_subscription(user_email, subscription_data)
            
            logger.info(f"Subscription created for {user_email}: {plan_name}")
            return True
            
        elif event_type == "customer.subscription.updated":
            # Subscription updated (plan change, cancellation, etc.)
            subscription = data["object"]
            
            # Update subscription data
            subscription_data = {
                "subscription_id": subscription["id"],
                "status": subscription["status"],
                "current_period_start": datetime.fromtimestamp(subscription["current_period_start"]),
                "current_period_end": datetime.fromtimestamp(subscription["current_period_end"]),
                "cancel_at_period_end": subscription["cancel_at_period_end"]
            }
            
            await redis_manager.update_subscription_by_id(subscription["id"], subscription_data)
            
            logger.info(f"Subscription updated: {subscription['id']}")
            return True
            
        elif event_type == "customer.subscription.deleted":
            # Subscription cancelled/ended
            subscription = data["object"]
            
            await redis_manager.deactivate_subscription(subscription["id"])
            
            logger.info(f"Subscription cancelled: {subscription['id']}")
            return True
            
        elif event_type == "invoice.payment_succeeded":
            # Successful payment for subscription
            invoice = data["object"]
            subscription_id = invoice["subscription"]
            
            # Reactivate subscription if it was past due
            await redis_manager.reactivate_subscription(subscription_id)
            
            logger.info(f"Payment succeeded for subscription: {subscription_id}")
            return True
            
        elif event_type == "invoice.payment_failed":
            # Failed payment for subscription
            invoice = data["object"]
            subscription_id = invoice["subscription"]
            
            # Mark subscription as past due (but don't deactivate immediately)
            await redis_manager.mark_subscription_past_due(subscription_id)
            
            logger.warning(f"Payment failed for subscription: {subscription_id}")
            return True
            
        else:
            logger.info(f"Unhandled subscription webhook event: {event_type}")
            return True
            
    except Exception as e:
        logger.error(f"Error handling subscription webhook {event_type}: {str(e)}", exc_info=True)
        return False