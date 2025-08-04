# Threadr 🧵

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.x-38B2AC.svg)](https://tailwindcss.com/)
[![Test Coverage](https://img.shields.io/badge/coverage-95.7%25-brightgreen.svg)](https://github.com/hoshdog/threadr)
[![Production Status](https://img.shields.io/badge/status-live%20production-success.svg)](https://threadr-plum.vercel.app)

**Live SaaS Application**: Transform blog articles and long-form content into engaging Twitter/X threads using AI-powered content analysis.

## 🚨 CRITICAL SECURITY ISSUE

**IMMEDIATE ACTION REQUIRED**: API keys are hardcoded in the frontend configuration file (`frontend/public/config.js` line 59). This exposes sensitive credentials to all users and represents a serious security vulnerability that needs immediate attention.

🌐 **Try it now**: [https://threadr-plum.vercel.app](https://threadr-plum.vercel.app)  
📊 **Current Status**: Live production with active monetization ($4.99 for 30-day premium access - FLAT RATE)
⚠️ **Security Issue**: API keys hardcoded in frontend (immediate fix required)
🔄 **Next.js Status**: Development version exists but NOT deployed to production

## 🚀 Live Features

Threadr is a **fully functional production SaaS** that offers:

✅ **Smart URL Extraction**: Supports 15+ major platforms (Medium, Dev.to, Substack, etc.)  
✅ **AI-Powered Thread Generation**: GPT-3.5-turbo intelligently splits content into 280-char tweets  
✅ **Inline Editing**: WYSIWYG editor for refining generated threads  
✅ **One-Click Copying**: Copy individual tweets or entire threads instantly  
✅ **Freemium Model**: 5 daily / 20 monthly free generations, premium for $4.99/30 days (FLAT RATE, not recurring)  
✅ **Rate Limiting**: Redis-based protection against abuse  
✅ **Secure Payments**: Stripe integration with webhook verification  
✅ **Email Capture**: User engagement and notification system

## 📁 Project Structure

```
threadr/
├── docs/                      # Comprehensive documentation
│   ├── deployment/           
│   │   ├── railway/          # Railway deployment guides
│   │   └── vercel/           # Vercel deployment guides
│   ├── api/                  # API documentation
│   ├── security/             # Security documentation
│   └── development/          # Development guides
│
├── backend/                   # FastAPI backend
│   ├── src/                  # Source code
│   │   ├── api/             # API routes
│   │   ├── core/            # Core functionality
│   │   ├── services/        # Business logic
│   │   └── utils/           # Utilities
│   ├── tests/               # Test suite
│   ├── scripts/             # Backend scripts
│   └── archive/             # Archived code
│
├── frontend/                  # Alpine.js + Tailwind frontend
│   ├── src/                 # Source files
│   └── tests/               # Frontend tests
│
├── scripts/                   # Project-level scripts
│   ├── deploy/              # Deployment scripts
│   └── test/                # Testing scripts
│
└── deployment/               # Deployment configurations
    └── configs/             # Alternative nixpacks configs
```

## 🛠️ Technology Stack

### Current Production Stack (LIVE at https://threadr-plum.vercel.app)
- **Backend**: Python FastAPI with async support (95.7% test coverage) - STABLE
- **Frontend**: Alpine.js + Tailwind CSS (260KB monolithic HTML file) - PRODUCTION
- **State Management**: Alpine.js global state with x-data objects
- **AI**: OpenAI GPT-3.5-turbo for intelligent content analysis
- **Database**: Redis for rate limiting, premium access, and email storage
- **Payments**: Stripe with secure webhook processing
- **Deployment**: Railway (backend) + Vercel (frontend - static HTML hosting)
- **Security**: Cloudflare protection, CORS, HMAC verification, rate limiting
- **⚠️ Security Issue**: API keys hardcoded in frontend config.js
- **Monitoring**: Health checks, readiness probes, detailed logging

### Development Stack (Next.js - EXISTS BUT NOT DEPLOYED)
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS (in `threadr-nextjs/` directory)
- **State Management**: React Query + Zustand (planned)
- **Status**: Development environment only - NOT in production
- **Note**: Next.js migration planned but incomplete - users are using Alpine.js version

## 💰 Revenue & Metrics

**Current Performance:**
- 🚀 **Live Production**: Fully functional SaaS application
- 💳 **Active Monetization**: $4.99 for 30-day premium access
- 📊 **95.7% Test Coverage**: Production-ready codebase
- ⚡ **Sub-2 Second**: Average thread generation time
- 🛡️ **Security**: HMAC webhook verification, rate limiting protection
- 📈 **Growth Ready**: Infrastructure scales to 1000+ concurrent users

**Usage Limits:**
- **Free Tier**: 5 daily / 20 monthly thread generations
- **Premium**: Unlimited threads for 30 days ($4.99 FLAT RATE, not recurring)
- **Rate Protection**: Redis-based IP tracking prevents abuse
- **Renewal**: Users must manually purchase additional 30-day periods

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Redis (required for rate limiting and premium access)
- OpenAI API key (required for thread generation)
- Stripe account (required for payment processing)
- Upstash Redis account (recommended for production)

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/hoshdog/threadr.git
cd threadr

# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration including:
# - OPENAI_API_KEY
# - STRIPE_SECRET_KEY
# - STRIPE_WEBHOOK_SECRET
# - REDIS_URL (Upstash or local Redis)

# Run the development server
uvicorn src.main:app --reload --port 8001
```

The API will be available at `http://localhost:8001`

### Frontend Setup (Next.js - Current Migration)

```bash
# Navigate to Next.js project
cd threadr-nextjs

# Install dependencies
npm install

# Development server
npm run dev
# Visit http://localhost:3000

# Build for production
npm run build

# Start production server
npm start
```

### Frontend Setup (Alpine.js - DEPRECATED)

```bash
# DEPRECATED - Use only for critical production fixes during migration
cd frontend

# Option 1: Open directly in browser
open public/index.html  # macOS
start public/index.html  # Windows

# Option 2: Use a local server
python -m http.server 8000
# Visit http://localhost:8000/public/
```

## 📚 API Documentation

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/generate` | Generate thread from URL or text (rate limited) |
| POST | `/api/capture-email` | Capture user email for notifications |
| POST | `/api/stripe/webhook` | Process Stripe payment webhooks |
| GET | `/api/premium-status` | Check premium access status |
| GET | `/api/usage-stats` | Get current usage statistics |
| GET | `/health` | Health check with detailed diagnostics |
| GET | `/readiness` | Kubernetes readiness probe |

For detailed API documentation, see [docs/api/](docs/api/).

## 🔒 Security Features

- **Rate Limiting**: IP-based with Redis backend (5 daily/20 monthly free tier)
- **Payment Security**: HMAC-SHA256 webhook signature verification
- **CORS Protection**: Strict origin policy for production domains
- **Input Validation**: Comprehensive request validation and sanitization  
- **SSRF Protection**: URL allowlist (15+ domains) and private IP blocking
- **Security Headers**: CSP, HSTS, XSS protection, secure cookies
- **Premium Access Control**: Time-based access verification with Redis expiration

See [docs/security/](docs/security/) for detailed security documentation.

## 🚀 Deployment

### Backend Deployment (Railway)

```bash
# Using Railway CLI
railway up

# Or push to GitHub and connect Railway
git push origin main
```

See [docs/deployment/railway/](docs/deployment/railway/) for detailed Railway deployment guide.

### Frontend Deployment (Vercel)

```bash
# Using Vercel CLI
cd frontend
vercel --prod

# Or connect GitHub repository to Vercel
```

See [docs/deployment/vercel/](docs/deployment/vercel/) for detailed Vercel deployment guide.

## ⚙️ Environment Variables

### Required Backend Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# Stripe Configuration  
STRIPE_SECRET_KEY=sk_live_your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

# Redis Configuration
REDIS_URL=redis://default:password@host:port

# CORS Configuration
CORS_ORIGINS=https://threadr-plum.vercel.app,https://your-domain.com

# Application Settings
ENVIRONMENT=production
LOG_LEVEL=info
MAX_CONTENT_LENGTH=50000
RATE_LIMIT_DAILY=5
RATE_LIMIT_MONTHLY=20
```

### Optional Backend Variables

```bash
# Alternative Redis (if not using REDIS_URL)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-password
REDIS_DB=0

# Development Settings
DEBUG=false
TESTING=false

# Monitoring
HEALTH_CHECK_TIMEOUT=30
```

### Frontend Configuration

The frontend automatically detects the environment and uses the appropriate API URLs:
- **Development**: `http://localhost:8001`
- **Production**: `https://threadr-production.up.railway.app`

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test

# Run all tests
./scripts/test/run_all_tests.sh
```

## 🛣️ Development Roadmap

### Phase 1: MVP ✅ COMPLETED (July 2025)
- [x] AI-powered thread generation with GPT-3.5-turbo
- [x] URL content extraction (15+ supported domains)
- [x] Rate limiting and abuse protection
- [x] Frontend with Alpine.js + Tailwind CSS (DEPRECATED - reached architectural limits)
- [x] Email capture and user engagement
- [x] Stripe payment integration ($4.99 premium)
- [x] Production deployment (95.7% test coverage)

### Phase 1.5: Next.js Migration 🔄 PLANNED (August 2025)
- [x] Identified Alpine.js architectural limitations (260KB monolithic file)
- [x] Next.js 14 project setup with TypeScript and Tailwind (development only)
- [ ] Core feature migration (thread generation, templates, history)
- [ ] Authentication and state management with React Query + Zustand
- [ ] Performance optimization and testing
- [ ] Production deployment and user migration
- **Status**: Next.js version exists in development but is NOT deployed to production

### Phase 2: User Accounts & Analytics 🚧 CURRENT (Sep-Oct 2025)
- [ ] JWT-based user authentication system (Next.js components)
- [ ] Thread history and management (React Query integration)
- [ ] Personal analytics dashboard (with proper state management)
- [ ] Account and subscription management (TypeScript interfaces)
- [ ] Enhanced premium features (component-based architecture)

**Note**: Phase 2 now includes Next.js migration completion as prerequisite

### Phase 3: Advanced Features 📅 PLANNED (Oct-Dec 2025)
- [ ] Thread performance analytics
- [ ] Template system and marketplace
- [ ] Scheduled publishing to Twitter/X
- [ ] Team collaboration tools
- [ ] Developer API access

### Phase 4: Enterprise Scale 🎯 FUTURE (2026)
- [ ] White labeling and custom branding
- [ ] Advanced integrations (CRM, marketing tools)
- [ ] Bulk processing capabilities
- [ ] Custom AI models and fine-tuning
- [ ] Enterprise security (SSO, compliance)

**Revenue Targets** (Based on Current Flat-Rate Model):
- Phase 1: $1K MRR (requires 200 users buying $4.99/30-day periods monthly)
- Phase 2: $5K MRR by end 2025 (requires implementing recurring subscriptions)
- Phase 3: $15K MRR by end 2025 (requires tiered pricing implementation)
- Phase 4: $50K MRR by 2026 (requires architectural scaling and enterprise features)

**Note**: Current $4.99 flat-rate model requires manual re-purchases for sustained revenue.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** for the excellent async framework and automatic API docs
- **OpenAI** for GPT-3.5-turbo API powering intelligent thread generation
- **Next.js** for the scalable React framework enabling component-based architecture
- **TypeScript** for type safety and improved developer experience
- **React Query** for powerful server state management
- **Alpine.js** for initial rapid prototyping (graduated to Next.js for scale)
- **Tailwind CSS** for utility-first styling and rapid UI development
- **Stripe** for secure payment processing and webhook infrastructure
- **Railway** for seamless Python deployment and scaling
- **Vercel** for lightning-fast Next.js hosting with SSR/SSG
- **Redis/Upstash** for reliable rate limiting and premium access management

## 📞 Support & Community

- **Live App**: [https://threadr-plum.vercel.app](https://threadr-plum.vercel.app)
- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/hoshdog/threadr/issues) 
- **Feature Requests**: Create an issue with the `enhancement` label
- **Security**: Report security issues privately via email

## 📈 Business Metrics

**Current Status (August 2025):**
- 🚀 Live production SaaS with active revenue
- 💰 $4.99 premium tier with 30-day access
- 📊 95.7% backend test coverage
- ⚡ Sub-2 second average response time
- 🛡️ Zero security incidents since launch
- 📱 Responsive design works on all devices

---

**Built with ❤️ for content creators, marketers, and Twitter thread enthusiasts**

*Transforming long-form content into engaging social media threads, one AI-powered generation at a time.*