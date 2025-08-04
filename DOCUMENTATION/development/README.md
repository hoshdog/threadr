# Development Documentation

> **🛠️ DEVELOPMENT GUIDE**: Complete development workflow for Threadr project

## Development Environment Setup

### Prerequisites
- **Python 3.11+**: Backend development
- **Node.js 18+**: Frontend development (Next.js)
- **Git**: Version control
- **Redis**: Local development database
- **OpenAI API Key**: For thread generation testing
- **Stripe Account**: For payment testing

### Quick Start Guide

#### Backend Setup (FastAPI)
```bash
# Clone repository
git clone https://github.com/hoshdog/threadr.git
cd threadr

# Set up Python environment
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration

# Run development server
uvicorn src.main:app --reload --port 8001
# Backend available at http://localhost:8001
```

#### Frontend Setup (Next.js - Future)
```bash
# Navigate to Next.js project
cd threadr-nextjs

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with backend URL and configuration

# Run development server
npm run dev
# Frontend available at http://localhost:3000
```

#### Frontend Setup (Alpine.js - Current Production)
```bash
# Navigate to current frontend
cd frontend/public

# Option 1: Open directly in browser
open index.html  # macOS
start index.html  # Windows

# Option 2: Use development server
python -m http.server 8000
# Visit http://localhost:8000
```

## Development Workflow

### Feature Development Process
1. **Branch Creation**: Create feature branch from main
2. **Development**: Implement feature with tests
3. **Testing**: Run comprehensive test suite
4. **Code Review**: Submit pull request for review
5. **Deployment**: Merge to main triggers auto-deployment

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/user-authentication

# Make changes and commit
git add .
git commit -m "Add user authentication system"

# Push and create pull request
git push origin feature/user-authentication
# Create PR on GitHub

# After review and merge
git checkout main
git pull origin main
git branch -d feature/user-authentication
```

### Testing Strategy

#### Backend Testing (95.7% Coverage)
```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run tests with verbose output
pytest -v

# Performance testing
pytest tests/test_performance.py
```

#### Frontend Testing (Planned)
```bash
# Next.js testing
cd threadr-nextjs
npm test

# E2E testing with Playwright
npm run test:e2e

# Component testing
npm run test:components

# Visual regression testing
npm run test:visual
```

### Code Quality Standards

#### Python Code Standards
- **Formatter**: Black for code formatting
- **Linter**: Ruff for linting and import sorting
- **Type Checking**: mypy for static type analysis
- **Documentation**: Docstrings for all functions and classes

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/

# All quality checks
make quality  # (if Makefile exists)
```

#### TypeScript Code Standards
```bash
# Linting
npm run lint

# Type checking
npm run type-check

# Format code
npm run format

# All checks
npm run check-all
```

## Architecture Guidelines

### Backend Architecture (FastAPI)

#### Project Structure
```
backend/src/
├── main.py              # FastAPI application entry point
├── core/                # Core configuration and utilities
│   ├── config.py       # Environment configuration
│   └── redis_manager.py # Redis connection management
├── models/             # Pydantic models and schemas
│   ├── auth.py        # Authentication models
│   ├── thread.py      # Thread-related models
│   └── analytics.py   # Analytics models
├── routes/            # API route definitions
│   ├── auth.py       # Authentication endpoints
│   ├── thread.py     # Thread generation endpoints
│   └── analytics.py  # Analytics endpoints
├── services/          # Business logic services
│   ├── auth/         # Authentication services
│   ├── thread/       # Thread generation services
│   └── analytics/    # Analytics services
├── middleware/        # Custom middleware
│   └── auth.py       # JWT authentication middleware
└── utils/            # Utility functions
    └── security.py   # Security utilities
```

#### Design Principles
- **Separation of Concerns**: Clear separation between routes, services, and models
- **Dependency Injection**: Use FastAPI's dependency system
- **Async/Await**: Use async functions for I/O operations
- **Error Handling**: Comprehensive error handling with proper HTTP status codes
- **Validation**: Pydantic models for request/response validation

#### API Design Guidelines
- **RESTful URLs**: Use standard REST conventions
- **HTTP Status Codes**: Proper status codes for all responses
- **Request/Response Models**: Pydantic models for all endpoints
- **Documentation**: OpenAPI documentation with examples
- **Versioning**: API versioning strategy for future changes

### Frontend Architecture (Next.js)

#### Project Structure
```
threadr-nextjs/src/
├── app/                 # Next.js 14 App Router
│   ├── (auth)/         # Authentication pages
│   ├── (dashboard)/    # Main application pages
│   ├── layout.tsx      # Root layout
│   └── page.tsx        # Home page
├── components/         # Reusable React components
│   ├── ui/            # Base UI components
│   ├── forms/         # Form components
│   ├── thread/        # Thread-related components
│   └── auth/          # Authentication components
├── hooks/             # Custom React hooks
│   ├── api/          # API integration hooks
│   └── useAuth.ts    # Authentication hook
├── lib/              # Utilities and configuration
│   ├── api/          # API client
│   ├── stores/       # Zustand stores
│   └── utils/        # Helper functions
├── contexts/         # React contexts
└── types/           # TypeScript type definitions
```

#### Design Principles
- **Component Composition**: Build complex UIs from simple components
- **State Management**: Use React Query for server state, Zustand for client state
- **Type Safety**: Full TypeScript coverage
- **Performance**: Optimize for Core Web Vitals
- **Accessibility**: WCAG 2.1 AA compliance

## API Development

### Authentication System
```python
# JWT-based authentication
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(401, "Invalid token")
        return await get_user_by_username(username)
    except JWTError:
        raise HTTPException(401, "Invalid token")

@app.post("/api/auth/login")
async def login(credentials: LoginRequest):
    user = await authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
```

