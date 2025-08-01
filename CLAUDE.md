# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Threadr is a SaaS tool that converts blog articles or pasted content into Twitter threads. This is a greenfield project with the specification defined in MVP.md.

## Current Production Status

✅ **Live Production App**: https://threadr-plum.vercel.app - Fully functional SaaS
✅ **Backend API**: https://threadr-production.up.railway.app - 95.7% test coverage
✅ **Monetization Active**: Stripe payments ($4.99 for 30 days premium access)
✅ **Free Tier Limits**: 5 daily / 20 monthly thread generations enforced
✅ **URL Scraping**: Working for 15+ domains (Medium, Dev.to, Substack, etc.)
✅ **Thread Generation**: OpenAI GPT-3.5-turbo with smart content splitting
✅ **Payment Processing**: Secure webhook-based Stripe integration with HMAC verification
✅ **Rate Limiting**: Redis-based IP tracking prevents abuse
✅ **Email Capture**: Working system for user engagement and notifications

### Recent Updates (2025-08-01)
- 📁 **Project Reorganization**: Complete directory restructure for better maintainability
- 📊 **Project Status Report**: Comprehensive analysis showing path to $1K MRR
- 📚 **Documentation Consolidation**: Merged 16+ Railway docs into single guide
- 🏗️ **Phase 2 Progress**: User auth, thread history, and analytics features 40% complete
- 🐛 **Template Implementation Fixes**: Resolved critical production issues:
  - Fixed JavaScript syntax error (misplaced HTML, extra closing braces)
  - Fixed Pro Template modal blocking app access for non-premium users
  - Fixed unresponsive modal buttons (missing showUpgradeModal state and openPaymentModal function)
  - Fixed logo display issues by converting PNG references to inline SVG
- 🧹 **Post-Debug Cleanup**: Removed temporary test files and debug scripts

### Previous Updates (2025-07-31)
- ✅ **Stripe Payment Integration**: Complete webhook-based payment processing
- ✅ **Premium Access System**: Automatic premium grants on successful payments
- ✅ **Webhook Security**: HMAC-SHA256 signature verification for Stripe webhooks
- ✅ **Payment Configuration**: Environment-based Stripe API configuration
- ✅ **Error Handling**: Comprehensive payment processing error handling and logging

### Previous Fixes (2025-07-31)
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

## Monetization Implementation

### Current Payment Flow
1. **Free Tier**: 5 daily / 20 monthly thread generations
2. **Payment Trigger**: Users hit limits and see upgrade prompt
3. **Stripe Checkout**: $4.99 for 30 days premium access
4. **Webhook Processing**: Secure HMAC-SHA256 signature verification
5. **Premium Grant**: Automatic unlimited access for 30 days
6. **Renewal**: Users can purchase additional 30-day periods

### Payment Infrastructure
- **Stripe Integration**: Complete webhook-based processing
- **Security**: HMAC signature verification for all webhooks
- **Error Handling**: Comprehensive payment processing error logging
- **Environment Config**: Separate dev/prod Stripe API keys
- **Database**: Redis-based premium access tracking with expiration

### Key Metrics Tracking
- Daily/monthly usage per IP address
- Premium conversion rates
- Payment success/failure rates
- API cost monitoring (OpenAI usage)
- User engagement patterns

## Revenue Roadmap

### Current Tier (Phase 1 - Validated)
- **Free**: 5 daily / 20 monthly generations
- **Premium**: $4.99 for 30 days unlimited access
- **Target**: $1,000 MRR by end of month

### Phase 2: Tiered Pricing (Next 30 days)
- **Starter**: $9.99/month - 100 threads/month + basic analytics
- **Pro**: $19.99/month - Unlimited threads + advanced features
- **Team**: $49.99/month - Team accounts + collaboration tools

### Phase 3: Enterprise Features (60-90 days)
- **API Access**: $99/month - Direct API access for developers
- **White Label**: $299/month - Custom branding and domain
- **Enterprise**: Custom pricing - Volume licensing and support

### Revenue Targets
- **Month 1**: $1K MRR (200 premium users @ $4.99)
- **Month 3**: $5K MRR (mix of monthly subscriptions)
- **Month 6**: $15K MRR (including enterprise customers)
- **Year 1**: $50K MRR (established SaaS business)

## Project Status Summary (2025-08-01)

### Key Metrics & Progress
- **Revenue Goal**: $1K MRR by month end (needs 200 premium users)
- **Current Status**: Monetization active but no visibility into metrics
- **Phase 2 Progress**: ~40% complete (backend built, frontend integration needed)
- **Technical Health**: 95.7% test coverage, production stable

### Critical Path to $1K MRR
1. **Implement Revenue Tracking** (IMMEDIATE): Add usage/conversion metrics
2. **Complete User Accounts** (2 weeks): Frontend integration for auth system
3. **Launch Content Marketing** (30 days): Drive organic user acquisition
4. **Database Migration** (45 days): PostgreSQL for data persistence

