# Threadr API Quick Reference

## Base URL
```
https://threadr-production.up.railway.app
```

## Authentication
All requests to `/api/generate` require an API key:
```bash
X-API-Key: your-api-key-here
```

## Core Endpoints

### Generate Thread
```bash
POST /api/generate
Content-Type: application/json
X-API-Key: <your-api-key>

# From text
{
  "text": "Your content here..."
}

# From URL (when implemented)  
{
  "url": "https://example.com/article"
}
```

**Response:**
```json
{
  "success": true,
  "thread": [
    {
      "number": 1,
      "total": 3,
      "content": "1/3 Your content split into tweets...",
      "character_count": 42
    }
  ],
  "source_type": "text",
  "title": null
}
```

### Health Check
```bash
GET /health
```

### Rate Limit Status  
```bash
GET /api/rate-limit-status
```

**Response:**
```json
{
  "requests_used": 2,
  "requests_remaining": 8,
  "total_limit": 10,
  "window_hours": 1,
  "minutes_until_reset": 45
}
```

### Cache Statistics
```bash
GET /api/cache/stats
```

## Working Examples

### Basic Thread Generation
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"text": "This is a sample text that will be converted into a Twitter thread format with proper character limits and numbering."}' \
  "https://threadr-production.up.railway.app/api/generate"
```

### Check API Status
```bash
curl "https://threadr-production.up.railway.app/health"
```

### Monitor Rate Limits
```bash
curl "https://threadr-production.up.railway.app/api/rate-limit-status"
```

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "API key required. Please provide X-API-Key header."
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body"],
      "msg": "Either 'url' or 'text' must be provided"
    }
  ]
}
```

### 429 Rate Limited
```json
{
  "detail": "Rate limit exceeded. Try again in 45 minutes."
}
```

## Rate Limits
- **10 requests per hour** per IP address
- Uses Redis for distributed rate limiting
- Fallback to in-memory if Redis unavailable

## Features
- ✅ Text to Twitter thread conversion
- ✅ API key authentication  
- ✅ Rate limiting protection
- ✅ Redis caching
- ✅ Security headers
- ✅ CORS support
- ✅ Comprehensive monitoring

## Production Ready
- **Status**: ✅ READY
- **Uptime**: High availability on Railway
- **Security**: API key authentication + security headers
- **Performance**: ~3.6s average response time
- **Monitoring**: Health checks and metrics available