#!/bin/bash

# Threadr Production API Test Suite
# Tests all features of the deployed API at https://threadr-production.up.railway.app

BASE_URL="https://threadr-production.up.railway.app"
API_KEY_1="zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8"
API_KEY_2="FFAvIrarUm32RGDntib20DzSU21-B_zJ4w8mzaSz1So"
INVALID_KEY="invalid-key-for-testing"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

log_failure() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

log_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Test function wrapper
run_test() {
    local test_name="$1"
    local test_function="$2"
    
    log_test "$test_name"
    if $test_function; then
        log_success "$test_name"
    else
        log_failure "$test_name"
    fi
    echo ""
}

# Validate JSON response
validate_json() {
    local response="$1"
    if echo "$response" | jq . >/dev/null 2>&1; then
        return 0
    else
        log_info "Invalid JSON response: $response"
        return 1
    fi
}

# Check HTTP status code
check_status() {
    local expected="$1"
    local actual="$2"
    if [[ "$actual" == "$expected" ]]; then
        return 0
    else
        log_info "Expected status $expected, got $actual"
        return 1
    fi
}

# TEST IMPLEMENTATIONS

test_health_endpoint() {
    local response=$(curl -s -w "%{http_code}" "$BASE_URL/health")
    local body="${response%???}"
    local status="${response: -3}"
    
    check_status "200" "$status" && validate_json "$body" && \
    echo "$body" | jq -e '.status == "healthy"' >/dev/null
}

test_readiness_endpoint() {
    local response=$(curl -s -w "%{http_code}" "$BASE_URL/readiness")
    local body="${response%???}"
    local status="${response: -3}"
    
    check_status "200" "$status" && validate_json "$body" && \
    echo "$body" | jq -e '.status == "ready"' >/dev/null
}

test_monitor_health() {
    local response=$(curl -s -w "%{http_code}" "$BASE_URL/api/monitor/health")
    local body="${response%???}"
    local status="${response: -3}"
    
    check_status "200" "$status" && validate_json "$body" && \
    echo "$body" | jq -e '.status == "healthy" and .services' >/dev/null
}

test_test_endpoint() {
    local response=$(curl -s -w "%{http_code}" "$BASE_URL/api/test")
    local body="${response%???}"
    local status="${response: -3}"
    
    check_status "200" "$status" && validate_json "$body" && \
    echo "$body" | jq -e '.status == "working"' >/dev/null
}

test_auth_no_key() {
    local response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d '{"text": "Test authentication without API key"}' \
        "$BASE_URL/api/generate")
    local status="${response: -3}"
    
    check_status "401" "$status"
}

test_auth_invalid_key() {
    local response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $INVALID_KEY" \
        -d '{"text": "Test authentication with invalid API key"}' \
        "$BASE_URL/api/generate")
    local status="${response: -3}"
    
    check_status "401" "$status"
}

test_auth_valid_key() {
    local response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY_1" \
        -d '{"text": "Test authentication with valid API key"}' \
        "$BASE_URL/api/generate")
    local body="${response%???}"
    local status="${response: -3}"
    
    check_status "200" "$status" && validate_json "$body" && \
    echo "$body" | jq -e '.success == true and .thread' >/dev/null
}

test_generate_thread_from_text() {
    local test_text="This is a comprehensive test of the thread generation functionality. It should be split into multiple tweets based on the 280 character limit. The system should handle this gracefully and create a properly numbered thread with appropriate content distribution."
    
    local response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY_1" \
        -d "{\"text\": \"$test_text\"}" \
        "$BASE_URL/api/generate")
    local body="${response%???}"
    local status="${response: -3}"
    
    check_status "200" "$status" && validate_json "$body" && \
    echo "$body" | jq -e '.success == true and .thread and (.thread | length > 1) and .source_type == "text"' >/dev/null
}

test_generate_thread_from_url() {
    local test_url="https://medium.com/@test/sample-article"
    
    local response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY_1" \
        -d "{\"url\": \"$test_url\"}" \
        "$BASE_URL/api/generate")
    local body="${response%???}"
    local status="${response: -3}"
    
    # URL may fail to fetch (expected), but should return proper error structure
    validate_json "$body" && \
    echo "$body" | jq -e 'has("success")' >/dev/null
}

