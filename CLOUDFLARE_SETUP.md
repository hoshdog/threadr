# Cloudflare Security Setup for Threadr

## Overview
This guide covers setting up Cloudflare as a security layer for your Threadr application to protect against DDoS attacks, bots, and other threats.

## Step 1: Basic Cloudflare Setup

1. **Add your domain to Cloudflare**:
   - Sign up at cloudflare.com
   - Add your domain (e.g., threadr.app)
   - Update nameservers at your registrar

2. **DNS Configuration**:
   ```
   Type    Name    Content                     Proxy
   CNAME   @       threadr-api.railway.app     ✓ (Orange cloud)
   CNAME   www     threadr-api.railway.app     ✓ (Orange cloud)
   CNAME   api     threadr-api.railway.app     ✓ (Orange cloud)
   ```

## Step 2: Security Settings

### SSL/TLS Configuration
1. Go to **SSL/TLS** → **Overview**
2. Set encryption mode to **Full (strict)**
3. Enable **Always Use HTTPS**
4. Enable **Automatic HTTPS Rewrites**

### Security Level
1. Go to **Security** → **Settings**
2. Set Security Level to **High**
3. Challenge Passage: **30 minutes**
4. Browser Integrity Check: **On**

## Step 3: Rate Limiting Rules

### Create Rate Limiting Rules
1. Go to **Security** → **WAF** → **Rate limiting rules**

2. **Rule 1: API Endpoint Protection**
   ```
   Rule name: API Rate Limit
   Path: /api/*
   Requests: 60 per 1 minute
   Response: Challenge (429)
   Characteristics: IP
   ```

3. **Rule 2: Aggressive Bot Protection**
   ```
   Rule name: Block Suspicious Bots
   Path: /*
   Requests: 100 per 1 minute
   Response: Block
   Characteristics: IP + User Agent
   ```

4. **Rule 3: Generate Endpoint Protection**
   ```
   Rule name: Protect Generate Endpoint
   Path: /api/generate
   Requests: 20 per 1 hour
   Response: Challenge
   Characteristics: IP
   ```

## Step 4: Firewall Rules

Go to **Security** → **WAF** → **Custom rules**

### Rule 1: Block Bad Bots
```
Expression: 
(http.user_agent contains "bot" and not http.user_agent contains "googlebot" and not http.user_agent contains "bingbot") or
(http.user_agent eq "") or
(http.user_agent contains "curl") or
(http.user_agent contains "wget") or
(http.user_agent contains "python-requests")

Action: Challenge
```

### Rule 2: Geo-blocking (Optional)
```
Expression:
(ip.geoip.country in {"CN" "RU" "KP"} and not cf.threat_score lt 10)

Action: Challenge
```

### Rule 3: Block Suspicious Patterns
```
Expression:
(http.request.uri.query contains "UNION" or 
 http.request.uri.query contains "SELECT" or
 http.request.uri.query contains "<script" or
 http.request.uri.query contains "javascript:" or
 http.request.body.raw contains "UNION SELECT")

Action: Block
```

### Rule 4: Protect Against Large Payloads
```
Expression:
(http.request.body.size gt 1048576)

Action: Block
```

## Step 5: Page Rules

1. Go to **Rules** → **Page Rules**

### Rule 1: Cache Static Assets
```
URL: *.threadr.app/*.{js,css,jpg,jpeg,png,gif,svg,ico,woff,woff2}
Settings:
- Cache Level: Cache Everything
- Edge Cache TTL: 1 month
- Browser Cache TTL: 1 week
```

### Rule 2: API Performance
```
URL: api.threadr.app/*
Settings:
- Cache Level: Bypass
- Disable Performance
- Security Level: High
```

## Step 6: DDoS Protection

### Enable Advanced DDoS Protection
1. Go to **Security** → **DDoS**
2. Enable **Advanced DDoS Protection**
3. Set sensitivity to **High**

### Configure DDoS Alert
1. Create alerting for L7 DDoS attacks
2. Set threshold: 1000 requests per second
3. Alert via email and webhook

