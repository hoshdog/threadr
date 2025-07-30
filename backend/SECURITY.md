# Threadr API Security Documentation

This document describes the security measures implemented in the Threadr API.

## Table of Contents
1. [API Authentication](#api-authentication)
2. [Security Headers](#security-headers)
3. [URL Validation & SSRF Protection](#url-validation--ssrf-protection)
4. [Rate Limiting](#rate-limiting)
5. [Environment-Specific Features](#environment-specific-features)
6. [Configuration](#configuration)

## API Authentication

### Overview
The API uses header-based authentication with API keys. Multiple API keys can be configured for different clients.

### Implementation
- **Header**: `X-API-Key`
- **Protected Endpoints**: `/api/generate`
- **Public Endpoints**: `/health`, `/readiness`, `/api/test`

### Usage Example
```bash
curl -X POST https://api.threadr.app/api/generate \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://medium.com/article"}'
```

### Error Responses
- `401 Unauthorized`: Missing or invalid API key
- Header: `WWW-Authenticate: ApiKey`

## Security Headers

The following security headers are automatically added to all responses:

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Content-Type-Options` | `nosniff` | Prevents MIME type sniffing |
| `X-Frame-Options` | `DENY` | Prevents clickjacking attacks |
| `X-XSS-Protection` | `1; mode=block` | Enables XSS filter in older browsers |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Controls referrer information |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Forces HTTPS (production only) |
| `Content-Security-Policy` | `default-src 'none'; frame-ancestors 'none';` | Restrictive CSP for API |
| `Permissions-Policy` | `geolocation=(), microphone=(), camera=()` | Disables browser features |
| `X-Permitted-Cross-Domain-Policies` | `none` | Prevents Adobe Flash/PDF embedding |

## URL Validation & SSRF Protection

### Features
1. **Scheme Validation**: Only `http` and `https` URLs allowed
2. **Domain Allowlist**: Configurable list of allowed domains
3. **Private IP Blocking**: Prevents access to internal networks
4. **Hostname Resolution**: Validates resolved IPs before fetching

### Domain Allowlist Patterns
- Exact match: `medium.com`
- Wildcard subdomain: `*.medium.com`
- Pattern matching: `blog.*.com`

### Blocked IPs
- Private ranges: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
- Loopback: 127.0.0.0/8, ::1
- Link-local: 169.254.0.0/16, fe80::/10

### Error Responses
- `400 Bad Request`: Invalid URL scheme
- `403 Forbidden`: Domain not allowed or resolves to private IP

## Rate Limiting

### Implementation
- **Primary**: Redis-based distributed rate limiting
- **Fallback**: In-memory rate limiting (single instance)
- **Tracking**: By IP address

### Configuration
- Default: 10 requests per hour per IP
- Configurable via environment variables

### Endpoints
- `GET /api/rate-limit-status`: Check current rate limit status

### Error Response
- `429 Too Many Requests`: Rate limit exceeded
- Response includes minutes until reset

## Environment-Specific Features

### Production (`ENVIRONMENT=production`)
- API key authentication enforced
- Debug endpoints disabled (`/debug/startup` returns 404)
- HSTS header enabled
- Detailed error messages hidden

### Development (`ENVIRONMENT=development`)
- API key authentication optional
- Debug endpoints accessible
- HSTS header disabled
- Detailed error messages shown

## Configuration

### Environment Variables

```bash
# API Authentication
API_KEYS=key1,key2,key3  # Comma-separated list

# URL Security
ALLOWED_DOMAINS=medium.com,*.medium.com,dev.to,*.dev.to

# Rate Limiting
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW_HOURS=1

# Environment
ENVIRONMENT=production
```

### Security Checklist for Deployment

- [ ] Set `ENVIRONMENT=production`
- [ ] Configure strong API keys in `API_KEYS`
- [ ] Review and set `ALLOWED_DOMAINS` for your use case
- [ ] Ensure Redis is configured for distributed rate limiting
- [ ] Verify CORS origins match your frontend domains
- [ ] Enable HTTPS at the load balancer/proxy level
- [ ] Monitor rate limit violations and adjust as needed
- [ ] Regularly rotate API keys
- [ ] Review logs for security violations

## Security Best Practices

1. **API Keys**: Use strong, randomly generated API keys (minimum 32 characters)
2. **HTTPS**: Always use HTTPS in production (handled by Railway/proxy)
3. **Monitoring**: Monitor for repeated 401/403/429 responses
4. **Updates**: Keep dependencies updated for security patches
5. **Secrets**: Never commit API keys or sensitive data to version control

## Incident Response

If you detect suspicious activity:

1. Check logs for patterns of abuse
2. Temporarily block IPs if necessary (at infrastructure level)
3. Rotate compromised API keys immediately
4. Review allowed domains if SSRF attempts detected
5. Increase rate limits if under attack

## Testing Security

### Development Testing
```bash
# Test without API key (should fail in production)
curl http://localhost:8001/api/generate -X POST -H "Content-Type: application/json" -d '{"text": "test"}'

# Test with API key
curl http://localhost:8001/api/generate -X POST \
  -H "X-API-Key: your-test-key" \
  -H "Content-Type: application/json" \
  -d '{"text": "test"}'

# Test SSRF protection
curl http://localhost:8001/api/generate -X POST \
  -H "X-API-Key: your-test-key" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://localhost/admin"}'

# Check security config (dev only)
curl http://localhost:8001/api/security/config
```

### Security Headers Test
```bash
curl -I https://api.threadr.app/health
```

## Contact

For security concerns or vulnerability reports, please contact the development team immediately.