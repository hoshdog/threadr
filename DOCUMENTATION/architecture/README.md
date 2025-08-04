# Architecture Documentation

> **🏗️ SYSTEM ARCHITECTURE**: Complete technical architecture for Threadr SaaS platform

## Architecture Overview

Threadr uses a modern, scalable architecture designed to handle the transition from MVP to enterprise-scale SaaS platform. The system is built with clear separation of concerns, horizontal scalability, and security as core principles.

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Users/CDN     │    │   Application   │    │   Data Layer    │
│                 │    │     Layer       │    │                 │
│ • Global CDN    │◄──►│ • Frontend App  │◄──►│ • Redis Cache   │
│ • DDoS Protection│    │ • Backend API   │    │ • PostgreSQL    │
│ • SSL/Security  │    │ • Auth Service  │    │ • File Storage  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   External      │    │   Integration   │    │   Monitoring    │
│   Services      │    │     Layer       │    │                 │
│                 │    │                 │    │ • Health Checks │
│ • OpenAI API    │◄──►│ • Payment Proc  │◄──►│ • Error Tracking│
│ • Stripe API    │    │ • Email Service │    │ • Performance   │
│ • Email API     │    │ • Analytics     │    │ • Business KPIs │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Current Production Architecture

### Architecture Stack (LIVE)
- **Frontend**: Alpine.js + Tailwind CSS (260KB monolithic app)
- **Hosting**: Vercel (global CDN, automatic SSL)
- **Backend**: Python FastAPI (async/await, 95.7% test coverage)
- **Hosting**: Railway (container deployment, auto-scaling)
- **Database**: Redis (Upstash managed, global distribution)
- **Payments**: Stripe (webhooks, HMAC verification)
- **External APIs**: OpenAI GPT-3.5-turbo

### Data Flow (Current)
```
User Input → Frontend Validation → Backend API → OpenAI API → Thread Generation
    ↓              ↓                   ↓             ↓              ↓
Browser JS     Alpine.js          FastAPI      GPT-3.5-turbo   Response
    ↓              ↓                   ↓             ↓              ↓
Rate Check ←── Redis Cache ←───── Security ←─── Processing → Frontend Display
```

### Request Flow
1. **User Request**: User enters content or URL
2. **Frontend Processing**: Alpine.js validates input and shows loading state
3. **API Call**: Secure HTTPS request to FastAPI backend
4. **Authentication**: JWT token validation (when available)
5. **Rate Limiting**: Redis-based IP and user rate limiting
6. **Content Processing**: URL scraping or direct content processing
7. **AI Generation**: OpenAI API call for thread generation
8. **Response**: Structured thread response with tweets
9. **Caching**: Cache results for performance
10. **Frontend Display**: Real-time thread display with editing

## Target Architecture (Next.js Migration)

### Future Architecture Stack
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **State Management**: React Query + Zustand
- **Backend**: Same FastAPI (maintain stability)
- **Database**: PostgreSQL + Redis (persistence + caching)
- **Payments**: Enhanced Stripe integration
- **Monitoring**: Advanced analytics and error tracking

### Enhanced Data Flow
```
SSR/SSG → Component Hydration → API Integration → Server State → Client State
    ↓            ↓                    ↓               ↓             ↓
Next.js      React Query        FastAPI API    PostgreSQL    Zustand Store
    ↓            ↓                    ↓               ↓             ↓
SEO Opt ←── Performance ←───── Business Logic ← Persistence ← UI State
```

## System Components

### Frontend Architecture

#### Current (Alpine.js)
```
┌─────────────────────────────────────────────────────────────┐
│                    Single HTML File                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Alpine    │  │  Tailwind   │  │   Vanilla   │         │
│  │ Reactivity  │  │    CSS      │  │ JavaScript  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
│  Pros: Simple, Fast Development, No Build Process           │
│  Cons: Limited Scalability, No Component Reuse             │
└─────────────────────────────────────────────────────────────┘
```

#### Target (Next.js)
```
┌─────────────────────────────────────────────────────────────┐
│                   Component Architecture                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   React     │  │    Next.js  │  │ TypeScript  │         │
│  │ Components  │  │  App Router │  │Type Safety  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │React Query  │  │   Zustand   │  │  Tailwind   │         │
│  │Server State │  │Client State │  │    CSS      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
│  Pros: Scalable, Maintainable, Performance                 │
│  Cons: Complex Setup, Learning Curve                       │
└─────────────────────────────────────────────────────────────┘
```

