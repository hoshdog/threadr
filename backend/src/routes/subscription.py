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
import hmac
import hashlib

# Import dependencies
try:
    from ..core.redis_manager import get_redis_manager
    from ..middleware.auth import create_auth_dependencies
    from ..services.auth.auth_service import AuthService
except ImportError:
    from src.core.redis_manager import get_redis_manager
    from src.middleware.auth import create_auth_dependencies
    from src.services.auth.auth_service import AuthService

# Configure logging
logger = logging.getLogger(__name__)

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Threadr Subscription Plans Configuration
SUBSCRIPTION_PLANS = {
    "threadr_starter": {
        "name": "Threadr Starter",
        "display_name": "Starter",
        "monthly_price": 999,  # $9.99
        "annual_price": 9590,  # $95.90 (20% discount)
        "thread_limit": 100,
        "tier_level": 1,
        "features": [
            "basic_analytics", 
            "email_support", 
            "100_threads_per_month",
            "basic_templates"
        ]
    },
    "threadr_pro": {
        "name": "Threadr Pro",
        "display_name": "Pro",
        "monthly_price": 1999,  # $19.99
        "annual_price": 19190,  # $191.90 (20% discount)
        "thread_limit": -1,  # Unlimited
        "tier_level": 2,
        "features": [
            "unlimited_threads", 
            "advanced_analytics", 
            "premium_templates", 
            "priority_support",
            "custom_scheduling",
            "export_threads"
        ]
    },
    "threadr_team": {
        "name": "Threadr Team",
        "display_name": "Team",
        "monthly_price": 4999,  # $49.99
        "annual_price": 47990,  # $479.90 (20% discount)
        "thread_limit": -1,  # Unlimited
        "tier_level": 3,
        "features": [
            "unlimited_threads", 
            "team_collaboration", 
            "admin_dashboard", 
            "dedicated_support", 
            "custom_branding",
            "api_access",
            "bulk_processing",
            "analytics_export",
            "white_labeling"
        ]
    }
}

# Pydantic models
class SubscriptionInfo(BaseModel):
    subscription_id: Optional[str] = None
    plan_name: Optional[str] = None
    plan_display_name: Optional[str] = None
    tier_level: Optional[int] = None
    status: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: Optional[bool] = None
    thread_limit: Optional[int] = None
    features: Optional[List[str]] = None
    is_annual: Optional[bool] = None
    monthly_price: Optional[int] = None
    annual_price: Optional[int] = None

class CreateCheckoutRequest(BaseModel):
    price_id: str
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None

class UpdateSubscriptionRequest(BaseModel):
    new_price_id: str

