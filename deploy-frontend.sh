#!/bin/bash

# Threadr Frontend Deployment Script for Vercel
# Run this script from the root directory of the project

echo "🚀 Threadr Frontend Deployment to Vercel"
echo "========================================="

# Check if we're in the correct directory
if [ ! -f "frontend/index.html" ]; then
    echo "❌ Error: frontend/index.html not found. Please run this script from the project root directory."
    exit 1
fi

# Navigate to frontend directory
cd frontend
echo "📁 Current directory: $(pwd)"

# Check Vercel CLI installation
echo "🔍 Checking Vercel CLI installation..."
if command -v vercel &> /dev/null; then
    VERCEL_VERSION=$(vercel --version)
    echo "✅ Vercel CLI installed: $VERCEL_VERSION"
else
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
    echo "✅ Vercel CLI installed successfully"
fi

# Test backend API health
echo "🏥 Testing backend API health..."
if curl -s -f "https://threadr-production.up.railway.app/health" > /dev/null; then
    HEALTH_RESPONSE=$(curl -s "https://threadr-production.up.railway.app/health")
    echo "✅ Backend API is healthy: $(echo $HEALTH_RESPONSE | grep -o '"message":"[^"]*"' | cut -d'"' -f4)"
else
    echo "❌ Backend API health check failed"
    echo "⚠️  Continuing with deployment, but API may not be available"
fi

# Check authentication status
echo "🔐 Checking Vercel authentication..."
if vercel whoami &> /dev/null; then
    AUTH_USER=$(vercel whoami)
    echo "✅ Already authenticated as: $AUTH_USER"
    NEEDS_AUTH=false
else
    NEEDS_AUTH=true
fi

if [ "$NEEDS_AUTH" = true ]; then
    echo "🔑 Authentication required. Please login to Vercel..."
    echo "   Choose your preferred method (GitHub recommended)"
    vercel login
    
    # Verify authentication worked
    if vercel whoami &> /dev/null; then
        AUTH_USER=$(vercel whoami)
        echo "✅ Successfully authenticated as: $AUTH_USER"
    else
        echo "❌ Authentication failed. Please try again."
        exit 1
    fi
fi

# Deploy to production
echo "🚀 Deploying to Vercel production..."
echo "   This may take a few moments..."

DEPLOY_OUTPUT=$(vercel --prod --yes 2>&1)
DEPLOY_STATUS=$?

if [ $DEPLOY_STATUS -eq 0 ]; then
    # Extract the production URL from the output
    PRODUCTION_URL=$(echo "$DEPLOY_OUTPUT" | grep -o 'https://[^[:space:]]*\.vercel\.app')
    
    if [ -n "$PRODUCTION_URL" ]; then
        echo "✅ Deployment successful!"
        echo "🌐 Production URL: $PRODUCTION_URL"
        
        # Test the deployed frontend
        echo "🧪 Testing deployed frontend..."
        if curl -s -f "$PRODUCTION_URL" > /dev/null; then
            echo "✅ Frontend is accessible and responding"
        else
            echo "❌ Frontend test failed"
        fi
        
    else
        echo "⚠️  Deployment completed but couldn't extract URL from output"
        echo "Full output:"
        echo "$DEPLOY_OUTPUT"
    fi
    
else
    echo "❌ Deployment failed"
    echo "Full error output:"
    echo "$DEPLOY_OUTPUT"
    exit 1
fi

# Final instructions
echo ""
echo "🎉 Deployment Complete!"
echo "=============================="
echo "Frontend URL: $PRODUCTION_URL"
echo "Backend API:  https://threadr-production.up.railway.app"
echo ""
echo "Next Steps:"
echo "1. Visit the frontend URL to test the application"
echo "2. Try converting a blog article URL to a Twitter thread"
echo "3. Verify that the API connection works properly"
echo "4. Test the email capture modal after first use"
echo ""
echo "If you encounter issues, check the browser console for errors."

# Return to original directory
cd ..