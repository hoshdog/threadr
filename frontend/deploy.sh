#!/bin/bash
# Threadr Frontend Deployment Script - Bash
# Deploys the Threadr frontend to Vercel with proper configuration
# Author: Claude Code Deployment Engineer

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
PRODUCTION=false
FORCE=false
TOKEN=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--production)
            PRODUCTION=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -t|--token)
            TOKEN="$2"
            shift 2
            ;;
        -h|--help)
            echo "Threadr Frontend Deployment Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -p, --production    Deploy to production (default: preview)"
            echo "  -f, --force         Force deployment"
            echo "  -t, --token TOKEN   Use specific Vercel token"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                  # Deploy to preview"
            echo "  $0 --production     # Deploy to production"
            echo "  $0 -p -f            # Force deploy to production"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Utility functions
print_header() {
    echo -e "\n${BLUE}"
    echo "============================================================"
    echo " $1"
    echo "============================================================"
    echo -e "${NC}"
}

print_step() {
    echo -e "${CYAN}[STEP] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Main deployment function
deploy_frontend() {
    print_header "Threadr Frontend Deployment Script"
    
    # Check if we're in the correct directory
    if [[ ! -f "index.html" || ! -f "config.js" || ! -f "vercel.json" ]]; then
        print_error "Missing required files. Please run this script from the frontend directory."
        echo "Required files: index.html, config.js, vercel.json"
        exit 1
    fi
    
    print_success "Found all required files"
    
    # Check Vercel CLI installation
    print_step "Checking Vercel CLI installation..."
    if command -v vercel &> /dev/null; then
        VERCEL_VERSION=$(vercel --version 2>/dev/null || echo "unknown")
        print_success "Vercel CLI installed: $VERCEL_VERSION"
    else
        print_error "Vercel CLI not found. Please install it with: npm install -g vercel"
        exit 1
    fi
    
    # Check authentication status
    print_step "Checking Vercel authentication..."
    if [[ -n "$TOKEN" ]]; then
        print_step "Using provided token for authentication..."
        export VERCEL_TOKEN="$TOKEN"
    fi
    
    # Try to list projects to test authentication
    if vercel ls &> /dev/null; then
        print_success "Vercel authentication verified"
    else
        print_warning "Not authenticated with Vercel. Starting login process..."
        echo ""
        echo -e "${YELLOW}Please follow these steps:${NC}"
        echo -e "${YELLOW}1. A browser window will open${NC}"
        echo -e "${YELLOW}2. Sign in with your Vercel account${NC}"
        echo -e "${YELLOW}3. Return to this terminal once authenticated${NC}"
        echo ""
        
        # Attempt login
        if vercel login; then
            print_success "Successfully authenticated with Vercel"
        else
            print_error "Failed to authenticate with Vercel. Please try manually: vercel login"
            exit 1
        fi
    fi
    
    # Pre-deployment checks
    print_step "Running pre-deployment checks..."
    
    # Validate vercel.json structure
    if [[ -f "vercel.json" ]]; then
        if command -v jq &> /dev/null; then
            if jq empty vercel.json 2>/dev/null; then
                if jq -e '.builds and .routes' vercel.json > /dev/null; then
                    print_success "vercel.json validation passed"
                else
                    print_warning "vercel.json may be incomplete"
                fi
            else
                print_error "Invalid vercel.json format"
                exit 1
            fi
        else
            print_warning "jq not available, skipping JSON validation"
        fi
    fi
    
    # Validate config.js
    if [[ -f "config.js" ]]; then
        if grep -q "threadr-production\.up\.railway\.app" config.js; then
            print_success "Backend API URL configured correctly"
        else
            print_warning "Backend API URL may not be configured correctly"
        fi
    fi
    
    # Prepare deployment arguments
    DEPLOY_ARGS="--yes"
    
    if [[ "$PRODUCTION" == true ]]; then
        print_step "Deploying to PRODUCTION..."
        DEPLOY_ARGS="$DEPLOY_ARGS --prod"
    else
        print_step "Deploying to PREVIEW..."
    fi
    
    if [[ "$FORCE" == true ]]; then
        DEPLOY_ARGS="$DEPLOY_ARGS --force"
    fi
    
    echo -e "${BLUE}Deployment command: vercel $DEPLOY_ARGS${NC}"
    echo ""
    
    # Execute deployment
    print_step "Starting Vercel deployment..."
    if DEPLOY_OUTPUT=$(vercel $DEPLOY_ARGS 2>&1); then
        print_success "Deployment completed successfully!"
        echo ""
        
        # Extract deployment URL from output
        DEPLOYMENT_URL=$(echo "$DEPLOY_OUTPUT" | grep -o 'https://[^[:space:]]*\.vercel\.app' | head -1)
        
        if [[ -n "$DEPLOYMENT_URL" ]]; then
            echo -e "${GREEN}Deployment URL: $DEPLOYMENT_URL${NC}"
            
            # Test the deployment
            print_step "Testing deployment..."
            if command -v curl &> /dev/null; then
                HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$DEPLOYMENT_URL" --max-time 30)
                if [[ "$HTTP_STATUS" == "200" ]]; then
                    print_success "Deployment is accessible and returning HTTP 200"
                    
                    # Check if it contains expected content
                    if curl -s "$DEPLOYMENT_URL" --max-time 30 | grep -q "Threadr"; then
                        print_success "Deployment contains expected Threadr content"
                    else
                        print_warning "Deployment accessible but may not contain expected content"
                    fi
                else
                    print_warning "Deployment returned HTTP $HTTP_STATUS"
                fi
            else
                print_warning "curl not available, skipping deployment test"
            fi
            
            echo ""
            echo -e "${YELLOW}Next Steps:${NC}"
            echo -e "${YELLOW}1. Visit: $DEPLOYMENT_URL${NC}"
            echo -e "${YELLOW}2. Test the thread generation functionality${NC}"
            echo -e "${YELLOW}3. Configure custom domain if needed: vercel domains add your-domain.com${NC}"
            
            if [[ "$PRODUCTION" != true ]]; then
                echo -e "${YELLOW}4. Deploy to production when ready: $0 --production${NC}"
            fi
        else
            print_warning "Could not extract deployment URL from output"
            echo -e "${BLUE}Full deployment output:${NC}"
            echo "$DEPLOY_OUTPUT"
        fi
    else
        print_error "Deployment failed!"
        echo -e "${RED}Error output:${NC}"
        echo -e "${RED}$DEPLOY_OUTPUT${NC}"
        exit 1
    fi
}

# Script execution
echo -e "${BLUE}Threadr Frontend Deployment Script${NC}"
echo -e "${BLUE}Current directory: $(pwd)${NC}"
echo -e "${BLUE}Production deployment: $PRODUCTION${NC}"
echo -e "${BLUE}Force deployment: $FORCE${NC}"

if [[ -n "$TOKEN" ]]; then
    echo -e "${BLUE}Using provided authentication token${NC}"
fi

echo ""

# Run the deployment
deploy_frontend

echo ""
print_success "Deployment script completed successfully!"