# Next.js Threadr Fixes Checklist
*Specific changes needed to make it "look right" and work properly*

## 🎨 Phase 1: Twitter/X Visual Alignment (Day 1-2)

### 1. Color System Overhaul
**File: `threadr-nextjs/src/app/globals.css`**
- [ ] Replace ALL color definitions with Twitter palette:
  ```css
  :root {
    --twitter-blue: #1d9bf0;
    --twitter-dark: #15202b;
    --twitter-black: #000000;
    --twitter-gray: #8899ac;
    --twitter-border: #38444d;
    --twitter-hover: #1a8cd8;
  }
  ```
- [ ] Remove generic color variables
- [ ] Update all color classes to use Twitter colors

**File: `threadr-nextjs/tailwind.config.ts`**
- [ ] Add Twitter color palette to theme.extend.colors
- [ ] Remove generic blue scales
- [ ] Set black as primary background

### 2. Logo Implementation
**Action: Copy logo files**
- [ ] Copy `frontend/public/logos/threadrLogo_White_Cropped.PNG` to `threadr-nextjs/public/logos/`
- [ ] Copy `frontend/public/logos/threadrLogo_Black_Cropped.PNG` to `threadr-nextjs/public/logos/`
- [ ] Copy favicon files

**File: `threadr-nextjs/src/app/layout.tsx`**
- [ ] Update favicon link to use Threadr logo
- [ ] Add proper meta tags with logo

**Files: All pages using gradient boxes**
- [ ] Replace gradient divs with Image component using logo
- [ ] Add proper alt text and sizing

### 3. Sidebar Navigation Conversion
**File: `threadr-nextjs/src/app/(dashboard)/layout.tsx`**
- [ ] Convert from top nav to left sidebar
- [ ] Match Twitter's sidebar structure:
  - Logo at top
  - Navigation items with icons
  - User section at bottom
  - Dropdown menu for user
- [ ] Add mobile hamburger menu
- [ ] Implement Twitter-style hover states

### 4. Button Styling Update
**File: `threadr-nextjs/src/components/ui/Button.tsx`**
- [ ] Update primary variant to use `rounded-full`
- [ ] Change colors to Twitter blue
- [ ] Add Twitter-style hover/focus states
- [ ] Remove unnecessary variants

### 5. Typography Alignment
**File: `threadr-nextjs/src/app/globals.css`**
- [ ] Match Twitter font sizes and weights
- [ ] Update line heights and spacing
- [ ] Ensure Inter font is primary

## 🔌 Phase 2: Backend Connection (Day 3-5)

### 1. API Configuration Fix
**File: `threadr-nextjs/.env.local`**
- [ ] Create/update with production API:
  ```
  NEXT_PUBLIC_API_URL=https://threadr-production.up.railway.app
  NEXT_PUBLIC_API_KEY=zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8
  ```

**File: `threadr-nextjs/src/lib/api/client.ts`**
- [ ] Update base URL to use env variable
- [ ] Add API key to headers
- [ ] Test connection with health endpoint

### 2. Thread Generation Connection
**File: `threadr-nextjs/src/lib/api/threads.ts`**
- [ ] Implement real generateThread function:
  ```typescript
  async generateThread(data: GenerateThreadRequest): Promise<GenerateThreadResponse> {
    return this.client.post('/api/generate', data);
  }
  ```
- [ ] Remove mock data returns
- [ ] Add proper error handling

**File: `threadr-nextjs/src/hooks/api/useThreads.ts`**
- [ ] Update useGenerateThread to call real API
- [ ] Add loading and error states
- [ ] Handle rate limiting responses

### 3. Authentication Integration
**File: `threadr-nextjs/src/lib/api/auth.ts`**
- [ ] Connect login to `/api/auth/login`
- [ ] Connect register to `/api/auth/register`
- [ ] Implement token refresh logic
- [ ] Store tokens securely

**File: `threadr-nextjs/src/contexts/auth.tsx`**
- [ ] Load user from token on mount
- [ ] Implement logout that clears tokens
- [ ] Add token to API requests

### 4. Payment Integration
**File: `threadr-nextjs/src/lib/api/subscriptions.ts`**
- [ ] Add createCheckoutSession function
- [ ] Add verifyPremiumStatus function
- [ ] Handle webhook callbacks

**File: `threadr-nextjs/src/components/PremiumUpgradeModal.tsx`**
- [ ] Create component for upgrade flow
- [ ] Connect to Stripe checkout
- [ ] Handle success/cancel

## ✅ Phase 3: Feature Completion (Day 6-7)

### 1. Rate Limiting UI
**File: `threadr-nextjs/src/hooks/api/useUsageStats.ts`**
- [ ] Fetch real usage from `/api/usage-stats`
- [ ] Calculate remaining limits
- [ ] Trigger upgrade prompts

**File: `threadr-nextjs/src/components/thread/UsageIndicator.tsx`**
- [ ] Show real usage data
- [ ] Add upgrade button at limits
- [ ] Display premium expiry

### 2. Thread History Backend
**File: `threadr-nextjs/src/hooks/api/useThreads.ts`**
- [ ] Connect to `/api/threads` endpoints
- [ ] Implement save thread functionality
- [ ] Add delete thread API call

### 3. Email Capture
**File: `threadr-nextjs/src/components/EmailCaptureForm.tsx`**
- [ ] Create email capture component
- [ ] Connect to `/api/capture-email`
- [ ] Add to thread generation success

### 4. Analytics Connection
**File: `threadr-nextjs/src/app/analytics/page.tsx`**
- [ ] Fetch real data from `/api/analytics`
- [ ] Create charts with real metrics
- [ ] Add export functionality

## 🧪 Testing Checklist

### Visual Testing
- [ ] Compare side-by-side with production Alpine.js app
- [ ] Verify Twitter blue throughout
- [ ] Check logo appears correctly
- [ ] Confirm sidebar matches Twitter style

### Functional Testing
- [ ] Generate thread from URL
- [ ] Generate thread from text
- [ ] Hit rate limit and see upgrade prompt
- [ ] Complete payment flow
- [ ] Verify premium features unlock
- [ ] Save and load thread history

### API Testing
- [ ] All endpoints return 200 (not 404)
- [ ] Authentication tokens work
- [ ] Rate limiting enforced
- [ ] Premium status verified

## 📋 Definition of Done

The Next.js app is "right" when:
1. **Looks exactly like Twitter/X native tool** (not generic SaaS)
2. **All core features work with backend** (not mock data)
3. **Users can pay and become premium** (revenue generation works)
4. **Matches or exceeds Alpine.js functionality** (no regressions)
5. **Loads fast and feels responsive** (better performance)

## 🚀 Deployment Readiness

Before replacing Alpine.js version:
- [ ] All checklist items completed
- [ ] Tested with 5+ real users
- [ ] Conversion funnel verified
- [ ] No console errors
- [ ] Lighthouse score > 90
- [ ] Revenue tracking confirmed