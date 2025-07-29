#!/bin/bash

# Threadr Deployment Script
# This script helps deploy both frontend and backend

echo "Threadr Deployment Helper"
echo "========================"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Railway CLI not found. Please install it first:"
    echo "npm install -g @railway/cli"
    exit 1
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Vercel CLI not found. Please install it first:"
    echo "npm install -g vercel"
    exit 1
fi

echo ""
echo "Prerequisites:"
echo "1. Make sure you have accounts on Railway and Vercel"
echo "2. Your OPENAI_API_KEY should be ready"
echo "3. Update frontend/config.js with your Railway URL after deployment"
echo ""

read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo ""
echo "Step 1: Deploying Backend to Railway"
echo "-----------------------------------"
cd backend

echo "Logging into Railway..."
railway login

echo "Creating new Railway project..."
railway init

echo "Adding environment variables..."
echo "Please add OPENAI_API_KEY in Railway dashboard after deployment"

echo "Deploying to Railway..."
railway up

echo "Backend deployment initiated! Check Railway dashboard for status."
echo ""

cd ..

echo "Step 2: Deploying Frontend to Vercel"
echo "-----------------------------------"
cd frontend

echo "Deploying to Vercel..."
vercel

echo ""
echo "Deployment Complete!"
echo "==================="
echo ""
echo "Next Steps:"
echo "1. Add OPENAI_API_KEY in Railway dashboard"
echo "2. Update frontend/config.js with your Railway backend URL"
echo "3. Redeploy frontend with: vercel --prod"
echo "4. Update CORS_ORIGINS in Railway with your Vercel URL"