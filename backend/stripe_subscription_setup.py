#!/usr/bin/env python3
"""
Stripe Subscription Products Setup Script
Run this script to create subscription products in your Stripe account
"""

import stripe
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_subscription_products():
    """Create subscription products and prices in Stripe"""
    
    print("[INFO] Setting up Threadr subscription products in Stripe...")
    
    # Product 1: Starter Plan
    try:
        starter_product = stripe.Product.create(
            name="Threadr Starter",
            description="100 threads per month with basic analytics",
            metadata={
                "plan_type": "starter",
                "thread_limit": "100",
                "features": "basic_analytics,email_support"
            }
        )
        
        starter_price = stripe.Price.create(
            unit_amount=999,  # $9.99 in cents
            currency="usd",
            recurring={"interval": "month"},
            product=starter_product.id,
            metadata={
                "plan_name": "starter",
                "thread_limit": "100"
            }
        )
        
        print(f"[SUCCESS] Starter Plan Created: {starter_product.id}")
        print(f"   Price ID: {starter_price.id}")
        
    except stripe.error.StripeError as e:
        print(f"[ERROR] Error creating Starter plan: {e}")
    
    # Product 2: Pro Plan (RECOMMENDED)
    try:
        pro_product = stripe.Product.create(
            name="Threadr Pro",
            description="Unlimited threads with advanced analytics and premium templates",
            metadata={
                "plan_type": "pro",
                "thread_limit": "unlimited",
                "features": "unlimited_threads,advanced_analytics,premium_templates,priority_support"
            }
        )
        
        pro_price = stripe.Price.create(
            unit_amount=1999,  # $19.99 in cents
            currency="usd", 
            recurring={"interval": "month"},
            product=pro_product.id,
            metadata={
                "plan_name": "pro",
                "thread_limit": "unlimited"
            }
        )
        
        print(f"[SUCCESS] Pro Plan Created: {pro_product.id}")
        print(f"   Price ID: {pro_price.id}")
        
    except stripe.error.StripeError as e:
        print(f"[ERROR] Error creating Pro plan: {e}")
    
    # Product 3: Team Plan
    try:
        team_product = stripe.Product.create(
            name="Threadr Team",
            description="Everything in Pro plus team collaboration and admin features",
            metadata={
                "plan_type": "team", 
                "thread_limit": "unlimited",
                "features": "unlimited_threads,team_collaboration,admin_dashboard,dedicated_support,custom_branding"
            }
        )
        
        team_price = stripe.Price.create(
            unit_amount=4999,  # $49.99 in cents
            currency="usd",
            recurring={"interval": "month"}, 
            product=team_product.id,
            metadata={
                "plan_name": "team",
                "thread_limit": "unlimited"
            }
        )
        
        print(f"[SUCCESS] Team Plan Created: {team_product.id}")
        print(f"   Price ID: {team_price.id}")
        
    except stripe.error.StripeError as e:
        print(f"[ERROR] Error creating Team plan: {e}")
    
    # Create annual pricing options (20% discount)
    print("\n[INFO] Creating annual pricing options...")
    
    try:
        # Starter Annual ($95.90 = $9.99 * 12 * 0.8)
        starter_annual_price = stripe.Price.create(
            unit_amount=9590,  # $95.90 in cents (20% discount)
            currency="usd",
            recurring={"interval": "year"},
            product=starter_product.id,
            metadata={
                "plan_name": "starter_annual",
                "discount": "20_percent"
            }
        )
        print(f"[SUCCESS] Starter Annual: {starter_annual_price.id} ($95.90/year)")
        
        # Pro Annual ($191.90 = $19.99 * 12 * 0.8)
        pro_annual_price = stripe.Price.create(
            unit_amount=19190,  # $191.90 in cents (20% discount)
            currency="usd",
            recurring={"interval": "year"},
            product=pro_product.id,
            metadata={
                "plan_name": "pro_annual",
                "discount": "20_percent"
            }
        )
        print(f"[SUCCESS] Pro Annual: {pro_annual_price.id} ($191.90/year)")
        
        # Team Annual ($479.90 = $49.99 * 12 * 0.8)
        team_annual_price = stripe.Price.create(
            unit_amount=47990,  # $479.90 in cents (20% discount)
            currency="usd",
            recurring={"interval": "year"},
            product=team_product.id,
            metadata={
                "plan_name": "team_annual",
                "discount": "20_percent"
            }
        )
        print(f"[SUCCESS] Team Annual: {team_annual_price.id} ($479.90/year)")
        
    except stripe.error.StripeError as e:
        print(f"[ERROR] Error creating annual plans: {e}")
    
    print("\n[COMPLETE] SUBSCRIPTION SETUP COMPLETE!")
    print("\n[NEXT STEPS]:")
    print("1. Copy the Price IDs above and add them to your .env file")
    print("2. Update webhook to handle subscription events")
    print("3. Deploy backend subscription management endpoints")
    print("4. Update frontend with subscription selection UI")
    
    print("\n[REVENUE POTENTIAL]:")
    print("   95 Pro subscribers x $19.99 = $1,899 MRR")
    print("   Mixed plans targeting $1,349 MRR goal")

if __name__ == "__main__":
    if not os.getenv("STRIPE_SECRET_KEY"):
        print("[ERROR] Error: STRIPE_SECRET_KEY not found in environment variables")
        print("   Please set your Stripe secret key in .env file")
        exit(1)
    
    create_subscription_products()