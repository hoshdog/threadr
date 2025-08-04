# Threadr API Documentation

**MIGRATION NOTE (2025-08-04)**: This API documentation remains unchanged during the Next.js migration. The FastAPI backend is stable and all endpoints continue to work identically.

Base URL: `https://threadr-production.up.railway.app`  
**Frontend Migration**: Alpine.js → Next.js (backend APIs unchanged)

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

- **Production**: 5 daily / 20 monthly requests (free tier)
- **Premium**: Unlimited requests ($4.99 for 30 days)
- Rate limits are IP-based and stored in Redis
- Use the rate limit status endpoint to check current usage

## Integration with Next.js Frontend

### TypeScript API Client Example

```typescript
// lib/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'https://threadr-production.up.railway.app',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add JWT token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export { apiClient };
```

### React Query Integration

```typescript
// hooks/useThreadGeneration.ts
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';

interface GenerateThreadRequest {
  text?: string;
  url?: string;
}

export const useGenerateThread = () => {
  return useMutation({
    mutationFn: async (data: GenerateThreadRequest) => {
      const response = await apiClient.post('/api/generate', data);
      return response.data;
    },
  });
};
```

### Usage in Next.js Components

```tsx
// components/thread/ThreadGenerator.tsx
import { useGenerateThread } from '@/hooks/useThreadGeneration';

export default function ThreadGenerator() {
  const generateThread = useGenerateThread();
  
  const handleSubmit = (data: { text: string }) => {
    generateThread.mutate({ text: data.text });
  };
  
  return (
    <div>
      {generateThread.isLoading && <p>Generating thread...</p>}
      {generateThread.data && (
        <div>
          {generateThread.data.thread.map((tweet, index) => (
            <div key={index}>{tweet.content}</div>
          ))}
        </div>
      )}
    </div>
  );
}
```

## Migration Impact

**No Changes Required**:
- All API endpoints remain identical
- Authentication flows unchanged
- Rate limiting continues to work
- CORS configuration supports both Alpine.js and Next.js apps

**Frontend Benefits**:
- Type-safe API calls with TypeScript
- Better error handling with React Query
- Automatic retries and caching
- Optimistic updates for better UX

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