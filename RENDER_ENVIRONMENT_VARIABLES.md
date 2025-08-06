# 🔐 Render Environment Variables Configuration

## Required Environment Variables for Full Functionality

### ✅ Already Set (Per Your Confirmation)
1. **REDIS_URL**: `redis://red-d29f5k2li9vc73flfkt0:6379`
2. **OPENAI_API_KEY**: (Set with $5.00 budget)

### 🔴 CRITICAL - Must Add Immediately

#### 1. JWT_SECRET_KEY
**Purpose**: Secure token generation for authentication
**How to Generate**:
```python
# Option 1: Use Python to generate
import secrets
print(secrets.token_urlsafe(32))
```
```bash
# Option 2: Use OpenSSL
openssl rand -base64 32
```
**Add to Render**:
- Key: `JWT_SECRET_KEY`
- Value: (your generated secret)
- Example: `your-very-long-random-secret-key-here-at-least-32-chars`

#### 2. STRIPE_SECRET_KEY
**Purpose**: Payment processing
**Get from**: https://dashboard.stripe.com/apikeys
- Key: `STRIPE_SECRET_KEY`
- Value: `sk_test_...` (for testing) or `sk_live_...` (for production)

#### 3. STRIPE_WEBHOOK_SECRET
**Purpose**: Secure webhook verification
**Get from**: Stripe Dashboard → Webhooks → Your endpoint
- Key: `STRIPE_WEBHOOK_SECRET`
- Value: `whsec_...`

### 🟡 Optional but Recommended

#### 4. CORS_ORIGINS
**Purpose**: Allow frontend to connect
**Default**: `http://localhost:3000`
**Production Value**: `https://threadr-plum.vercel.app`
- Key: `CORS_ORIGINS`
- Value: `https://threadr-plum.vercel.app`

#### 5. FREE_TIER_DAILY_LIMIT
**Purpose**: Control free tier limits
**Default**: 5
- Key: `FREE_TIER_DAILY_LIMIT`
- Value: `5`

#### 6. FREE_TIER_MONTHLY_LIMIT
**Purpose**: Control monthly limits
**Default**: 20
- Key: `FREE_TIER_MONTHLY_LIMIT`
- Value: `20`

---

## How to Add Environment Variables in Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Select your service**: threadr-backend
3. **Click "Environment"** in the left sidebar
4. **Click "Add Environment Variable"**
5. **Enter Key and Value**
6. **Click "Save Changes"**
7. **Service will auto-redeploy**

---

## Complete Environment Variables List

### Currently Set (Automatic from render.yaml):
- ✅ `PYTHON_VERSION`: 3.11.9
- ✅ `PYTHONUNBUFFERED`: 1
- ✅ `ENVIRONMENT`: production
- ✅ `PYTHONPATH`: /opt/render/project/src/backend
- ✅ `BYPASS_DATABASE`: true

### User Already Added:
- ✅ `REDIS_URL`: redis://red-d29f5k2li9vc73flfkt0:6379
- ✅ `OPENAI_API_KEY`: (with $5.00 budget)

### Still Need to Add:
- 🔴 `JWT_SECRET_KEY`: (generate secure key)
- 🟡 `STRIPE_SECRET_KEY`: (if using payments)
- 🟡 `STRIPE_WEBHOOK_SECRET`: (if using payments)
- 🟡 `CORS_ORIGINS`: https://threadr-plum.vercel.app

---

## Quick JWT Secret Generation

### Option 1: Quick Python Command
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Option 2: Use This Example (CHANGE FOR PRODUCTION!)
```
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
```

### Option 3: Generate UUID
```bash
python -c "import uuid; print(str(uuid.uuid4()) + str(uuid.uuid4()))"
```

---

## Verification After Adding

After adding JWT_SECRET_KEY, verify with:
```bash
curl https://threadr-pw0s.onrender.com/health
```

Should show:
```json
{
  "status": "healthy",
  "services": {
    "redis": true,
    "routes": true
  }
}
```

---

## Complete Working Example

Here are ALL the environment variables you should have:

```env
# Core Settings (from render.yaml)
PYTHON_VERSION=3.11.9
PYTHONUNBUFFERED=1
ENVIRONMENT=production
PYTHONPATH=/opt/render/project/src/backend
BYPASS_DATABASE=true

# Services (User Added)
REDIS_URL=redis://red-d29f5k2li9vc73flfkt0:6379
OPENAI_API_KEY=sk-...your-key...

# Security (MUST ADD)
JWT_SECRET_KEY=generate-this-secure-random-key-min-32-chars

# Frontend Connection (Recommended)
CORS_ORIGINS=https://threadr-plum.vercel.app

# Payments (Optional)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Rate Limits (Optional - defaults work)
FREE_TIER_DAILY_LIMIT=5
FREE_TIER_MONTHLY_LIMIT=20
```

---

## Priority Actions

1. **IMMEDIATE**: Add `JWT_SECRET_KEY` (security critical)
2. **IMPORTANT**: Add `CORS_ORIGINS` (frontend connectivity)
3. **WHEN READY**: Add Stripe keys (for payments)

---

**Time Required**: 5 minutes
**Impact**: Full functionality with secure authentication