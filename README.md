# Threadr

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Alpine.js](https://img.shields.io/badge/Alpine.js-3.x-8BC0D0.svg)](https://alpinejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.x-38B2AC.svg)](https://tailwindcss.com/)

A modern SaaS tool that converts blog articles or pasted content into engaging Twitter/X threads using AI-powered content analysis.

## 🚀 Overview

Threadr simplifies the process of turning long-form content into Twitter threads by:
- Extracting content from URLs or accepting pasted text
- Using AI to intelligently split content into tweet-sized chunks
- Providing an intuitive interface for editing and refining threads
- Supporting one-click copying of individual tweets or entire threads

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

- **Backend**: Python FastAPI with async support
- **Frontend**: Alpine.js + Tailwind CSS (no build process)
- **AI**: OpenAI GPT-3.5-turbo for content analysis
- **Caching**: Redis for rate limiting and session management
- **Deployment**: Railway (backend) + Vercel (frontend)
- **Security**: Cloudflare protection, CORS, rate limiting

## 📋 Project Status

- ✅ **Backend**: Feature complete with thread generation, rate limiting, and health checks
- ✅ **Railway Deployment**: Live at https://threadr-production.up.railway.app
- ✅ **Frontend**: Live at https://threadr-plum.vercel.app
- ✅ **OpenAI Integration**: Working with graceful fallback handling
- ✅ **URL Scraping**: Fully functional for all allowed domains
- ✅ **Production Ready**: Both frontend and backend are deployed and working

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Redis (optional, for rate limiting)
- OpenAI API key

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
# Edit .env with your configuration

# Create OpenAI API key file (optional)
echo "your-openai-api-key" > .openai_key

# Run the development server
uvicorn src.main:app --reload --port 8001
```

The API will be available at `http://localhost:8001`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# No build process needed! Choose one:

# Option 1: Open directly in browser
open src/index.html  # macOS
# OR
start src/index.html  # Windows

# Option 2: Use a local server
python -m http.server 8000
# Visit http://localhost:8000/src/

# Option 3: Use Node.js serve
npx serve src/
```

## 📚 API Documentation

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/generate` | Generate thread from URL or text |
| POST | `/api/capture-email` | Capture user email for updates |
| GET | `/health` | Health check endpoint |
| GET | `/readiness` | Readiness probe for deployment |
| GET | `/api/rate-limit-status` | Check current rate limit status |

For detailed API documentation, see [docs/api/](docs/api/).

## 🔒 Security Features

- **Rate Limiting**: IP-based with Redis backend (10 requests/hour)
- **CORS Protection**: Configured for production domains
- **Input Validation**: Comprehensive request validation
- **SSRF Protection**: URL allowlist and private IP blocking
- **Security Headers**: CSP, HSTS, XSS protection
- **API Key Authentication**: Optional authentication support

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

## 🛣️ Roadmap

### Phase 1: MVP (Current)
- [x] Basic thread generation
- [x] URL content extraction
- [x] Rate limiting
- [ ] Frontend implementation
- [ ] Email capture

### Phase 2: Enhancement
- [ ] Thread templates
- [ ] Image support
- [ ] Thread scheduling
- [ ] Analytics dashboard

### Phase 3: Monetization
- [ ] Stripe payment integration
- [ ] Usage tiers
- [ ] Team accounts
- [ ] API access

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent async framework
- OpenAI for GPT-3.5-turbo API
- Alpine.js for the reactive frontend
- Tailwind CSS for utility-first styling

## 📞 Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/yourusername/threadr/issues)
- Email: support@threadr.app

---

Built with ❤️ for content creators who love Twitter threads