def create_subscription_router(auth_service: AuthService) -> APIRouter:
    """Create subscription router with auth service dependency"""
    router = APIRouter(prefix="/api", tags=["subscription"])
    
    # Create auth dependencies
    auth_deps = create_auth_dependencies(auth_service)
    get_current_user_required = auth_deps["get_current_user_required"]
    get_current_user_optional = auth_deps["get_current_user_optional"]
    
    @router.get("/subscriptions/plans", response_model=Dict[str, Any])
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
            
            # Convert plans dict to array format expected by frontend
            plans_array = []
            for plan_id, plan_info in plans_with_prices.items():
                plans_array.append({
                    "id": plan_id,
                    **plan_info
                })
            
            return {
                "success": True,
                "data": plans_array
            }
        except Exception as e:
            logger.error(f"Error fetching subscription plans: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to fetch subscription plans")
    
    @router.post("/stripe/create-checkout-session", response_model=Dict[str, Any])
    async def create_checkout_session(
        request: CreateCheckoutRequest,
        current_user = Depends(get_current_user_required)
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
                customer_email=current_user.email,
                client_reference_id=current_user.user_id,
                metadata={
                    "user_id": current_user.user_id,
                    "email": current_user.email
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
    
    @router.get("/subscriptions/current", response_model=SubscriptionInfo)
    async def get_subscription_status(current_user = Depends(get_current_user_required)):
        """Get current user's subscription status"""
        try:
            redis_manager = get_redis_manager()
            user_id = current_user.user_id
            
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
            # Convert datetime objects for the response
            response_data = subscription_data.copy()
            if 'current_period_start' in response_data and isinstance(response_data['current_period_start'], str):
                response_data['current_period_start'] = datetime.fromisoformat(response_data['current_period_start'])
            if 'current_period_end' in response_data and isinstance(response_data['current_period_end'], str):
                response_data['current_period_end'] = datetime.fromisoformat(response_data['current_period_end'])
            
            return SubscriptionInfo(**response_data)
            
        except Exception as e:
            logger.error(f"Error fetching subscription status: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to fetch subscription status")
    
    @router.post("/subscriptions/cancel", response_model=Dict[str, Any])
    async def cancel_subscription(current_user = Depends(get_current_user_required)):
        """Cancel user's subscription at period end"""
        try:
            redis_manager = get_redis_manager()
            user_id = current_user.user_id
            
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
    
    @router.post("/subscriptions/reactivate", response_model=Dict[str, Any])
    async def reactivate_subscription(current_user = Depends(get_current_user_required)):
        """Reactivate a cancelled subscription"""
        try:
            redis_manager = get_redis_manager()
            user_id = current_user.user_id
            
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
    
    @router.post("/subscriptions/change-plan", response_model=Dict[str, Any])
    async def change_subscription_plan(
        request: UpdateSubscriptionRequest,
        current_user = Depends(get_current_user_required)
    ):
        """Change subscription plan (upgrade/downgrade)"""
        try:
            redis_manager = get_redis_manager()
            user_id = current_user.user_id
            
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
            plan_name, is_annual = get_plan_name_from_price_id(request.new_price_id)
            plan_info = get_plan_by_name(plan_name)
            subscription_data.update({
                "plan_name": plan_name,
                "plan_display_name": plan_info.get("display_name", "Unknown"),
                "tier_level": plan_info.get("tier_level", 0),
                "current_period_start": datetime.fromtimestamp(updated_subscription.current_period_start),
                "current_period_end": datetime.fromtimestamp(updated_subscription.current_period_end),
                "thread_limit": plan_info.get("thread_limit", 5),
                "features": plan_info.get("features", []),
                "is_annual": is_annual,
                "monthly_price": plan_info.get("monthly_price", 0),
                "annual_price": plan_info.get("annual_price", 0)
            })
            await redis_manager.update_user_subscription(user_id, subscription_data)
            
            return {
                "success": True,
                "message": f"Plan changed to {plan_info.get('display_name', plan_name)}",
                "new_plan": plan_name
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe plan change error: {str(e)}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
        except Exception as e:
            logger.error(f"Error changing subscription plan: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to change subscription plan")
    
    @router.get("/subscriptions/usage", response_model=Dict[str, Any])
    async def get_subscription_usage(current_user = Depends(get_current_user_required)):
        """Get current subscription usage statistics"""
        try:
            redis_manager = get_redis_manager()
            user_id = current_user.user_id
            
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
    
    @router.get("/premium/check", response_model=Dict[str, Any])
    async def check_premium_status_auth(current_user = Depends(get_current_user_optional)):
        """Check premium status for authenticated users"""
        try:
            redis_manager = get_redis_manager()
            
            if current_user:
                # Authenticated user - check by user_id
                subscription_data = await redis_manager.get_user_subscription(current_user.user_id)
                if subscription_data and subscription_data.get("status") == "active":
                    return {
                        "success": True,
                        "is_premium": True,
                        "expires_at": subscription_data.get("current_period_end"),
                        "plan_name": subscription_data.get("plan_display_name", "Premium")
                    }
            
            # No authenticated user or no active subscription
            return {
                "success": True,
                "is_premium": False,
                "expires_at": None,
                "plan_name": None
            }
            
        except Exception as e:
            logger.error(f"Error checking premium status: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to check premium status")
    
    @router.post("/stripe/webhook", response_model=Dict[str, Any])
    async def stripe_webhook(request: Request):
        """Handle Stripe webhook events for subscription lifecycle"""
        try:
            payload = await request.body()
            sig_header = request.headers.get("stripe-signature")
            
            if not sig_header:
                logger.error("Missing stripe-signature header")
                raise HTTPException(status_code=400, detail="Missing stripe-signature header")
            
            # Verify webhook signature
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, STRIPE_WEBHOOK_SECRET
                )
            except ValueError:
                logger.error("Invalid payload in webhook")
                raise HTTPException(status_code=400, detail="Invalid payload")
            except stripe.error.SignatureVerificationError:
                logger.error("Invalid signature in webhook")
                raise HTTPException(status_code=400, detail="Invalid signature")
            
            # Handle the event
            event_type = event['type']
            logger.info(f"Processing Stripe webhook: {event_type}")
            
            success = await handle_subscription_webhook(event_type, event['data'])
            
            if success:
                return {"success": True, "message": f"Processed {event_type}"}
            else:
                logger.error(f"Failed to process webhook: {event_type}")
                raise HTTPException(status_code=500, detail="Webhook processing failed")
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected webhook error: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Webhook processing failed")
    
    return router

def get_plan_name_from_price_id(price_id: str) -> tuple[str, bool]:
    """Extract plan name from Stripe price ID using environment variables
    
    Returns:
        tuple: (plan_name, is_annual)
    """
    for plan_name in SUBSCRIPTION_PLANS.keys():
        env_key = plan_name.replace('_', '_').upper()
        monthly_price_id = os.getenv(f"STRIPE_{env_key}_MONTHLY_PRICE_ID")
        annual_price_id = os.getenv(f"STRIPE_{env_key}_ANNUAL_PRICE_ID")
        
        if price_id == monthly_price_id:
            return plan_name, False
        elif price_id == annual_price_id:
            return plan_name, True
    
    return "unknown", False

def get_plan_by_name(plan_name: str) -> Dict[str, Any]:
    """Get plan information by plan name"""
    return SUBSCRIPTION_PLANS.get(plan_name, {})

async def handle_subscription_webhook(event_type: str, data: Dict[str, Any]) -> bool:
    """Handle subscription-related webhook events"""
    try:
        redis_manager = get_redis_manager()
        
        if event_type == "customer.subscription.created":
            # New subscription created
            subscription = data["object"]
            customer_id = subscription["customer"]
            
            # Get customer details
            customer = stripe.Customer.retrieve(customer_id)
            user_email = customer.email
            
            # Extract plan information
            price_id = subscription["items"]["data"][0]["price"]["id"]
            plan_name, is_annual = get_plan_name_from_price_id(price_id)
            plan_info = SUBSCRIPTION_PLANS.get(plan_name, {})
            
            # Store subscription data
            subscription_data = {
                "subscription_id": subscription["id"],
                "plan_name": plan_name,
                "plan_display_name": plan_info.get("display_name", "Unknown"),
                "tier_level": plan_info.get("tier_level", 0),
                "status": subscription["status"],
                "current_period_start": datetime.fromtimestamp(subscription["current_period_start"]),
                "current_period_end": datetime.fromtimestamp(subscription["current_period_end"]),
                "cancel_at_period_end": subscription["cancel_at_period_end"],
                "thread_limit": plan_info.get("thread_limit", 5),
                "features": plan_info.get("features", []),
                "is_annual": is_annual,
                "monthly_price": plan_info.get("monthly_price", 0),
                "annual_price": plan_info.get("annual_price", 0)
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


# Create a default router instance for backward compatibility with main.py imports
# This will be a minimal router that can be imported but requires proper initialization
router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])

# Add a note that this router needs to be properly initialized
@router.get("/")
async def subscription_router_not_initialized():
    """Placeholder endpoint - this router needs proper initialization via create_subscription_router()"""
    return {"error": "Subscription router not properly initialized. Use create_subscription_router() function."}