# Production Security Checklist for Threadr

## Pre-Deployment Security Checklist

### 🔴 CRITICAL - Must Complete Before Production

- [ ] **API Authentication Implemented**
  - [ ] API key generation system in place
  - [ ] All endpoints require authentication (except health)
  - [ ] API keys stored as hashed values
  - [ ] Rate limiting per API key implemented

- [ ] **OpenAI API Key Secured**
  - [ ] Removed all file-based key loading
  - [ ] API key only loaded from environment variables
  - [ ] No API keys in source code or configs
  - [ ] Key rotation mechanism ready

- [ ] **Environment Variables Set**
  ```bash
  ENVIRONMENT=production
  OPENAI_API_KEY=sk-...
  CLIENT_API_KEYS=secure-random-key-1,secure-random-key-2
  CORS_ORIGINS=https://threadr.app,https://www.threadr.app
  ALLOWED_DOMAINS=medium.com,dev.to,hashnode.com
  ```

- [ ] **Remove Debug Endpoints**
  - [ ] `/debug/startup` removed or protected
  - [ ] `/docs` disabled in production
  - [ ] `/openapi.json` disabled in production
  - [ ] Stack traces hidden in error responses

### 🟠 HIGH Priority - Complete Within 24 Hours

- [ ] **Cloudflare Configuration**
  - [ ] Domain proxied through Cloudflare
  - [ ] SSL/TLS set to "Full (strict)"
  - [ ] Rate limiting rules configured
  - [ ] Firewall rules active
  - [ ] DDoS protection enabled

- [ ] **Input Validation**
  - [ ] URL validation prevents SSRF
  - [ ] Content length limits enforced
  - [ ] Request size limits implemented
  - [ ] Blocked internal/private IPs

- [ ] **Security Headers**
  - [ ] X-Content-Type-Options: nosniff
  - [ ] X-Frame-Options: DENY
  - [ ] Strict-Transport-Security configured
  - [ ] Content-Security-Policy implemented
  - [ ] Referrer-Policy set

- [ ] **Redis Rate Limiting**
  - [ ] Redis instance provisioned (Upstash)
  - [ ] Rate limiting using Redis
  - [ ] Distributed rate limiting tested
  - [ ] Graceful fallback if Redis fails

### 🟡 MEDIUM Priority - Complete Within 1 Week

- [ ] **Monitoring Setup**
  - [ ] Sentry error tracking configured
  - [ ] Cloudflare analytics enabled
  - [ ] Uptime monitoring active
  - [ ] Alert thresholds configured

- [ ] **Dependency Security**
  - [ ] All dependencies updated
  - [ ] Security scan completed (`safety check`)
  - [ ] No known vulnerabilities
  - [ ] Dependabot enabled on GitHub

- [ ] **HTTPS Enforcement**
  - [ ] Force HTTPS redirects
  - [ ] HSTS header configured
  - [ ] HSTS preload submitted
  - [ ] Mixed content eliminated

- [ ] **Logging & Auditing**
  - [ ] Security events logged
  - [ ] Failed auth attempts tracked
  - [ ] Rate limit violations logged
  - [ ] Logs shipped to secure storage

### ✅ Testing Checklist

- [ ] **Authentication Tests**
  ```bash
  # Should fail without API key
  curl -X POST https://api.threadr.app/api/generate \
    -H "Content-Type: application/json" \
    -d '{"text":"test"}'
  
  # Should succeed with valid key
  curl -X POST https://api.threadr.app/api/generate \
    -H "X-API-Key: your-api-key" \
    -H "Content-Type: application/json" \
    -d '{"text":"test"}'
  ```

- [ ] **Rate Limiting Tests**
  ```bash
  # Should block after limit
  for i in {1..25}; do
    curl -X POST https://api.threadr.app/api/generate \
      -H "X-API-Key: your-api-key" \
      -H "Content-Type: application/json" \
      -d '{"text":"test"}'
  done
  ```

- [ ] **SSRF Protection Tests**
  ```bash
  # Should be blocked
  curl -X POST https://api.threadr.app/api/generate \
    -H "X-API-Key: your-api-key" \
    -H "Content-Type: application/json" \
    -d '{"url":"http://localhost:8080"}'
  
  # Should be blocked
  curl -X POST https://api.threadr.app/api/generate \
    -H "X-API-Key: your-api-key" \
    -H "Content-Type: application/json" \
    -d '{"url":"http://192.168.1.1"}'
  ```

- [ ] **Security Headers Tests**
  ```bash
  # Check headers
  curl -I https://api.threadr.app/health
  # Verify all security headers present
  ```

- [ ] **Large Payload Tests**
  ```bash
  # Should be rejected
  curl -X POST https://api.threadr.app/api/generate \
    -H "X-API-Key: your-api-key" \
    -H "Content-Type: application/json" \
    -d '{"text":"'$(python -c 'print("x"*2000000)')"}'
  ```

### 🚨 Incident Response Plan

1. **If API Keys Compromised**:
   - [ ] Rotate all API keys immediately
   - [ ] Revoke compromised keys
   - [ ] Audit usage logs
   - [ ] Notify affected users

2. **If Under DDoS Attack**:
   - [ ] Enable Cloudflare "Under Attack" mode
   - [ ] Increase rate limits temporarily
   - [ ] Block attacking regions/IPs
   - [ ] Scale up Railway instances

3. **If Data Breach Suspected**:
   - [ ] Disable affected endpoints
   - [ ] Preserve logs for investigation
   - [ ] Notify security team
   - [ ] Document timeline of events

### 📊 Security Metrics to Monitor

- **API Authentication**:
  - Failed authentication attempts/hour
  - Unique API keys used/day
  - Suspicious patterns in key usage

- **Rate Limiting**:
  - Rate limit violations/hour
  - Top violating IPs
  - Legitimate users affected

- **Error Rates**:
  - 4xx errors by endpoint
  - 5xx errors indicating attacks
  - Timeout rates

- **Performance Under Load**:
  - Response times during high traffic
  - Memory usage patterns
  - CPU utilization

### 🔐 Security Contacts

- **Security Issues**: security@threadr.app
- **Cloudflare Support**: Use dashboard for Pro support
- **Railway Support**: support@railway.app
- **Vulnerability Reports**: Use GitHub Security tab

### 📝 Compliance Considerations

- [ ] **Privacy Policy** includes:
  - Data collection practices
  - Third-party services (OpenAI)
  - Data retention policies
  - User rights

- [ ] **Terms of Service** includes:
  - Acceptable use policy
  - Rate limiting disclosure
  - Service limitations
  - Liability limitations

- [ ] **Security Page** (/security) includes:
  - Security measures overview
  - Responsible disclosure process
  - Security contact information
  - Update notifications

### 🚀 Post-Launch Security Tasks

**Week 1**:
- [ ] Security scan with OWASP ZAP
- [ ] Penetration testing (basic)
- [ ] Review first week's logs
- [ ] Adjust rate limits based on usage

**Month 1**:
- [ ] Professional security audit
- [ ] Load testing with security scenarios
- [ ] Implement Web Application Firewall
- [ ] Set up bug bounty program

**Ongoing**:
- [ ] Weekly dependency updates
- [ ] Monthly security reviews
- [ ] Quarterly penetration tests
- [ ] Annual security audit

## Final Launch Approval

**DO NOT LAUNCH until all CRITICAL items are checked!**

Approved by: _________________ Date: _________________

Security Review by: _________________ Date: _________________