### Backend Architecture

#### FastAPI Service Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                        │
│                                                              │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   API Routes    │    │   Middleware    │                │
│  │                 │    │                 │                │
│  │ • Authentication│    │ • CORS Handler  │                │
│  │ • Thread Gen    │    │ • Rate Limiting │                │
│  │ • User Mgmt     │    │ • Error Handler │                │ 
│  │ • Analytics     │    │ • Logging       │                │
│  └─────────────────┘    └─────────────────┘                │
│           │                       │                         │
│           ▼                       ▼                         │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Services      │    │   Data Models   │                │
│  │                 │    │                 │                │
│  │ • Auth Service  │    │ • User Models   │                │
│  │ • Thread Service│    │ • Thread Models │                │
│  │ • Payment Svc   │    │ • Analytics     │                │
│  │ • Analytics Svc │    │ • Validation    │                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

#### Service Layer Details
```python
# Service Architecture Pattern
class ThreadService:
    def __init__(self, db: Database, openai_client: OpenAI):
        self.db = db
        self.openai = openai_client
    
    async def generate_thread(self, content: str, user_id: str) -> Thread:
        # Business logic for thread generation
        pass
    
    async def save_thread(self, thread: Thread) -> Thread:
        # Data persistence logic
        pass

class AuthService:
    def __init__(self, db: Database, jwt_handler: JWTHandler):
        self.db = db
        self.jwt = jwt_handler
    
    async def authenticate_user(self, email: str, password: str) -> User:
        # Authentication business logic
        pass
```

### Database Architecture

#### Current (Redis-Only)
```
┌─────────────────────────────────────────────────────────────┐
│                    Redis Data Store                          │
│                                                              │
│  Key-Value Store:                                           │
│  ├── user_sessions:{user_id} → User session data           │
│  ├── rate_limit:{ip} → Rate limiting counters              │
│  ├── premium_access:{user_id} → Premium status             │ 
│  ├── thread_cache:{content_hash} → Cached thread results   │
│  └── email_captures:{email} → Email marketing data         │
│                                                              │
│  Pros: Fast, Simple, Low Latency                           │
│  Cons: Limited Queries, No Relationships, Volatile         │
└─────────────────────────────────────────────────────────────┘
```

#### Target (PostgreSQL + Redis)
```
┌─────────────────────────────────────────────────────────────┐
│                 Hybrid Data Architecture                     │
│                                                              │
│  ┌─────────────────────┐    ┌─────────────────────┐         │
│  │    PostgreSQL       │    │       Redis         │         │
│  │  (Persistent Data)  │    │   (Cache & Sessions)│         │
│  │                     │    │                     │         │
│  │ • Users             │    │ • Session Cache     │         │
│  │ • Threads           │    │ • Rate Limiting     │         │
│  │ • Subscriptions     │    │ • Thread Cache      │         │
│  │ • Analytics         │    │ • Real-time Data    │         │
│  │ • Audit Logs        │    │ • Temporary Storage │         │
│  └─────────────────────┘    └─────────────────────┘         │
│                                                              │
│  Benefits: ACID Compliance + Performance + Scalability     │
└─────────────────────────────────────────────────────────────┘
```

### Security Architecture

#### Multi-Layer Security Model
```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
│                                                              │
│  Layer 1: Network Security                                 │
│  ├── Cloudflare DDoS Protection                            │
│  ├── SSL/TLS Encryption (HTTPS)                            │
│  └── IP-based Rate Limiting                                │
│                                                              │
│  Layer 2: Application Security                             │
│  ├── JWT Authentication                                     │
│  ├── Input Validation & Sanitization                       │
│  ├── CORS Protection                                        │
│  └── API Rate Limiting                                     │
│                                                              │
│  Layer 3: Data Security                                    │
│  ├── Database Encryption at Rest                           │
│  ├── Secure API Key Management                             │
│  ├── Payment Security (Stripe)                             │
│  └── Audit Logging                                         │
│                                                              │
│  Layer 4: Business Logic Security                          │
│  ├── Role-based Access Control                             │
│  ├── Usage Limits & Quotas                                 │
│  ├── Content Filtering                                     │
│  └── Fraud Detection                                       │
└─────────────────────────────────────────────────────────────┘
```

## Scalability Architecture

