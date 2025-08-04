# Threadr Automated Verification & Monitoring Tools

This directory contains comprehensive automated verification and monitoring tools for your Threadr deployment, specifically designed to verify your Week 1 premium improvements.

## 🚀 Quick Start

### Run Complete Verification Suite (Recommended)

**Windows (Command Prompt):**
```bash
run_verification_suite.bat
```

**Windows (PowerShell):**
```powershell
.\run_verification_suite.ps1
```

This will run all three verification tools in sequence and generate comprehensive reports.

## 🔧 Individual Tools

### 1. Production Verification Script
**File:** `scripts/verification/production_verification.py`

**Purpose:** Tests all deployed features including API security, Redis configuration, UX improvements, and core functionality.

**Usage:**
```bash
# Basic run
python scripts/verification/production_verification.py

# Verbose output with JSON report
python scripts/verification/production_verification.py --verbose --json-output verification_results.json

# Custom URLs
python scripts/verification/production_verification.py --frontend-url https://your-app.vercel.app --backend-url https://your-api.railway.app
```

**Tests Performed:**
- ✅ Backend health and readiness
- ✅ Frontend accessibility and configuration
- ✅ API key security implementation
- ✅ Redis connection and performance
- ✅ Rate limiting functionality
- ✅ Premium status endpoints
- ✅ Stripe webhook security
- ✅ Email capture system

### 2. API Security Monitor
**File:** `scripts/monitoring/api_security_monitor.py`

**Purpose:** Monitors API key security implementation and detects security vulnerabilities.

**Usage:**
```bash
# Single security scan
python scripts/monitoring/api_security_monitor.py --verbose

# Continuous monitoring (5-minute intervals)
python scripts/monitoring/api_security_monitor.py --continuous --interval 300

# With Slack alerts
python scripts/monitoring/api_security_monitor.py --alerts-webhook https://hooks.slack.com/your/webhook/url

# Generate security report
python scripts/monitoring/api_security_monitor.py --json-output security_report.json
```

**Security Checks:**
- 🔐 API key environment variable configuration
- 🛡️ Authentication mechanism testing
- 📋 Security headers analysis
- ⏱️ Rate limiting effectiveness
- 🔴 Redis security configuration
- 🚨 Vulnerability detection

### 3. Redis Performance Tester
**File:** `scripts/performance/redis_performance_test.py`

**Purpose:** Comprehensive Redis performance testing for Railway/Upstash configuration.

**Usage:**
```bash
# Standard performance test
python scripts/performance/redis_performance_test.py

# Full test suite with custom parameters
python scripts/performance/redis_performance_test.py --test-suite full --duration 60 --workers 10

# Generate performance report
python scripts/performance/redis_performance_test.py --json-output redis_performance.json
```

**Performance Tests:**
- 🔗 Basic connectivity and latency
- 📊 Usage stats performance (reads/writes)
- 💎 Premium status caching effectiveness
- 📧 Email capture storage performance
- ⏱️ Rate limiting performance under load
- 🔀 Concurrent load testing
- 🧠 Memory pressure testing

## 📊 Monitoring Dashboard

**File:** `monitoring_dashboard.html`

**Purpose:** Real-time monitoring dashboard for deployment status and performance metrics.

**Usage:**
1. Start a local server:
   ```bash
   python -m http.server 8080
   ```
2. Open: http://localhost:8080/monitoring_dashboard.html

**Dashboard Features:**
- 📈 Real-time status indicators
- 🌐 Service health monitoring
- 📊 Performance charts (response times, success rates)
- 🧪 Recent test results
- 🚨 Security alerts
- ⚡ Quick action buttons
- 💾 Export reports functionality

## 📁 Output Files

All verification tools generate detailed JSON reports in the `verification_reports/` directory:

- `production_verification_YYYYMMDD_HHMMSS.json` - Complete system verification
- `security_report_YYYYMMDD_HHMMSS.json` - Security analysis and vulnerabilities
- `performance_report_YYYYMMDD_HHMMSS.json` - Performance benchmarks and metrics

## 🎯 Success Criteria

### Production Verification
- ✅ All critical services healthy
- ✅ API endpoints responding correctly
- ✅ Rate limiting active and working
- ✅ Frontend configuration proper
- ✅ Overall success rate > 90%

### Security Monitoring
- 🔒 No CRITICAL security issues
- 🟡 Maximum 2-3 MEDIUM issues acceptable
- 📊 Risk score < 25%
- 🛡️ Security status: EXCELLENT or GOOD

### Performance Testing
- ⚡ Average latency < 200ms
- 🚀 Throughput > 20 ops/sec
- ✅ Success rate > 95%
- 🏆 Performance grade: B or better

## 🚨 Troubleshooting

### Common Issues

**1. "Python not found"**
- Install Python 3.7+ from python.org
- Add Python to your system PATH
- Restart command prompt/PowerShell

**2. "Module not found" errors**
- Install required modules: `pip install aiohttp asyncio`
- Ensure you're in the correct directory

**3. "Connection refused" errors**
- Verify your frontend/backend URLs are correct
- Check that services are actually deployed and running
- Test URLs manually in browser first

**4. "Permission denied" on PowerShell**
- Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Or use Command Prompt instead

### Getting Help

1. **Check the logs**: All tools provide verbose output with `--verbose` flag
2. **Review JSON reports**: Detailed error information in the reports
3. **Manual testing**: Try accessing URLs directly in browser
4. **Environment variables**: Verify all required env vars are set in Vercel/Railway

## 🔄 Automation & CI/CD

### Daily Monitoring (Recommended)
Set up automated daily verification:

```bash
# Create a scheduled task (Windows) or cron job (Linux/Mac)
python scripts/verification/production_verification.py --json-output daily_check.json
```

### Continuous Security Monitoring
For production environments:

```bash
# Run continuous security monitoring
python scripts/monitoring/api_security_monitor.py --continuous --interval 1800 --alerts-webhook YOUR_WEBHOOK_URL
```

### Integration with GitHub Actions
Add to your CI/CD pipeline:

```yaml
- name: Verify Deployment
  run: |
    python scripts/verification/production_verification.py --json-output verification.json
    python scripts/monitoring/api_security_monitor.py --json-output security.json
```

## 📚 Additional Resources

- **DEPLOYMENT_VERIFICATION_GUIDE.md** - Step-by-step manual verification
- **CLAUDE.md** - Project context and configuration details
- **Backend documentation** - `backend/README.md`
- **Frontend documentation** - `frontend/README.md`

---

These tools provide comprehensive automated verification of your Threadr deployment, ensuring your Week 1 premium improvements are properly configured, secure, and performing well in production.