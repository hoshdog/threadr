# 📁 Threadr File Location Index - Updated August 2025

## 🎯 Quick Reference - Where to Find What

### 🚀 Deployment & Configuration
| What | Where | Purpose |
|------|-------|---------|
| Vercel Config | `/vercel.json` | Next.js deployment from monorepo |
| Railway Config | `/nixpacks.toml` | Backend Python deployment |
| Docker Config | `/Dockerfile` | Container deployment option |
| Environment Examples | `/backend/.env.example` | Environment variable templates |
| Next.js Config | `/threadr-nextjs/vercel.json` | Next.js specific settings |

### 💻 Source Code
| Component | Location | Technology |
|-----------|----------|------------|
| Backend API | `/backend/src/` | Python FastAPI |
| Alpine.js Frontend | `/frontend/public/` | Legacy production app |
| Next.js Frontend | `/threadr-nextjs/src/` | Modern production app |
| Shared Assets | `/frontend/public/logos/` | Logo files (PNG) |

### 📚 Documentation (Consolidated)
| Category | Location | Contents |
|----------|----------|----------|
| API Docs | `/docs/api/` | Endpoints, authentication |
| Deployment | `/docs/deployment/` | Vercel, Railway, Docker guides |
| Development | `/docs/development/` | Setup, testing, Stripe |
| Architecture | `/docs/architecture/` | Technical decisions |
| Security | `/docs/security/` | Security guidelines |
| Guides | `/docs/guides/` | How-to guides |
| Project Status | `/docs/project/` | Status reports, summaries |

### 🧪 Testing & Scripts
| Type | Location | Purpose |
|------|----------|---------|
| Backend Tests | `/backend/tests/` | Python unit/integration tests |
| Frontend Tests | `/frontend/tests/` | Alpine.js test files |
| Utility Scripts | `/scripts/` | Deployment, security, cleanup |
| Operations | `/OPERATIONS/` | Monitoring, automation scripts |

### 🗄️ Archive & Legacy
| Content | Location | Status |
|---------|----------|--------|
| Old Documentation | `/archive/legacy-docs/` | Historical reference only |
| Test Reports | `/archive/test_reports/` | Past test results |
| Old Configs | `/archive/legacy-configs/` | Deprecated configurations |
| Test HTML Files | `/archive/test-files/` | Old debugging files |

## 🔍 Specific File Locations

### Critical Configuration Files
```
Root Directory (Clean - Only 7 Files):
├── CLAUDE.md                    # AI assistant instructions
├── Dockerfile                   # Container configuration
├── README.md                    # Project overview
├── index.html                   # Alpine.js entry (to be removed)
├── nixpacks.toml               # Railway deployment
├── package.json                # Root package config
└── vercel.json                 # Vercel monorepo config
```

### Backend Structure
```
backend/
├── src/
│   ├── main.py                 # FastAPI entry point
│   ├── core/
│   │   └── redis_manager.py    # Redis connection management
│   ├── routes/
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── subscription.py     # Stripe subscription handling
│   │   └── thread.py          # Thread generation
│   └── services/
│       ├── auth/              # JWT authentication
│       └── thread/            # OpenAI integration
├── requirements.txt           # Python dependencies
└── .env.example              # Environment template
```

### Next.js Frontend Structure
```
threadr-nextjs/
├── src/
│   ├── app/                   # Next.js 14 app directory
│   │   ├── (auth)/           # Auth pages (login, register)
│   │   ├── (dashboard)/      # Main app pages
│   │   └── page.tsx          # Home page
│   ├── components/           # React components
│   ├── lib/                  # Utilities and API client
│   └── hooks/               # Custom React hooks
├── public/                  # Static assets
├── package.json            # Dependencies
└── vercel.json            # Deployment config
```

### Documentation Organization
```
docs/
├── README.md                          # Documentation index
├── api/
│   ├── API_DOCUMENTATION.md          # Full API reference
│   └── API_ENDPOINTS_REFERENCE.md    # Quick endpoint guide
├── deployment/
│   ├── railway/
│   │   └── RAILWAY_DEPLOYMENT_GUIDE.md
│   ├── vercel/
│   │   └── VERCEL_DEPLOYMENT.md
│   └── NEXTJS_DEPLOYMENT_GUIDE.md    # Next.js specific
├── development/
│   ├── STRIPE_INTEGRATION.md         # Payment setup
│   └── TESTING_GUIDE.md              # Test procedures
└── security/
    └── SECURITY_CHECKLIST.md         # Security guidelines
```

## 🎮 Common Tasks - Where to Go

### To Deploy Next.js
1. Check `/vercel.json` for configuration
2. See `/docs/deployment/NEXTJS_DEPLOYMENT_GUIDE.md`
3. Environment vars in Vercel dashboard

### To Update Backend
1. Edit code in `/backend/src/`
2. Test with `/backend/tests/`
3. Deploy via Railway (auto-deploy on push)

### To Add Documentation
1. Choose appropriate category in `/docs/`
2. Follow existing naming conventions
3. Update this index if adding new sections

### To Run Scripts
1. Security cleanup: `/scripts/security-cleanup.py`
2. Organization: `/scripts/organize-root-directory.py`
3. Testing: `/scripts/test_backend_deployment.py`

## 🚨 Important Notes

### Security
- **NEVER** commit `.env` files (only `.env.example`)
- API keys should use placeholders in docs
- Run security cleanup script after updates

### Development
- Alpine.js frontend: Edit `/frontend/public/`
- Next.js frontend: Edit `/threadr-nextjs/src/`
- Backend API: Edit `/backend/src/`

### Deployment
- Frontend deploys automatically via Vercel
- Backend deploys automatically via Railway
- Both triggered by GitHub pushes

## 📊 Statistics After Cleanup

### Documentation
- **Before**: 940+ scattered files
- **After**: ~50 organized files (target)
- **Reduction**: 95%

### Root Directory
- **Before**: 30+ files
- **After**: 7 essential files
- **Improvement**: 77% cleaner

### File Organization
- **Moved**: 22 files to proper locations
- **Archived**: Legacy documentation
- **Active Docs**: Consolidated in `/docs/`

---
*Last Updated: August 2025*
*Maintained in: `/FILE_LOCATION_INDEX_UPDATED.md`*