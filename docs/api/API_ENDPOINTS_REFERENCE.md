# API Endpoints Reference

Complete reference for all Threadr API endpoints in production.

## Base URL
- **Production**: `https://threadr-production.up.railway.app`
- **Local Development**: `http://localhost:8001`

## Authentication

Most endpoints require API key authentication:

```bash
curl -H "X-API-Key: your-api-key-here"
```

## Core Endpoints

### 1. Generate Thread
**POST** `/api/generate`

Converts a URL or text into a Twitter/X thread.

**Request Body:**
```json
{
  "url": "https://medium.com/@example/article",
  // OR
  "text": "Your article content here..."
}
```

**Response:**
```json
{
  "success": true,
  "thread": [
    {
      "number": 1,
      "total": 5,
      "content": "1/5 First tweet content...",
      "character_count": 250
    }
  ],
  "source_type": "url",
  "title": "Article Title",
  "error": null
}
```

**Headers Required:**
- `Content-Type: application/json`
- `X-API-Key: your-api-key`

**Error Responses:**
- `400` - Bad request (invalid URL or empty content)
- `401` - Missing or invalid API key
- `403` - Domain not allowed for scraping
- `429` - Rate limit exceeded
- `500` - Internal server error

## Health & Status Endpoints

### 2. Health Check
**GET** `/health`

Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-31T03:07:11.922765",
  "version": "1.0.0",
  "environment": "production",
  "message": "Threadr API is running"
}
```

**No authentication required**

### 3. Readiness Check
**GET** `/readiness`

Kubernetes-style readiness probe.

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2025-07-31T03:07:11.922765",
  "checks": {
    "api": true,
    "redis": true
  }
}
```

### 4. Monitor Health
**GET** `/api/monitor/health`

Detailed health monitoring endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-31T03:07:11.922765",
  "uptime_seconds": 3600,
  "environment": "production",
  "services": {
    "api": "operational",
    "redis": "operational",
    "openai": "operational"
  }
}
```

## Utility Endpoints

### 5. Rate Limit Status
**GET** `/api/rate-limit-status`

Check your current rate limit status.

**Headers Required:**
- `X-API-Key: your-api-key`

**Response:**
```json
{
  "requests_made": 25,
  "requests_remaining": 25,
  "reset_time": "2025-07-31T04:00:00Z",
  "window_hours": 1
}
```

### 6. Cache Statistics
**GET** `/api/cache/stats`

Get cache performance statistics.

**Headers Required:**
- `X-API-Key: your-api-key`

**Response:**
```json
{
  "total_requests": 1000,
  "cache_hits": 750,
  "cache_misses": 250,
  "hit_rate": 0.75,
  "cached_items": 150
}
```

### 7. Clear Cache
**POST** `/api/cache/clear`

Clear the cache (admin only).

**Headers Required:**
- `X-API-Key: admin-api-key`

**Response:**
```json
{
  "status": "success",
  "message": "Cache cleared successfully"
}
```

## Test Endpoints (Development Only)

These endpoints return 404 in production:

### 8. API Test
**GET** `/api/test`

Test basic API functionality.

### 9. URL Check Test
**POST** `/api/test/url-check`

Test URL validation and domain checking.

### 10. Network Test
**GET** `/api/test/railway-network`

Test network connectivity from Railway.

## Rate Limiting

Default rate limits:
- **50 requests per hour** per API key
- **10 requests per hour** for unauthenticated requests

Rate limit headers in response:
```
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1701234567
```

## Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

Common error messages:
- `"API key required. Please provide X-API-Key header."`
- `"Rate limit exceeded. Try again in X minutes."`
- `"Domain not allowed. Allowed domains include: ..."`
- `"Invalid URL format"`
- `"Content too short to create a thread"`

## Allowed Domains for Scraping

The following domains are allowed for URL scraping:
- medium.com (and subdomains)
- dev.to (and subdomains)
- substack.com (and subdomains)
- hashnode.com (and subdomains)
- wordpress.com (and subdomains)
- blogger.com (and subdomains)
- ghost.io (and subdomains)
- github.com (and subdomains)
- notion.so
- linkedin.com (and subdomains)
- twitter.com / x.com

## Example Usage

### Generate Thread from URL
```bash
curl -X POST https://threadr-production.up.railway.app/api/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"url": "https://medium.com/@example/great-article"}'
```

### Generate Thread from Text
```bash
curl -X POST https://threadr-production.up.railway.app/api/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"text": "Your long article content here..."}'
```

### Check Health
```bash
curl https://threadr-production.up.railway.app/health
```

## SDK Examples

### JavaScript/TypeScript
```javascript
const response = await fetch('https://threadr-production.up.railway.app/api/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-api-key'
  },
  body: JSON.stringify({
    url: 'https://medium.com/@example/article'
  })
});

const data = await response.json();
console.log(data.thread);
```

### Python
```python
import requests

response = requests.post(
    'https://threadr-production.up.railway.app/api/generate',
    headers={
        'Content-Type': 'application/json',
        'X-API-Key': 'your-api-key'
    },
    json={
        'url': 'https://medium.com/@example/article'
    }
)

data = response.json()
print(data['thread'])
```

## Best Practices

1. **Always include API key** in production requests
2. **Handle rate limits** gracefully with exponential backoff
3. **Cache responses** when possible to reduce API calls
4. **Validate URLs** before sending to API
5. **Handle errors** appropriately in your application
6. **Use HTTPS** for all API calls

## Support

For API issues or questions:
1. Check the [Troubleshooting Guide](../deployment/DEPLOYMENT_TROUBLESHOOTING_GUIDE.md)
2. Review error messages carefully
3. Test with curl first to isolate issues