test_rate_limit_status() {
    local response=$(curl -s -w "%{http_code}" "$BASE_URL/api/rate-limit-status")
    local body="${response%???}"
    local status="${response: -3}"
    
    check_status "200" "$status" && validate_json "$body" && \
    echo "$body" | jq -e 'has("requests_used") and has("requests_remaining") and has("total_limit")' >/dev/null
}

test_cache_stats() {
    local response=$(curl -s -w "%{http_code}" "$BASE_URL/api/cache/stats")
    local body="${response%???}"
    local status="${response: -3}"
    
    check_status "200" "$status" && validate_json "$body" && \
    echo "$body" | jq -e 'has("available")' >/dev/null
}

test_security_headers() {
    local response=$(curl -s -I "$BASE_URL/health")
    
    echo "$response" | grep -q "X-Content-Type-Options: nosniff" && \
    echo "$response" | grep -q "X-Frame-Options: DENY" && \
    echo "$response" | grep -q "X-XSS-Protection: 1; mode=block" && \
    echo "$response" | grep -q "Content-Security-Policy:"
}

test_cors_headers() {
    local response=$(curl -s -I -H "Origin: https://example.com" "$BASE_URL/health")
    
    echo "$response" | grep -q "Access-Control-Allow"
}

test_invalid_request_format() {
    local response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY_1" \
        -d '{"invalid": "request"}' \
        "$BASE_URL/api/generate")
    local status="${response: -3}"
    
    check_status "422" "$status"
}

test_empty_text() {
    local response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY_1" \
        -d '{"text": ""}' \
        "$BASE_URL/api/generate")
    local status="${response: -3}"
    
    check_status "422" "$status"
}

test_both_url_and_text() {
    local response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY_1" \
        -d '{"text": "Test", "url": "https://example.com"}' \
        "$BASE_URL/api/generate")
    local status="${response: -3}"
    
    check_status "422" "$status"
}

test_performance_simple_text() {
    local start_time=$(date +%s%N)
    
    local response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY_1" \
        -d '{"text": "Quick performance test of the API"}' \
        "$BASE_URL/api/generate")
    
    local end_time=$(date +%s%N)
    local duration=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
    local status="${response: -3}"
    
    log_info "API response time: ${duration}ms"
    
    check_status "200" "$status" && [[ $duration -lt 5000 ]] # Should respond within 5 seconds
}

# MAIN TEST EXECUTION

echo "==================================="
echo "Threadr Production API Test Suite"
echo "Testing: $BASE_URL"
echo "==================================="
echo ""

# Prerequisites check
log_info "Checking prerequisites..."
if ! command -v curl &> /dev/null; then
    echo "ERROR: curl is required but not installed"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "ERROR: jq is required but not installed"
    exit 1
fi

echo ""

# Basic Health Tests
echo "--- HEALTH & MONITORING TESTS ---"
run_test "Health endpoint responds correctly" test_health_endpoint
run_test "Readiness endpoint responds correctly" test_readiness_endpoint
run_test "Monitor health endpoint provides detailed status" test_monitor_health
run_test "Test endpoint confirms API functionality" test_test_endpoint

# Authentication Tests
echo "--- AUTHENTICATION TESTS ---"
run_test "Reject requests without API key" test_auth_no_key
run_test "Reject requests with invalid API key" test_auth_invalid_key
run_test "Accept requests with valid API key" test_auth_valid_key

# Core Functionality Tests
echo "--- THREAD GENERATION TESTS ---"
run_test "Generate thread from text content" test_generate_thread_from_text
run_test "Handle URL input (may fail gracefully)" test_generate_thread_from_url

# Rate Limiting & Caching Tests
echo "--- RATE LIMITING & CACHING TESTS ---"
run_test "Rate limit status endpoint works" test_rate_limit_status
run_test "Cache stats endpoint responds" test_cache_stats

# Security Tests
echo "--- SECURITY TESTS ---"
run_test "Security headers are present" test_security_headers
run_test "CORS headers are configured" test_cors_headers

# Error Handling Tests
echo "--- ERROR HANDLING TESTS ---"
run_test "Reject invalid request format" test_invalid_request_format
run_test "Reject empty text input" test_empty_text
run_test "Reject both URL and text in same request" test_both_url_and_text

# Performance Tests
echo "--- PERFORMANCE TESTS ---"
run_test "API responds within acceptable time" test_performance_simple_text

# FINAL RESULTS
echo "==================================="
echo "TEST RESULTS SUMMARY"
echo "==================================="
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
echo "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! The API is production ready.${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please review the failures above.${NC}"
    exit 1
fi