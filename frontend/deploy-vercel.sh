#!/bin/bash

# Threadr Frontend - Vercel Deployment Script
# Run this script from the frontend/ directory

echo "🚀 Threadr Frontend - Vercel Deployment"
echo "==============================================="

# Check if we're in the correct directory
if [ ! -f "index.html" ]; then
    echo "❌ Error: index.html not found. Please run this script from the frontend/ directory."
    exit 1
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "⚠️  Vercel CLI not found. Installing..."
    npm install -g vercel
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Vercel CLI. Please install manually: npm install -g vercel"
        exit 1
    fi
fi

# Check Vercel login status
echo "🔐 Checking Vercel authentication..."
vercel whoami
if [ $? -ne 0 ]; then
    echo "🔐 Please login to Vercel..."
    vercel login
    if [ $? -ne 0 ]; then
        echo "❌ Vercel login failed. Please try again."
        exit 1
    fi
fi

# Display current configuration
echo ""
echo "📋 Current Configuration:"
echo "- Project: threadr-frontend"
echo "- Backend API: https://threadr-production.up.railway.app"
echo "- Files: index.html, config.js, vercel.json, package.json"

# Ask for deployment type
echo ""
echo "🎯 Select deployment type:"
echo "1. Preview deployment (for testing)"
echo "2. Production deployment"
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "🔄 Deploying to preview..."
        vercel
        ;;
    2)
        echo ""
        echo "🚀 Deploying to production..."
        vercel --prod
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment completed successfully!"
    echo ""
    echo "🔗 Your frontend is now live and connected to the Railway backend."
    echo "📱 Test the application by generating a thread from a URL or text."
    
    echo ""
    echo "📊 Next steps:"
    echo "1. Test the live deployment"
    echo "2. Set up custom domain (optional)"
    echo "3. Monitor usage and performance"
else
    echo ""
    echo "❌ Deployment failed. Please check the error messages above."
    echo "💡 Common issues:"
    echo "- Network connectivity problems"
    echo "- Vercel account limits reached"
    echo "- Configuration errors in vercel.json"
fi

echo ""
echo "🔧 For troubleshooting, check:"
echo "- Vercel dashboard: https://vercel.com/dashboard"
echo "- Railway backend: https://threadr-production.up.railway.app/health"
echo "- Browser console for client-side errors"