#!/bin/bash
# monitor-postgresql-deployment.sh
# Comprehensive monitoring script for Threadr PostgreSQL deployment on Render

BACKEND_URL="https://threadr-pw0s.onrender.com"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Monitoring Threadr PostgreSQL Deployment...${NC}"
echo -e "Backend URL: $BACKEND_URL"
echo -e "Timestamp: $(date)"
echo ""

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}⚠️  jq not found. Install with: brew install jq (macOS) or apt-get install jq (Ubuntu)${NC}"
    echo "Proceeding without JSON formatting..."
    JQ_AVAILABLE=false
else
    JQ_AVAILABLE=true
fi

# Function to format JSON output
format_json() {
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "$1" | jq .
    else
        echo "$1"
    fi
}

# 1. Basic Health Check
echo -e "${BLUE}1. 🏥 Health Check...${NC}"
HEALTH_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" $BACKEND_URL/health)
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -1 | sed 's/HTTP_CODE://')
HEALTH_BODY=$(echo "$HEALTH_RESPONSE" | sed '$d')

echo -e "HTTP Status: $HTTP_CODE"
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Health endpoint responding${NC}"
    format_json "$HEALTH_BODY"
else
    echo -e "${RED}❌ Health endpoint failed with HTTP $HTTP_CODE${NC}"
    echo "$HEALTH_BODY"
fi
echo ""

# 2. Readiness Check  
echo -e "${BLUE}2. 🎯 Readiness Check...${NC}"
READINESS_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" $BACKEND_URL/readiness)
HTTP_CODE=$(echo "$READINESS_RESPONSE" | tail -1 | sed 's/HTTP_CODE://')
READINESS_BODY=$(echo "$READINESS_RESPONSE" | sed '$d')

echo -e "HTTP Status: $HTTP_CODE"
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Readiness endpoint responding${NC}"
    format_json "$READINESS_BODY"
else
    echo -e "${RED}❌ Readiness endpoint failed with HTTP $HTTP_CODE${NC}"
    echo "$READINESS_BODY"
fi
echo ""

# 3. Database Status Verification
echo -e "${BLUE}3. 🗄️  Database Status Analysis...${NC}"
if [ "$JQ_AVAILABLE" = true ]; then
    DB_STATUS=$(echo "$HEALTH_BODY" | jq -r '.services.database // "unknown"')
    REDIS_STATUS=$(echo "$HEALTH_BODY" | jq -r '.services.redis // "unknown"')
    ROUTES_STATUS=$(echo "$HEALTH_BODY" | jq -r '.services.routes // "unknown"')
    OVERALL_STATUS=$(echo "$HEALTH_BODY" | jq -r '.status // "unknown"')
    
    echo -e "Overall Status: $OVERALL_STATUS"
    echo -e "Database Status: $DB_STATUS"
    echo -e "Redis Status: $REDIS_STATUS"
    echo -e "Routes Status: $ROUTES_STATUS"
    
    if [ "$DB_STATUS" = "true" ]; then
        echo -e "${GREEN}✅ PostgreSQL is ENABLED and healthy${NC}"
    else
        echo -e "${RED}❌ PostgreSQL is NOT working properly${NC}"
    fi
    
    if [ "$REDIS_STATUS" = "true" ]; then
        echo -e "${GREEN}✅ Redis is working${NC}"
    else
        echo -e "${YELLOW}⚠️  Redis is not available${NC}"
    fi
else
    # Fallback without jq
    if echo "$HEALTH_BODY" | grep -q '"database":true'; then
        echo -e "${GREEN}✅ PostgreSQL appears to be enabled${NC}"
    else
        echo -e "${RED}❌ PostgreSQL does not appear to be working${NC}"
    fi
fi
echo ""

# 4. Test Core Functionality  
echo -e "${BLUE}4. 🧪 Testing Core Thread Generation...${NC}"
GENERATE_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST $BACKEND_URL/api/generate \
  -H "Content-Type: application/json" \
  -d '{"content": "This is a test post to verify the API is working with PostgreSQL enabled."}')

HTTP_CODE=$(echo "$GENERATE_RESPONSE" | tail -1 | sed 's/HTTP_CODE://')
GENERATE_BODY=$(echo "$GENERATE_RESPONSE" | sed '$d')

echo -e "HTTP Status: $HTTP_CODE"
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Thread generation working${NC}"
    # Don't show full response, just confirm it worked
    if [ "$JQ_AVAILABLE" = true ]; then
        THREAD_COUNT=$(echo "$GENERATE_BODY" | jq -r '.thread | length // 0')
        echo "Generated threads: $THREAD_COUNT"
    else
        echo "Thread generation successful"
    fi
else
    echo -e "${RED}❌ Thread generation failed with HTTP $HTTP_CODE${NC}"
    echo "$GENERATE_BODY"
fi
echo ""

# 5. Test User Authentication Endpoints
echo -e "${BLUE}5. 🔐 Testing Database-Dependent Authentication...${NC}"

# Test user registration (should create record in PostgreSQL)
echo -e "Testing user registration..."
REGISTER_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST $BACKEND_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test-db-'$(date +%s)'@example.com",
    "password": "TestPassword123!",
    "full_name": "Database Test User"
  }')

HTTP_CODE=$(echo "$REGISTER_RESPONSE" | tail -1 | sed 's/HTTP_CODE://')
REGISTER_BODY=$(echo "$REGISTER_RESPONSE" | sed '$d')

echo -e "Registration HTTP Status: $HTTP_CODE"
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    echo -e "${GREEN}✅ User registration working (PostgreSQL write test passed)${NC}"
    if [ "$JQ_AVAILABLE" = true ]; then
        USER_EMAIL=$(echo "$REGISTER_BODY" | jq -r '.user.email // "unknown"')
        echo "Registered user: $USER_EMAIL"
    fi
else
    echo -e "${RED}❌ User registration failed with HTTP $HTTP_CODE${NC}"
    echo "$REGISTER_BODY"
fi
echo ""

# 6. Summary
echo -e "${BLUE}📊 DEPLOYMENT SUMMARY${NC}"
echo "=========================="
echo -e "Backend URL: $BACKEND_URL"
echo -e "Health Check: $([ "$HTTP_CODE" = "200" ] && echo "${GREEN}PASS${NC}" || echo "${RED}FAIL${NC}")"

if [ "$JQ_AVAILABLE" = true ] && [ ! -z "$DB_STATUS" ]; then
    echo -e "Database Status: $([ "$DB_STATUS" = "true" ] && echo "${GREEN}ENABLED${NC}" || echo "${RED}DISABLED${NC}")"
    echo -e "Redis Status: $([ "$REDIS_STATUS" = "true" ] && echo "${GREEN}WORKING${NC}" || echo "${YELLOW}UNAVAILABLE${NC}")"
else
    echo -e "Database Status: ${YELLOW}UNKNOWN (install jq for detailed status)${NC}"
fi

echo ""
echo -e "${BLUE}🎯 Monitoring Complete!${NC}"
echo ""
echo -e "${YELLOW}💡 Next Steps:${NC}"
echo -e "   1. If database shows ENABLED: Begin frontend auth integration"
echo -e "   2. If database shows DISABLED: Check Render deployment logs"
echo -e "   3. Monitor response times for performance impact"
echo -e "   4. Test more complex database operations"