### Current Scalability (MVP)
- **Frontend**: Vercel global CDN (automatically scalable)
- **Backend**: Railway auto-scaling (vertical scaling)
- **Database**: Redis cluster (Upstash managed)
- **Capacity**: ~100-500 concurrent users

### Target Scalability (Growth)
```
┌─────────────────────────────────────────────────────────────┐
│                   Horizontal Scaling                        │
│                                                              │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Load Balancer │    │  Auto Scaling   │                │
│  │                 │    │                 │                │
│  │ • Railway       │    │ • Multiple      │                │
│  │ • Health Checks │    │   Instances     │                │
│  │ • Failover      │    │ • Scale Up/Down │                │
│  └─────────────────┘    └─────────────────┘                │
│           │                       │                         │
│           ▼                       ▼                         │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Database      │    │    Caching      │                │
│  │   Scaling       │    │    Strategy     │                │
│  │                 │    │                 │                │
│  │ • Read Replicas │    │ • Redis Cluster │                │
│  │ • Sharding      │    │ • CDN Caching   │                │
│  │ • Connection    │    │ • Application   │                │
│  │   Pooling       │    │   Caching       │                │
│  └─────────────────┘    └─────────────────┘                │
│                                                              │
│  Capacity: 1000+ concurrent users                          │
└─────────────────────────────────────────────────────────────┘
```

## Performance Architecture

### Performance Optimization Strategy
```
┌─────────────────────────────────────────────────────────────┐
│                  Performance Layers                         │
│                                                              │
│  Frontend Performance:                                      │
│  ├── Next.js SSR/SSG (SEO + Speed)                        │
│  ├── Code Splitting (Lazy Loading)                        │
│  ├── Image Optimization (Next.js)                         │
│  ├── Caching Strategy (Browser + CDN)                     │
│  └── Core Web Vitals Optimization                         │
│                                                              │
│  Backend Performance:                                       │
│  ├── Async/Await (Non-blocking I/O)                       │
│  ├── Connection Pooling (DB + Redis)                      │
│  ├── Query Optimization (Indexes)                         │
│  ├── Response Caching (Redis)                             │
│  └── API Rate Limiting (Prevent Abuse)                    │
│                                                              │
│  Infrastructure Performance:                                │
│  ├── Global CDN (Vercel Edge Network)                     │
│  ├── Database Optimization (Indexes)                      │
│  ├── Container Optimization (Docker)                      │
│  └── Monitoring & Alerting (APM)                          │
└─────────────────────────────────────────────────────────────┘
```

### Performance Targets
- **Frontend Loading**: <2 seconds (Lighthouse 90+)
- **API Response Time**: <500ms (95th percentile)
- **Thread Generation**: <3 seconds (including OpenAI)
- **Database Queries**: <100ms (simple), <500ms (complex)
- **Uptime**: 99.9% (8.76 hours downtime/year)

## Integration Architecture

### External Service Integration
```
┌─────────────────────────────────────────────────────────────┐
│                External Service Integration                  │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   OpenAI    │  │   Stripe    │  │   Email     │         │
│  │     API     │  │ Payments    │  │  Service    │         │
│  │             │  │             │  │             │         │
│  │• GPT-3.5    │  │• Webhooks   │  │• Transact   │         │
│  │• Rate Limit │  │• HMAC Sig   │  │• Marketing  │         │
│  │• Error      │  │• PCI Compliant│ │• Templates │         │
│  │  Handling   │  │• Retry Logic│  │• Analytics  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                 │                 │               │
│         ▼                 ▼                 ▼               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Circuit Breaker Pattern                    │ │
│  │ • Automatic Failover                                   │ │
│  │ • Exponential Backoff                                  │ │
│  │ • Health Monitoring                                    │ │
│  │ • Graceful Degradation                                 │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### API Integration Patterns
```python
# Circuit Breaker Pattern for External APIs
class OpenAIService:
    def __init__(self):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=OpenAIError
        )
    
    @self.circuit_breaker
    async def generate_thread(self, content: str) -> Thread:
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": content}],
                timeout=30
            )
            return self.parse_response(response)
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise OpenAIError(f"Thread generation failed: {e}")
```

## Monitoring Architecture

### Observability Stack
```
┌─────────────────────────────────────────────────────────────┐
│                   Monitoring & Observability                │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Metrics   │  │    Logs     │  │   Traces    │         │
│  │             │  │             │  │             │         │
│  │• App Metrics│  │• Structured │  │• Request    │         │
│  │• Business   │  │  Logging    │  │  Tracing    │         │
│  │  KPIs       │  │• Error      │  │• Performance│         │
│  │• System     │  │  Tracking   │  │  Analysis   │         │
│  │  Health     │  │• Audit      │  │• Bottleneck │         │
│  │             │  │  Trail      │  │  Detection  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                 │                 │               │
│         ▼                 ▼                 ▼               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Alerting System                         │ │
│  │ • Real-time Alerts                                     │ │
│  │ • SLA Monitoring                                       │ │
│  │ • Anomaly Detection                                    │ │
│  │ • Escalation Procedures                                │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

