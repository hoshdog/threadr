# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Threadr is a SaaS tool that converts blog articles or pasted content into Twitter threads. This is a greenfield project with the specification defined in MVP.md.

## Project Status

✅ **Backend Implementation**: FastAPI backend is complete with thread generation, rate limiting, and health checks
✅ **Railway Deployment**: Fully functional at https://threadr-production.up.railway.app
✅ **OpenAI Integration**: GPT-3.5-turbo integration with graceful fallback when API key unavailable
✅ **URL Scraping**: Working for all allowed domains (Medium, Dev.to, Substack, etc.)
✅ **Frontend Deployment**: Live at https://threadr-plum.vercel.app
✅ **Full Integration**: Frontend successfully communicates with backend, complete E2E functionality

### Recent Fixes (2025-07-31)
- Fixed Railway health check failures ("service unavailable" errors)
- Resolved OpenAI API key startup dependency issues
- Updated gunicorn configuration for proper port binding
- Enhanced health endpoint with detailed diagnostics
- Increased health check timeout from 30s to 60s
- Fixed Pydantic v2 HttpUrl isinstance error that caused 500 errors
- Simplified httpx configuration for Railway compatibility
- Fixed project structure imports and PYTHONPATH issues for src/ directory
- Removed complex SSL context and proxy configurations that failed on Railway
- Successfully deployed URL scraping functionality

## Technology Stack (Expert-Verified Decision)

Final technology decisions after expert review:
- **Frontend**: Alpine.js + Tailwind CSS via CDN (no build process, reactive UI)
- **Backend**: Python FastAPI (async support, better than Flask for this use case)
- **Storage**: In-memory + Upstash Redis free tier (no database complexity for MVP)
- **AI Integration**: OpenAI GPT-3.5-turbo API (proven reliability, extensive docs)
- **Deployment**: 
  - Frontend: Vercel (static hosting)
  - Backend: Railway (excellent Python support)
  - Protection: Cloudflare free tier (DDoS + rate limiting)

## Core Features to Implement

1. URL/content input interface (critical - 80% of users will paste URLs)
2. AI-powered content summarization and tweet splitting (280 chars each)
3. Inline editing functionality for generated tweets (users need to refine AI output)
4. Copy individual tweets or entire thread functionality
5. Email capture after first use (essential for future monetization)
6. IP-based rate limiting (prevent abuse and API cost explosion)
7. Phased monetization: Week 1 (free), Week 2 (limits), Week 3 (Stripe payment links)

## Development Commands

### Frontend (Alpine.js + Tailwind)
```bash
# No build process needed!
# Simply open index.html in browser
# For development server:
python -m http.server 8000  # or
npx serve frontend/
```

### Backend (Python FastAPI)
```bash
# Initial setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Development (from backend directory)
uvicorn src.main:app --reload --port 8001

# Testing
pytest

# Linting
ruff check .
black .
```

### Deployment
```bash
# Frontend to Vercel
vercel --prod

# Backend to Railway
railway up
```

## Architecture Considerations

1. **Organized File Structure** (Updated 2025-07-31):
   ```
   threadr/
   ├── backend/
   │   ├── src/
   │   │   ├── main.py (FastAPI endpoints)
   │   │   └── redis_manager.py (Redis utilities)
   │   ├── tests/
   │   │   └── test_*.py (All backend tests)
   │   ├── scripts/
   │   │   └── (Utility scripts)
   │   └── requirements.txt
   ├── frontend/
   │   ├── src/
   │   │   ├── index.html (Alpine.js + Tailwind)
   │   │   └── config.js
   │   └── tests/
   ├── docs/
   │   ├── deployment/
   │   │   ├── railway/
   │   │   └── vercel/
   │   ├── api/
   │   ├── security/
   │   └── development/
   ├── scripts/
   │   ├── deploy/
   │   └── test/
   └── README.md
   ```

2. **API Endpoints**:
   - `POST /api/generate` - Convert content/URL to thread
   - `POST /api/capture-email` - Store user email
   - Rate limiting via IP address (no auth needed)

3. **Key Implementation Details**:
   - Use BeautifulSoup for URL content extraction
   - Implement IP-based rate limiting with Redis
   - Handle OpenAI API errors gracefully
   - Store emails in Redis for MVP (migrate to DB later)

## 4-Hour Implementation Plan

### Hour 1: Frontend Setup
1. Create `frontend/index.html` with Alpine.js + Tailwind CDN
2. Build form with URL/content input
3. Add loading states and error handling
4. Style with Tailwind for professional look

### Hour 2: Backend Core
1. Set up FastAPI with CORS enabled
2. Implement `/api/generate` endpoint
3. Add BeautifulSoup for URL scraping
4. Integrate OpenAI API for thread generation

### Hour 3: Integration & Protection
1. Connect frontend to backend API
2. Implement IP-based rate limiting
3. Add email capture functionality
4. Test end-to-end flow

### Hour 4: Deployment
1. Deploy frontend to Vercel
2. Deploy backend to Railway
3. Configure Cloudflare protection
4. Test production environment

## Critical Implementation Notes

### Must-Have Features (Don't Skip These!)
- **URL input**: 80% of users will paste URLs, not full content
- **Email capture**: Essential for monetization - add after first use
- **Rate limiting**: Prevent API cost disasters from day one
- **Basic editing**: Users need to refine AI output for quality

### Expert Warnings
- Vanilla JS is NOT simpler for this use case - use Alpine.js
- Vercel is NOT ideal for Python backends - use Railway
- Don't skip the database entirely - use Redis for rate limiting
- JSON files + multiple workers = race conditions

### Quick Win Tips
- Use GPT-3.5-turbo (cheaper and sufficient for summaries)
- Implement "Copy All" before individual tweet copying
- Add Cloudflare from day 1 (free DDoS protection)
- Start with Stripe Payment Links (no code needed)

## Critical Deployment Learnings (2025-07-31)

### Railway Deployment Pitfalls & Solutions
1. **httpx Configuration Issues**
   - **Problem**: Complex SSL contexts and proxy configs fail in Railway containers
   - **Solution**: Use simple httpx.AsyncClient with just timeout, follow_redirects, and headers
   - **Code**: 
     ```python
     async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers={...}) as client:
     ```

2. **Pydantic v2 Type Checking**
   - **Problem**: `isinstance(url, HttpUrl)` throws TypeError with Pydantic v2 subscripted generics
   - **Solution**: Always convert to string: `url_str = str(url)`
   
3. **Project Structure & Imports**
   - **Problem**: Moving files to src/ directory breaks imports
   - **Solution**: Update PYTHONPATH in nixpacks.toml: `PYTHONPATH = "/app/backend:/app/backend/src"`
   - **Import Fix**: Use try/except for relative imports:
     ```python
     try:
         from .redis_manager import initialize_redis
     except ImportError:
         from redis_manager import initialize_redis
     ```

4. **CORS Configuration**
   - **Problem**: CORS errors between Vercel frontend and Railway backend
   - **Solution**: Remove trailing slashes from CORS_ORIGINS in .env.production

### Web Scraping Implementation
- **Domain Allowlist**: Always check allowed domains before scraping
- **Error Handling**: Provide user-friendly messages for JavaScript-required sites
- **Fallback Methods**: Implement multiple content extraction strategies
- **SSL Issues**: Let httpx handle SSL verification with defaults, don't customize

### Development Best Practices
1. **Always test deployment configs locally first**
2. **Use debug endpoints during development but remove for production**
3. **Monitor Railway logs closely - connection timeouts often indicate config issues**
4. **Keep httpx configuration simple for containerized environments**
5. **Document all deployment fixes immediately**