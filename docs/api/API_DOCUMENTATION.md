# Threadr API Documentation

Base URL: `https://your-backend.railway.app`

## Endpoints

### Health Check
```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Generate Thread
```
POST /api/generate
```

Generate a Twitter/X thread from a URL or text content.

#### Request Body

Option 1 - From URL:
```json
{
  "url": "https://example.com/article"
}
```

Option 2 - From Text:
```json
{
  "text": "Your article content here..."
}
```

#### Response
```json
{
  "success": true,
  "thread": [
    {
      "number": 1,
      "total": 5,
      "content": "1/5 🧵 Here's an interesting article...",
      "character_count": 45
    }
  ],
  "source_type": "url",
  "title": "Article Title",
  "error": null
}
```

#### Error Responses

Rate Limit Exceeded (429):
```json
{
  "detail": "Rate limit exceeded. Try again in 45 minutes."
}
```

Bad Request (400):
```json
{
  "detail": "Failed to fetch URL: Connection error"
}
```

### Rate Limit Status
```
GET /api/rate-limit-status
```

Check your current rate limit status.

Response:
```json
{
  "requests_used": 3,
  "requests_remaining": 7,
  "total_limit": 10,
  "window_hours": 1,
  "minutes_until_reset": 45
}
```

## Rate Limiting

- Default: 10 requests per hour per IP address
- Rate limits are configurable via environment variables
- Use the rate limit status endpoint to check your current usage

## CORS

CORS is configured to allow requests from specified origins. In production, update the `CORS_ORIGINS` environment variable with your frontend domain.

## Authentication

Currently, the API uses IP-based rate limiting. No API keys are required for basic usage.

## Error Handling

All errors follow this format:
```json
{
  "detail": "Error description"
}
```

Common HTTP status codes:
- 200: Success
- 400: Bad Request (invalid input)
- 429: Rate Limit Exceeded
- 500: Internal Server Error