## Step 7: Bot Management (Pro Plan)

If on Pro plan or higher:

1. **Bot Fight Mode**: Enable
2. **Super Bot Fight Mode**: 
   - Definitely automated: Challenge
   - Likely automated: Challenge
   - Verified bots: Allow

## Step 8: Security Headers

Add these via Transform Rules:

1. Go to **Rules** → **Transform Rules** → **Modify Response Header**

```
Header: Strict-Transport-Security
Value: max-age=31536000; includeSubDomains; preload

Header: X-Content-Type-Options
Value: nosniff

Header: X-Frame-Options
Value: DENY

Header: Referrer-Policy
Value: strict-origin-when-cross-origin
```

## Step 9: Analytics and Monitoring

### Set Up Alerts
1. Go to **Analytics** → **Notifications**
2. Create alerts for:
   - DDoS attacks
   - Origin errors (5xx)
   - SSL certificate issues
   - Spike in 4xx errors

### Enable Logging
1. Consider Cloudflare Logpush for detailed logs
2. Send to your SIEM or log aggregator

## Step 10: Additional Recommendations

### 1. Enable Cloudflare Turnstile
Replace traditional CAPTCHAs with Turnstile for better UX:
```javascript
// Frontend implementation
<div class="cf-turnstile" 
     data-sitekey="your-site-key"
     data-callback="onTurnstileSuccess">
</div>
```

### 2. Configure Cloudflare Workers (Optional)
Create edge functions for additional validation:

```javascript
// Example Worker for API key validation
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const apiKey = request.headers.get('X-API-Key')
  
  if (!apiKey) {
    return new Response('API Key required', { status: 403 })
  }
  
  // Forward valid requests
  return fetch(request)
}
```

### 3. Set Up Cloudflare Access (Zero Trust)
For admin endpoints:
1. Create Access application
2. Set authentication method (Google, GitHub, etc.)
3. Protect `/admin/*` routes

## Testing Your Setup

### 1. Test Rate Limiting
```bash
# Should get challenged after threshold
for i in {1..100}; do
  curl -X POST https://api.threadr.app/api/generate \
    -H "Content-Type: application/json" \
    -d '{"text":"test"}'
done
```

### 2. Test Security Headers
```bash
curl -I https://api.threadr.app/health
# Check for security headers in response
```

### 3. Test Bot Protection
```bash
# Should be challenged or blocked
curl -A "BadBot" https://api.threadr.app/
```

## Monitoring Dashboard

Create a custom Cloudflare dashboard to monitor:
- Request volume
- Cache hit ratio
- Threat events blocked
- Rate limit triggers
- Origin response times
- 4xx/5xx error rates

## Cost Optimization

1. **Free Plan Limits**:
   - 10M requests/month
   - Basic DDoS protection
   - 3 page rules

2. **When to Upgrade**:
   - Need more page rules → Pro ($25/month)
   - Advanced bot protection → Pro
   - Custom WAF rules → Pro
   - Load balancing → Load Balancing addon

## Emergency Response

If under active attack:

1. **Enable "I'm Under Attack" Mode**:
   - Security → Settings → I'm Under Attack Mode

2. **Increase Challenge Passage**:
   - Set to 1 day during attack

3. **Block Specific Countries**:
   - Create firewall rule to block attacking regions

4. **Contact Cloudflare**:
   - Pro plans have priority support

## Integration with Railway Backend

Update your Railway environment variables:
```
TRUSTED_PROXIES=173.245.48.0/20,103.21.244.0/22,103.22.200.0/22,103.31.4.0/22,141.101.64.0/18,108.162.192.0/18,190.93.240.0/20,188.114.96.0/20,197.234.240.0/22,198.41.128.0/17,162.158.0.0/15,104.16.0.0/13,104.24.0.0/14,172.64.0.0/13,131.0.72.0/22
REAL_IP_HEADER=CF-Connecting-IP
```

This ensures your app correctly identifies client IPs behind Cloudflare.