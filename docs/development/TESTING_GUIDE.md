# Threadr API Testing Guide

This comprehensive guide will help you test the Threadr FastAPI backend deployed on Railway. The backend converts articles and text into Twitter/X threads.

## 🚀 Quick Start Information

**Railway URL:** `https://threadr-production.up.railway.app`

**API Keys:** 
- `zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8`
- `FFAvIrarUm32RGDntib20DzSU21-B_zJ4w8mzaSz1So`

**Rate Limits:** 50 requests per hour per IP address

**CORS Origins:** Configured for `https://threadr-plum.vercel.app/`

---

## 📋 Test Categories

### 1. Health Checks (Public Endpoints)

These endpoints don't require authentication and should always return 200 OK if the service is running.

#### Basic Health Check
```bash
curl -X GET "https://threadr-production.up.railway.app/health" \
  -H "Accept: application/json"
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-30T12:00:00.000Z",
  "version": "1.0.0",
  "environment": "production",
  "message": "Threadr API is running"
}
```

**✅ Success Indicators:**
- Status code: `200 OK`
- Response contains `"status": "healthy"`
- Timestamp is recent

**❌ Failure Indicators:**
- Status code other than 200
- No response or timeout
- Status not "healthy"

#### Readiness Check
```bash
curl -X GET "https://threadr-production.up.railway.app/readiness" \
  -H "Accept: application/json"
```

**Expected Response:**
```json
{
  "status": "ready",
  "timestamp": "2025-07-30T12:00:00.000Z",
  "checks": {
    "basic_functionality": "passed",
    "openai_service": "configured"
  }
}
```

**✅ Success Indicators:**
- Status code: `200 OK`
- `"status": "ready"`
- `basic_functionality`: `"passed"`

#### Root Path Health Check
```bash
curl -X GET "https://threadr-production.up.railway.app/" \
  -H "Accept: application/json"
```

**Expected Response:** Same as `/health` endpoint

---

### 2. API Authentication Tests

The main API endpoint requires an `X-API-Key` header for authentication.

#### Test Without API Key (Should Fail)
```bash
curl -X POST "https://threadr-production.up.railway.app/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"text": "This should fail without API key"}'
```

**Expected Response:**
```json
{
  "detail": "API key required. Please provide X-API-Key header."
}
```

**✅ Success Indicators:**
- Status code: `401 Unauthorized`
- Error message mentions API key requirement
- `WWW-Authenticate: ApiKey` header present

#### Test With Invalid API Key (Should Fail)
```bash
curl -X POST "https://threadr-production.up.railway.app/api/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: invalid-key-12345" \
  -d '{"text": "This should fail with invalid key"}'
```

**Expected Response:**
```json
{
  "detail": "Invalid API key"
}
```

**✅ Success Indicators:**
- Status code: `401 Unauthorized`
- Error message indicates invalid API key

#### Test With Valid API Key (Should Succeed)
```bash
curl -X POST "https://threadr-production.up.railway.app/api/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8" \
  -d '{"text": "This is a test message to verify API key authentication is working correctly. It should be split into multiple tweets if long enough."}'
```

**✅ Success Indicators:**
- Status code: `200 OK`
- Response contains thread data
- No authentication errors

---

### 3. Thread Generation Tests

#### Generate Thread from Text Content
```bash
curl -X POST "https://threadr-production.up.railway.app/api/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8" \
  -d '{
    "text": "Artificial intelligence is transforming the way we work and live. From automating routine tasks to enabling new forms of creativity, AI is becoming an integral part of our daily lives. Machine learning algorithms can now process vast amounts of data to identify patterns and make predictions that were previously impossible. This technology is being applied across industries, from healthcare and finance to transportation and entertainment. However, with great power comes great responsibility, and we must ensure that AI development prioritizes safety, fairness, and transparency."
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "thread": [
    {
      "number": 1,
      "total": 3,
      "content": "1/3 Artificial intelligence is transforming the way we work and live. From automating routine tasks to enabling new forms of creativity, AI is becoming an integral part of our daily lives.",
      "character_count": 187
    },
    {
      "number": 2,
      "total": 3,
      "content": "2/3 Machine learning algorithms can now process vast amounts of data to identify patterns and make predictions that were previously impossible. This technology is being applied across industries...",
      "character_count": 245
    },
    {
      "number": 3,
      "total": 3,
      "content": "3/3 However, with great power comes great responsibility, and we must ensure that AI development prioritizes safety, fairness, and transparency.",
      "character_count": 142
    }
  ],
  "source_type": "text",
  "title": null,
  "error": null
}
```

**✅ Success Indicators:**
- Status code: `200 OK`
- `"success": true`
- Thread array contains multiple tweets
- Each tweet has proper numbering (1/n, 2/n, etc.)
- Character counts are ≤ 280
- `source_type`: `"text"`