### Thread Generation Service
```python
@app.post("/api/generate")
async def generate_thread(
    request: ThreadRequest,
    current_user: User = Depends(get_current_user)
):
    # Check rate limits
    if not await check_rate_limit(current_user.id):
        raise HTTPException(429, "Rate limit exceeded")
    
    # Generate thread using OpenAI
    thread = await thread_service.generate_thread(
        content=request.content,
        user_id=current_user.id
    )
    
    # Save to database
    await thread_service.save_thread(thread)
    
    return thread
```

### Error Handling
```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

## Database Development

### Redis Data Models
```python
# User session data
user_session = {
    "user_id": "uuid",
    "email": "user@example.com",
    "premium_until": "2025-09-01T00:00:00Z",
    "usage_daily": 3,
    "usage_monthly": 15
}

# Thread data
thread_data = {
    "thread_id": "uuid",
    "user_id": "uuid",
    "content": "Original content",
    "tweets": ["Tweet 1", "Tweet 2", "Tweet 3"],
    "created_at": "2025-08-01T12:00:00Z",
    "updated_at": "2025-08-01T12:00:00Z"
}

# Rate limiting data
rate_limit = {
    "ip_address": "192.168.1.1",
    "daily_count": 5,
    "monthly_count": 20,
    "last_reset": "2025-08-01T00:00:00Z"
}
```

### PostgreSQL Migration (Planned)
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Threads table
CREATE TABLE threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    title VARCHAR(255),
    content TEXT NOT NULL,
    tweets JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Subscriptions table
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    plan_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Performance Optimization

### Backend Performance
- **Async Operations**: Use async/await for all I/O operations
- **Connection Pooling**: Redis and database connection pooling
- **Caching**: Cache frequently accessed data
- **Request Validation**: Early validation to prevent unnecessary processing
- **Monitoring**: Track response times and error rates

### Frontend Performance
- **Code Splitting**: Automatic code splitting with Next.js
- **Image Optimization**: Next.js image optimization
- **Caching**: Proper caching headers and strategies
- **Bundle Analysis**: Regular bundle size analysis
- **Core Web Vitals**: Optimize for Google's performance metrics

## Security Development

### Backend Security
```python
# Input validation
from pydantic import BaseModel, validator

class ThreadRequest(BaseModel):
    content: str
    
    @validator('content')
    def validate_content(cls, v):
        if len(v) > 50000:
            raise ValueError('Content too long')
        if not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/generate")
@limiter.limit("5/minute")
async def generate_thread(request: Request, thread_req: ThreadRequest):
    pass
```

### Frontend Security
```typescript
// Secure API calls
const apiCall = async (endpoint: string, data: any) => {
  const token = localStorage.getItem('auth_token')
  
  const response = await fetch(`${API_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    },
    body: JSON.stringify(data)
  })
  
  if (!response.ok) {
    throw new Error(`API call failed: ${response.statusText}`)
  }
  
  return response.json()
}

// Input sanitization
import DOMPurify from 'dompurify'

const sanitizeInput = (input: string): string => {
  return DOMPurify.sanitize(input, { ALLOWED_TAGS: [] })
}
```

## Debugging and Troubleshooting

### Backend Debugging
```python
# Logging configuration
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Debug endpoint
@app.get("/debug/info")
async def debug_info():
    return {
        "environment": os.getenv("ENVIRONMENT"),
        "redis_connected": await redis_client.ping(),
        "openai_available": bool(os.getenv("OPENAI_API_KEY")),
        "timestamp": datetime.utcnow()
    }
```

### Common Issues and Solutions

#### Issue: CORS Errors
```python
# Problem: CORS not configured properly
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://threadr-plum.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Issue: Redis Connection Failures
```python
# Problem: Redis connection issues
import redis
from redis.exceptions import ConnectionError

try:
    redis_client = redis.from_url(redis_url)
    await redis_client.ping()
except ConnectionError:
    logger.error("Redis connection failed")
    # Use fallback storage or raise error
```

## Development Tools

### Recommended VS Code Extensions
- **Python**: Python extension pack
- **TypeScript**: TypeScript and JavaScript support
- **Tailwind CSS**: Tailwind CSS IntelliSense
- **GitLens**: Git supercharged
- **Thunder Client**: API testing
- **Error Lens**: Inline error display

### Useful Development Commands
```bash
# Backend development
cd backend
python -m pytest --watch  # Watch mode testing
uvicorn src.main:app --reload --log-level debug

# Frontend development
cd threadr-nextjs
npm run dev  # Development server
npm run build && npm run start  # Production simulation
npm run analyze  # Bundle analysis

# Database operations
redis-cli -u $REDIS_URL
psql $DATABASE_URL  # (when PostgreSQL added)

# Deployment testing
vercel dev  # Local Vercel simulation
railway run uvicorn src.main:app  # Local Railway simulation
```

## Development Best Practices

### Code Review Guidelines
- **Security**: Check for security vulnerabilities
- **Performance**: Review for performance implications
- **Testing**: Ensure adequate test coverage
- **Documentation**: Update documentation for changes
- **Standards**: Follow coding standards and conventions

### Git Best Practices
- **Commit Messages**: Use conventional commit format
- **Branch Naming**: Use descriptive branch names
- **Pull Requests**: Small, focused PRs with clear descriptions
- **Code Review**: All code must be reviewed before merge

### Testing Best Practices
- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test API endpoints and database operations
- **E2E Tests**: Test complete user workflows
- **Performance Tests**: Test under expected load

---

**🛠️ Complete development environment ready for scaling to $1K MRR**

*Comprehensive development workflow supporting rapid iteration and quality delivery*