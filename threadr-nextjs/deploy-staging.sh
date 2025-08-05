#!/bin/bash

echo "==============================================="
echo " Threadr Next.js - Vercel Staging Deployment"
echo "==============================================="
echo

echo "Checking Vercel CLI..."
if ! command -v vercel &> /dev/null; then
    echo "ERROR: Vercel CLI not found. Please install with: npm i -g vercel"
    exit 1
fi

vercel --version
echo

echo "Checking build status..."
npm run build

if [ $? -ne 0 ]; then
    echo "ERROR: Build failed. Please check for errors above."
    exit 1
fi

echo
echo "Build successful! Starting deployment..."
echo
echo "IMPORTANT: When prompted, choose:"
echo "  - Set up and deploy: Yes"
echo "  - Link to existing project: No (new deployment)"
echo "  - Project name: threadr-nextjs-staging"
echo "  - Directory: Accept default (./)"
echo "  - Override settings: No"
echo
read -p "Press Enter to continue with deployment..."

echo "Deploying to Vercel staging..."
vercel --prod=false

echo
echo "==============================================="
echo "Deployment completed!"
echo
echo "Next steps:"
echo "1. Note your deployment URL from above"
echo "2. Go to Vercel Dashboard"
echo "3. Add environment variables (see VERCEL_DEPLOYMENT_INSTRUCTIONS.md)"
echo "4. Redeploy with: vercel --prod=false"
echo "==============================================="