#### Generate Thread from URL
```bash
curl -X POST "https://threadr-production.up.railway.app/api/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8" \
  -d '{
    "url": "https://blog.openai.com/chatgpt"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "thread": [
    {
      "number": 1,
      "total": 4,
      "content": "1/4 Introducing ChatGPT - A new AI assistant that can engage in conversational interactions...",
      "character_count": 156
    }
  ],
  "source_type": "url",
  "title": "Introducing ChatGPT",
  "error": null
}
```

**✅ Success Indicators:**
- Status code: `200 OK`
- `"success": true`
- `source_type`: `"url"`
- `title` field populated (if article has title)
- Thread properly generated from scraped content

#### Test URL Domain Restrictions
```bash
curl -X POST "https://threadr-production.up.railway.app/api/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8" \
  -d '{
    "url": "https://malicious-site.com/article"
  }'
```

**Expected Response:**
```json
{
  "detail": "Domain not allowed. Allowed domains include: medium.com, any subdomain of medium.com, dev.to, any subdomain of dev.to, and 12 more..."
}
```

**✅ Success Indicators:**
- Status code: `403 Forbidden`
- Error mentions domain restrictions
- Lists allowed domains

#### Test Invalid URL Format
```bash
curl -X POST "https://threadr-production.up.railway.app/api/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8" \
  -d '{
    "url": "not-a-valid-url"
  }'
```

**Expected Response:**
```json
{
  "detail": [
    {
      "type": "url_parsing",
      "loc": ["body", "url"],
      "msg": "invalid or missing URL scheme",
      "input": "not-a-valid-url"
    }
  ]
}
```

**✅ Success Indicators:**
- Status code: `422 Unprocessable Entity`
- Validation error for URL format

---

### 4. Rate Limiting Tests

#### Check Current Rate Limit Status
```bash
curl -X GET "https://threadr-production.up.railway.app/api/rate-limit-status" \
  -H "Accept: application/json"
```

**Expected Response:**
```json
{
  "requests_used": 1,
  "requests_remaining": 49,
  "total_limit": 50,
  "window_hours": 1,
  "minutes_until_reset": 0,
  "using_redis": true
}
```

**✅ Success Indicators:**
- Status code: `200 OK`
- `total_limit`: `50`
- `window_hours`: `1`
- `requests_remaining` decreases with each request

#### Test Rate Limit Enforcement

**⚠️ Warning:** This test will consume your rate limit quickly. Use with caution.

Create a script to make multiple requests:

```bash
#!/bin/bash
for i in {1..55}; do
  echo "Request $i:"
  curl -X POST "https://threadr-production.up.railway.app/api/generate" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8" \
    -d '{"text": "Rate limit test message"}' \
    -w "\nStatus: %{http_code}\n\n"
  
  if [ $i -gt 50 ]; then
    echo "Should be rate limited now..."
  fi
done
```

**Expected Behavior:**
- First 50 requests: `200 OK`
- Requests 51+: `429 Too Many Requests`

**Rate Limited Response:**
```json
{
  "detail": "Rate limit exceeded. Try again in 60 minutes."
}
```

**✅ Success Indicators:**
- Rate limiting kicks in after 50 requests
- Status code: `429 Too Many Requests`
- Error message indicates when to retry

---

### 5. CORS Headers Verification

#### Test CORS Preflight Request
```bash
curl -X OPTIONS "https://threadr-production.up.railway.app/api/generate" \
  -H "Origin: https://threadr-plum.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: X-API-Key,Content-Type" \
  -v
```

**✅ Success Indicators:**
- Status code: `200 OK`
- `Access-Control-Allow-Origin: https://threadr-plum.vercel.app`
- `Access-Control-Allow-Methods` includes `POST`
- `Access-Control-Allow-Headers` includes `X-API-Key`

#### Test CORS with Allowed Origin
```bash
curl -X POST "https://threadr-production.up.railway.app/api/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8" \
  -H "Origin: https://threadr-plum.vercel.app" \
  -d '{"text": "CORS test message"}' \
  -v
```

**✅ Success Indicators:**
- Status code: `200 OK`
- `Access-Control-Allow-Origin` header present in response
- No CORS-related errors

#### Test CORS with Disallowed Origin
```bash
curl -X POST "https://threadr-production.up.railway.app/api/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8" \
  -H "Origin: https://malicious-site.com" \
  -d '{"text": "CORS test message"}' \
  -v
```

**Expected Behavior:**
- CORS error in browser (curl will still work)
- Missing or incorrect `Access-Control-Allow-Origin` header

---

### 6. Additional Test Endpoints

#### Test API Functionality
```bash
curl -X GET "https://threadr-production.up.railway.app/api/test" \
  -H "Accept: application/json"
```