For detailed analysis, see: `THREADR_PROJECT_STATUS_REPORT.md`

## Next Development Phase

### Phase 2: User Accounts & Data Persistence (Current Priority - 40% Complete)
1. **User Authentication**: JWT-based login system ✅ (backend complete)
2. **Thread History**: Save and manage generated threads ✅ (backend complete)
3. **Usage Analytics**: Personal dashboard with usage stats ✅ (backend complete)
4. **Account Management**: Subscription management and billing history 🔄 (in progress)
5. **Social Features**: Share threads, favorite templates 📋 (planned)

### Phase 3: Analytics & Premium Features (30-60 days)
1. **Advanced Analytics**: Thread performance tracking
2. **Template System**: Pre-built thread templates
3. **Scheduled Publishing**: Direct posting to Twitter/X
4. **Team Collaboration**: Shared workspaces and approval workflows
5. **API Access**: Developer API for integrations

### Phase 4: Enterprise & Scale (60-90 days)
1. **White Labeling**: Custom branding options
2. **Advanced Integrations**: CRM, marketing tools, etc.
3. **Bulk Processing**: Handle multiple URLs simultaneously
4. **Advanced AI**: Custom models and fine-tuning
5. **Enterprise Security**: SSO, audit logs, compliance

### Technical Debt & Infrastructure
1. **Database Migration**: Move from Redis to PostgreSQL
2. **Caching Layer**: Implement proper caching strategy
3. **Monitoring**: Set up comprehensive logging and alerting
4. **Performance**: Optimize for scale (1000+ concurrent users)
5. **Testing**: Expand test coverage to 98%+

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

## Core Features (Completed)

✅ **URL/Content Input**: Supports 15+ domains plus direct text input
✅ **AI Thread Generation**: GPT-3.5-turbo with intelligent 280-char splitting  
✅ **Inline Editing**: Full WYSIWYG editing of generated tweets
✅ **Copy Functionality**: Individual tweets and entire thread copying
✅ **Email Capture**: Working system with user engagement tracking
✅ **Rate Limiting**: Redis-based IP tracking (5 daily/20 monthly free)
✅ **Monetization**: Active Stripe payments ($4.99 for 30-day premium)
✅ **Premium Access**: Automatic unlimited access after payment
✅ **Usage Analytics**: Real-time tracking of user consumption

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

1. **Organized File Structure** (Updated 2025-08-01):
   ```
   threadr/
   ├── backend/
   │   ├── src/
   │   │   ├── main.py (FastAPI application)
   │   │   ├── core/
   │   │   │   ├── config.py
   │   │   │   └── redis_manager.py
   │   │   ├── models/
   │   │   │   ├── analytics.py
   │   │   │   ├── auth.py
   │   │   │   ├── team.py
   │   │   │   └── thread.py
   │   │   ├── routes/
   │   │   │   ├── analytics.py
   │   │   │   ├── auth.py
   │   │   │   ├── team.py
   │   │   │   └── thread.py
   │   │   ├── services/
   │   │   │   ├── analytics/
   │   │   │   ├── auth/
   │   │   │   ├── team/
   │   │   │   └── thread/
   │   │   ├── middleware/
   │   │   │   └── auth.py
   │   │   └── utils/
   │   ├── tests/
   │   │   ├── unit/
   │   │   ├── integration/
   │   │   └── e2e/
   │   └── requirements.txt
   ├── frontend/
   │   ├── src/
   │   │   ├── index.html
   │   │   ├── config.js
   │   │   └── assets/logos/
   │   ├── dashboard/
   │   └── tests/
   ├── docs/
   │   ├── deployment/
   │   │   ├── railway/
   │   │   │   └── RAILWAY_DEPLOYMENT_GUIDE.md
   │   │   └── vercel/
   │   ├── api/
   │   ├── security/
   │   └── development/
   ├── scripts/
   │   ├── deploy/
   │   └── test/
   ├── archive/
   │   ├── backend/
   │   ├── docs/
   │   └── test_reports/
   └── README.md
   ```

2. **API Endpoints**:
   - `POST /api/generate` - Convert content/URL to thread (with rate limiting)
   - `POST /api/capture-email` - Store user email for updates
   - `POST /api/stripe/webhook` - Process Stripe payment webhooks
   - `GET /api/premium-status` - Check premium access status
   - `GET /api/usage-stats` - Get current usage statistics
   - `GET /health` - Health check with detailed diagnostics
   - `GET /readiness` - Kubernetes readiness probe

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

## Critical Deployment Learnings (2025-08-01)

### Consolidated Railway Documentation ✅
**All Railway deployment knowledge has been consolidated into a single comprehensive guide:**
`docs/deployment/railway/RAILWAY_DEPLOYMENT_GUIDE.md`

This guide replaces 16+ fragmented documentation files and includes:
- Complete configuration setup
- Environment variables
- Common issues and solutions
- Redis setup
- URL scraping configuration
- Health checks and troubleshooting

### Railway Deployment Pitfalls & Solutions (Historical)
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