### Multi-Environment Strategy
```
┌─────────────────────────────────────────────────────────────┐
│                 Deployment Environments                     │
│                                                              │
│  Development → Staging → Production                        │
│       │           │          │                              │
│       ▼           ▼          ▼                              │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                      │
│  │  Local  │ │ Preview │ │  Live   │                      │
│  │   Dev   │ │ Deploy  │ │  Prod   │                      │
│  │         │ │         │ │         │                      │
│  │• Hot    │ │• Feature│ │• Main   │                      │
│  │  Reload │ │  Branch │ │  Branch │                      │
│  │• Debug  │ │• Testing│ │• Stable │                      │
│  │  Mode   │ │• Review │ │• Monitored                      │
│  └─────────┘ └─────────┘ └─────────┘                      │
│                                                              │
│  CI/CD Pipeline: GitHub Actions → Auto Deploy             │
└─────────────────────────────────────────────────────────────┘
```

## Migration Architecture

### Alpine.js to Next.js Migration Strategy
```
┌─────────────────────────────────────────────────────────────┐
│                    Migration Strategy                        │
│                                                              │
│  Phase 1: Parallel Deployment                              │
│  ┌─────────────┐              ┌─────────────┐             │
│  │  Alpine.js  │              │  Next.js    │             │  
│  │ (Production)│◄─────────────┤ (Staging)   │             │
│  │             │   Traffic    │             │             │
│  │ • 100% Live │   Splitting  │ • 0% Live   │             │
│  │ • Stable    │              │ • Testing   │             │
│  └─────────────┘              └─────────────┘             │
│                                                              │
│  Phase 2: Gradual Migration                                │
│  ┌─────────────┐              ┌─────────────┐             │
│  │  Alpine.js  │              │  Next.js    │             │
│  │ (90% Traffic)│◄─────────────┤(10% Traffic)│             │
│  │             │   A/B Test   │             │             │
│  │ • Monitor   │              │ • Validate  │             │
│  │ • Support   │              │ • Optimize  │             │
│  └─────────────┘              └─────────────┘             │
│                                                              │
│  Phase 3: Complete Migration                               │
│  ┌─────────────┐              ┌─────────────┐             │
│  │  Alpine.js  │              │  Next.js    │             │
│  │ (Retired)   │              │(100% Traffic)│             │
│  │             │              │             │             │
│  │ • Archive   │              │ • Production│             │
│  │ • Backup    │              │ • Optimized │             │
│  └─────────────┘              └─────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

## Architecture Decision Records (ADRs)

### ADR-001: Frontend Framework Choice
- **Decision**: Start with Alpine.js, migrate to Next.js
- **Reasoning**: Rapid MVP development, then scale for growth
- **Status**: Alpine.js in production, Next.js ready for migration

### ADR-002: Backend Framework Choice
- **Decision**: FastAPI with Python
- **Reasoning**: Async support, automatic docs, strong typing
- **Status**: Production stable with 95.7% test coverage

### ADR-003: Database Strategy
- **Decision**: Redis for MVP, PostgreSQL for growth
- **Reasoning**: Fast development, then data persistence
- **Status**: Redis live, PostgreSQL migration planned

### ADR-004: Payment Processing
- **Decision**: Stripe with webhook integration
- **Reasoning**: PCI compliance, developer experience
- **Status**: Production stable with HMAC verification

### ADR-005: Deployment Strategy
- **Decision**: Vercel + Railway dual deployment
- **Reasoning**: Optimal performance and cost for each service
- **Status**: Production stable with auto-deployment

---

**🏗️ Scalable architecture supporting growth from MVP to $50K+ MRR**

*Modern, secure, and performance-optimized system design*