**Expected Response:**
```json
{
  "status": "working",
  "timestamp": "2025-07-30T12:00:00.000Z",
  "test_result": {
    "input_length": 87,
    "tweets_generated": 1,
    "sample_tweet": "This is a test message to verify the API is working correctly."
  },
  "openai_status": "available"
}
```

#### Cache Statistics
```bash
curl -X GET "https://threadr-production.up.railway.app/api/cache/stats" \
  -H "Accept: application/json"
```

**Expected Response:**
```json
{
  "available": true,
  "total_keys": 42,
  "memory_usage": "1.2MB",
  "hit_rate": 0.75,
  "uptime_seconds": 3600
}
```

#### Comprehensive Health Monitor
```bash
curl -X GET "https://threadr-production.up.railway.app/api/monitor/health" \
  -H "Accept: application/json"
```

**Expected Response:**
```json
{
  "timestamp": "2025-07-30T12:00:00.000Z",
  "status": "healthy",
  "services": {
    "api": "healthy",
    "openai": "healthy",
    "redis": "healthy",
    "basic_functionality": "healthy"
  },
  "details": {
    "redis": {
      "total_keys": 42,
      "memory_usage": "1.2MB"
    },
    "environment": "production",
    "uptime_seconds": 3600
  }
}
```

---

## 🔧 Testing Scripts

### Automated Test Script

Save this as `test-threadr-api.sh`:

```bash
#!/bin/bash

BASE_URL="https://threadr-production.up.railway.app"
API_KEY="zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8"

echo "🚀 Testing Threadr API on Railway"
echo "================================="

echo -e "\n1. Testing Health Endpoints..."
echo "✓ Basic health check:"
curl -s "$BASE_URL/health" | jq -r '.status'

echo "✓ Readiness check:"
curl -s "$BASE_URL/readiness" | jq -r '.status'

echo -e "\n2. Testing Authentication..."
echo "✗ No API key (should fail):"
curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"text": "test"}'

echo -e "\n✓ Valid API key (should succeed):"
curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"text": "This is a test message for authentication."}'

echo -e "\n3. Testing Thread Generation..."
echo "✓ Text to thread:"
curl -s -X POST "$BASE_URL/api/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"text": "This is a comprehensive test of the thread generation functionality."}' \
  | jq -r '.success'

echo -e "\n4. Testing Rate Limits..."
echo "✓ Rate limit status:"
curl -s "$BASE_URL/api/rate-limit-status" | jq -r '.requests_remaining'

echo -e "\n5. Testing Additional Endpoints..."
echo "✓ API test endpoint:"
curl -s "$BASE_URL/api/test" | jq -r '.status'

echo "✓ Cache stats:"
curl -s "$BASE_URL/api/cache/stats" | jq -r '.available'

echo -e "\n🎉 All tests completed!"
```

Make it executable: `chmod +x test-threadr-api.sh`

---

## 🚨 Troubleshooting

### Common Issues and Solutions

1. **503 Service Unavailable**
   - Check if Railway deployment is running
   - Verify environment variables are set
   - Check Railway logs for startup errors

2. **401 Authentication Errors**
   - Verify API key is correct
   - Check `X-API-Key` header is properly set
   - Ensure no extra spaces in API key

3. **429 Rate Limited**
   - Wait for rate limit window to reset (1 hour)
   - Check rate limit status endpoint
   - Use different IP address if testing

4. **400 Bad Request for URLs**
   - Verify URL is properly formatted
   - Check if domain is in allowed list
   - Ensure URL is accessible

5. **CORS Errors**
   - Verify origin matches configured CORS origins
   - Check if preflight requests are being sent
   - Ensure proper headers are included

### Rate Limit Reset

If you exhaust your rate limit during testing, you can:
1. Wait 1 hour for automatic reset
2. Use a different IP address (VPN/mobile hotspot)
3. Contact system administrator to clear rate limits

---

## 📊 Success Metrics

A fully functional API should show:

- ✅ All health checks return `200 OK`
- ✅ Authentication properly blocks unauthorized requests
- ✅ Thread generation works for both text and URLs
- ✅ Rate limiting enforces 50 requests/hour limit
- ✅ CORS headers allow configured origins
- ✅ All endpoints return proper status codes
- ✅ Response times under 5 seconds for thread generation
- ✅ No 5xx server errors during normal operation

---

## 🔍 Monitoring Commands

### Check API Status
```bash
curl -s https://threadr-production.up.railway.app/health | jq
```

### Monitor Rate Limits
```bash
curl -s https://threadr-production.up.railway.app/api/rate-limit-status | jq
```

### Full System Health
```bash
curl -s https://threadr-production.up.railway.app/api/monitor/health | jq
```

This comprehensive testing guide should help you verify all aspects of the Threadr API functionality. Remember to replace the API keys with your actual keys and adjust the Railway URL if it changes.