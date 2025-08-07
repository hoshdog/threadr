#!/bin/bash
# Comprehensive Threadr Business Functionality Test Runner
# Tests thread generation, storage, authentication, rate limiting, and analytics

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default configuration
BASE_URL="${BASE_URL:-https://threadr-pw0s.onrender.com}"
ENVIRONMENT="${ENVIRONMENT:-production}"
SKIP_CLEANUP="${SKIP_CLEANUP:-false}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --base-url)
            BASE_URL="$2"
            shift 2
            ;;
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --skip-cleanup)
            SKIP_CLEANUP="true"
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --base-url URL     Base URL for API (default: https://threadr-pw0s.onrender.com)"
            echo "  --environment ENV  Environment to test (default: production)"
            echo "  --skip-cleanup     Skip cleanup of test data"
            echo "  --help             Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}🚀 Threadr Business Functionality Test Suite${NC}"
echo -e "${GREEN}============================================================${NC}"

# Environment setup
echo -e "${YELLOW}🔧 Setting up test environment...${NC}"
export BASE_URL="$BASE_URL"

# Check Python availability
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python not found. Please install Python 3.8+ and ensure it's in PATH${NC}"
    exit 1
fi

# Determine Python command
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo -e "${GREEN}✅ Python available: $PYTHON_VERSION${NC}"

# Check pip availability
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo -e "${RED}❌ pip not found. Please install pip${NC}"
    exit 1
fi

# Determine pip command
PIP_CMD="pip3"
if ! command -v pip3 &> /dev/null; then
    PIP_CMD="pip"
fi

# Check required packages
echo -e "${YELLOW}📦 Checking Python dependencies...${NC}"
REQUIRED_PACKAGES=("httpx" "asyncio")

for package in "${REQUIRED_PACKAGES[@]}"; do
    if $PYTHON_CMD -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✅ Package '$package' available${NC}"
    else
        echo -e "${YELLOW}⚠️  Installing missing package: $package${NC}"
        $PIP_CMD install $package
    fi
done

# Display test configuration
echo -e "\n${CYAN}🎯 TEST CONFIGURATION:${NC}"
echo -e "   Base URL: $BASE_URL"
echo -e "   Environment: $ENVIRONMENT"
echo -e "   Skip Cleanup: $SKIP_CLEANUP"
echo -e "   Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"

# Validate API availability
echo -e "\n${YELLOW}🔍 Pre-flight checks...${NC}"

# Check if curl is available
if command -v curl &> /dev/null; then
    HEALTH_CHECK=$(curl -s "$BASE_URL/health" || echo "error")
    
    if [[ "$HEALTH_CHECK" == "error" ]]; then
        echo -e "${RED}❌ Pre-flight check failed: API not responding at $BASE_URL${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ API Health: Responding${NC}"
    
    # Try to parse JSON if possible (requires jq)
    if command -v jq &> /dev/null; then
        DB_STATUS=$(echo "$HEALTH_CHECK" | jq -r '.services.database // false' 2>/dev/null)
        REDIS_STATUS=$(echo "$HEALTH_CHECK" | jq -r '.services.redis // false' 2>/dev/null)
        
        if [[ "$DB_STATUS" == "true" ]]; then
            echo -e "${GREEN}✅ Database: Connected${NC}"
        else
            echo -e "${YELLOW}⚠️  Database: Status unknown${NC}"
        fi
        
        if [[ "$REDIS_STATUS" == "true" ]]; then
            echo -e "${GREEN}✅ Redis: Connected${NC}"
        else
            echo -e "${YELLOW}⚠️  Redis: Status unknown${NC}"
        fi
    fi
    
else
    echo -e "${YELLOW}⚠️  curl not available, skipping detailed health check${NC}"
fi

# Run the comprehensive test suite
echo -e "\n${YELLOW}🧪 Starting comprehensive business functionality tests...${NC}"
echo -e "${YELLOW}============================================================${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_SCRIPT="$SCRIPT_DIR/test_core_business_functionality.py"

if [[ ! -f "$TEST_SCRIPT" ]]; then
    echo -e "${RED}❌ Test script not found at: $TEST_SCRIPT${NC}"
    exit 1
fi

# Execute the Python test suite
START_TIME=$(date +%s)

echo -e "${YELLOW}⏳ Executing test suite (this may take 2-5 minutes)...${NC}"

if $PYTHON_CMD "$TEST_SCRIPT"; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}✅ Core business functionality is working correctly${NC}"
    echo -e "${GREEN}📈 Revenue-generating features validated${NC}"
    echo -e "${GREEN}🔒 Security and authentication verified${NC}"
    echo -e "${GREEN}💾 Data persistence confirmed${NC}"
    
    echo -e "\n${CYAN}⏱️  Total execution time: $DURATION seconds${NC}"
    
    # Success recommendations
    echo -e "\n${CYAN}🎯 NEXT STEPS:${NC}"
    echo -e "   1. ✅ System ready for production traffic"
    echo -e "   2. 📊 Consider setting up monitoring alerts"
    echo -e "   3. 🚀 Deploy any pending features"
    echo -e "   4. 💰 Focus on user acquisition"
    
else
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    echo -e "\n${RED}⚠️  SOME TESTS FAILED${NC}"
    echo -e "${RED}❌ Core business functionality has issues${NC}"
    echo -e "${YELLOW}🔧 Review test report for specific failures${NC}"
    echo -e "${RED}⚠️  DO NOT deploy to production until issues are resolved${NC}"
    
    # Check for test report files
    LATEST_REPORT=$(ls -t threadr_test_report_*.json 2>/dev/null | head -1 || echo "")
    if [[ -n "$LATEST_REPORT" ]]; then
        echo -e "\n${YELLOW}📄 Latest test report: $LATEST_REPORT${NC}"
    fi
    
    echo -e "\n${YELLOW}🔧 TROUBLESHOOTING:${NC}"
    echo -e "   1. Check API connectivity: curl $BASE_URL/health"
    echo -e "   2. Verify environment variables are set"
    echo -e "   3. Check Python dependencies: $PIP_CMD list"
    echo -e "   4. Review logs above for specific errors"
    
    exit 1
fi

# Display additional information
echo -e "\n${CYAN}📋 TEST COVERAGE:${NC}"
echo -e "   ✅ Thread Generation (URL + Content)"
echo -e "   ✅ OpenAI API Integration"
echo -e "   ✅ PostgreSQL Data Storage"
echo -e "   ✅ User Authentication (JWT)"
echo -e "   ✅ Rate Limiting (Free vs Premium)"
echo -e "   ✅ Thread CRUD Operations"
echo -e "   ✅ Analytics Tracking"
echo -e "   ✅ Data Persistence Validation"

echo -e "\n${CYAN}🔍 MONITORED METRICS:${NC}"
echo -e "   📊 API Response Times"
echo -e "   💾 Database Connection Health"
echo -e "   🧠 AI Generation Success Rate"
echo -e "   🔐 Authentication Success Rate"
echo -e "   📈 Feature Completion Rate"

if [[ "$SKIP_CLEANUP" != "true" ]]; then
    echo -e "\n${GREEN}🧹 Cleanup completed automatically${NC}"
else
    echo -e "\n${YELLOW}⚠️  Test data cleanup SKIPPED (as requested)${NC}"
fi

echo -e "\n${GREEN}============================================================${NC}"
echo -e "${GREEN}✅ Business functionality testing completed successfully!${NC}"
echo -e "${GREEN}============================================================${NC}"