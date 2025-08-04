# Operations Documentation

> **🔧 OPERATIONS GUIDE**: Scripts, automation, and operational procedures for Threadr

## Operations Overview

This directory contains all operational tools, scripts, and procedures needed to maintain, monitor, and scale the Threadr platform. Operations are organized into deployment automation, monitoring systems, and testing procedures.

### Operations Structure
```
OPERATIONS/
├── deployment/          # Deployment automation scripts
│   ├── auto-deploy.py   # Automated deployment orchestration
│   ├── rollback.py      # Emergency rollback procedures
│   └── health-check.py  # Post-deployment verification
├── monitoring/          # System monitoring and alerting
│   ├── health-monitor.py # Continuous health monitoring
│   ├── cost-tracker.py  # API cost monitoring and alerts
│   └── performance.py   # Performance metrics collection
├── testing/             # Test automation and validation
│   ├── production-test.py # Production environment testing
│   ├── load-test.py     # Performance and load testing
│   └── security-scan.py # Security vulnerability scanning
└── README.md           # This file
```

## Deployment Operations

### Automated Deployment
The deployment system handles both frontend (Vercel) and backend (Railway) deployments with proper coordination and rollback capabilities.

#### Current Deployment Flow
```
Code Commit → GitHub → Webhook → Auto Deploy → Health Check → Success/Rollback
     ↓            ↓        ↓          ↓           ↓              ↓
   Git Push   → Trigger → Vercel → Railway → Monitoring → Notification
```

#### Deployment Scripts
```bash
# Main deployment script
python OPERATIONS/deployment/auto-deploy.py

# Emergency rollback
python OPERATIONS/deployment/rollback.py --environment production

# Health verification
python OPERATIONS/deployment/health-check.py --full-suite
```

### Deployment Automation Features
- **Coordinated Deployment**: Frontend and backend deploy in correct order
- **Health Verification**: Automatic post-deployment testing
- **Rollback Capability**: Automatic rollback on failure detection
- **Notification System**: Slack/email alerts for deployment status
- **Environment Management**: Support for staging and production

### Manual Deployment Procedures

#### Emergency Deployment (Critical Fixes)
```bash
# 1. Hotfix preparation
git checkout main
git pull origin main
git checkout -b hotfix/critical-security-fix

# 2. Apply fix and test
# Make necessary changes
pytest backend/tests/
npm test  # (for Next.js when ready)

# 3. Deploy immediately
git add .
git commit -m "HOTFIX: Critical security vulnerability"
git push origin hotfix/critical-security-fix

# 4. Merge and deploy
git checkout main
git merge hotfix/critical-security-fix
git push origin main
# Auto-deployment triggers

# 5. Verify deployment
python OPERATIONS/deployment/health-check.py --critical
```

#### Scheduled Deployment (Regular Updates)
```bash
# 1. Pre-deployment checks
python OPERATIONS/testing/production-test.py
python OPERATIONS/monitoring/health-monitor.py --baseline

# 2. Deploy with verification
python OPERATIONS/deployment/auto-deploy.py --environment production --verify

# 3. Post-deployment monitoring
python OPERATIONS/monitoring/performance.py --watch 300  # 5 minutes
```

## Monitoring Operations

### Health Monitoring System
Continuous monitoring of all system components with automatic alerting and recovery procedures.

#### Monitoring Components
- **Application Health**: API endpoints, response times, error rates
- **Infrastructure Health**: Server resources, database connections
- **Business Metrics**: User activity, revenue metrics, conversion rates
- **Security Monitoring**: Failed auth attempts, suspicious activity
- **Cost Monitoring**: API usage costs, infrastructure spending

#### Monitoring Scripts
```bash
# Continuous health monitoring
python OPERATIONS/monitoring/health-monitor.py --daemon

# Cost tracking and alerts
python OPERATIONS/monitoring/cost-tracker.py --alert-threshold 100

# Performance metrics collection
python OPERATIONS/monitoring/performance.py --collect-metrics
```

### Alert Management
```python
# Alert configuration example
ALERT_RULES = {
    'api_response_time': {
        'threshold': 2000,  # 2 seconds
        'severity': 'warning',
        'action': 'scale_backend'
    },
    'error_rate': {
        'threshold': 0.05,  # 5%
        'severity': 'critical',
        'action': 'rollback_deploy'
    },
    'cost_spike': {
        'threshold': 200,  # $200/day
        'severity': 'critical',
        'action': 'rate_limit_tightening'
    }
}
```

### Monitoring Dashboards
- **Business Dashboard**: Revenue, users, conversion rates
- **Technical Dashboard**: Performance, errors, uptime
- **Security Dashboard**: Authentication, rate limiting, threats
- **Cost Dashboard**: API costs, infrastructure spending

## Testing Operations

### Production Testing Suite
Comprehensive testing of the live production environment to ensure everything works correctly.

#### Test Categories
1. **Smoke Tests**: Basic functionality verification
2. **Integration Tests**: End-to-end user workflows
3. **Performance Tests**: Load and stress testing
4. **Security Tests**: Vulnerability scanning
5. **Business Logic Tests**: Revenue and user management

#### Testing Scripts
```bash
# Full production test suite
python OPERATIONS/testing/production-test.py --full

# Load testing
python OPERATIONS/testing/load-test.py --users 100 --duration 300

# Security scanning
python OPERATIONS/testing/security-scan.py --comprehensive
```

### Test Automation Schedule
- **Hourly**: Basic health checks and smoke tests
- **Daily**: Full integration test suite
- **Weekly**: Performance and load testing
- **Monthly**: Comprehensive security scanning

## Backup and Recovery Operations

### Backup Strategy
```
Data Type          Frequency    Retention    Method
-------------------------------------------------
Code Repository    Real-time    Indefinite   Git (GitHub)
Database (Redis)   Daily        30 days      Upstash Auto
Environment Config Weekly       90 days      Encrypted Store
User Data          Daily        1 year       PostgreSQL Backup
```

### Recovery Procedures

#### Data Recovery
```bash
# Restore from Redis backup
python OPERATIONS/recovery/restore-redis.py --date 2025-08-01

# Restore user data (when PostgreSQL implemented)
python OPERATIONS/recovery/restore-database.py --backup-id latest

# Restore application configuration
python OPERATIONS/recovery/restore-config.py --environment production
```

#### Disaster Recovery Plan
1. **Assessment**: Determine scope of failure
2. **Communication**: Notify stakeholders and users
3. **Recovery**: Execute appropriate recovery procedures
4. **Verification**: Confirm systems are restored
5. **Post-mortem**: Document incident and improvements

## Security Operations

### Security Monitoring
- **Authentication Failures**: Track failed login attempts
- **API Abuse**: Monitor for unusual usage patterns
- **Security Headers**: Verify security headers are present
- **Vulnerability Scanning**: Regular security assessments

### Security Incident Response

#### Incident Classification
- **P0 (Critical)**: Active security breach, data exposure
- **P1 (High)**: Potential vulnerability with high impact
- **P2 (Medium)**: Security weakness requiring attention
- **P3 (Low)**: Minor security improvement needed

#### Response Procedures
```bash
# Security incident response
python OPERATIONS/security/incident-response.py --severity P0

# Emergency security lockdown
python OPERATIONS/security/lockdown.py --mode emergency

# Security audit
python OPERATIONS/security/audit.py --comprehensive
```

## Cost Management Operations

### Cost Monitoring
Track and optimize costs across all services to maintain profitability.

#### Cost Components
- **OpenAI API**: Thread generation costs
- **Railway**: Backend hosting and scaling
- **Vercel**: Frontend hosting (currently free)
- **Upstash**: Redis database costs
- **Stripe**: Payment processing fees

#### Cost Optimization Scripts
```bash
# Daily cost analysis
python OPERATIONS/cost/analyze-costs.py --date today

# Cost projection
python OPERATIONS/cost/project-costs.py --period monthly

# Cost optimization recommendations
python OPERATIONS/cost/optimize.py --suggestions
```

### Cost Alerts and Controls
```python
# Cost control configuration
COST_CONTROLS = {
    'openai': {
        'daily_limit': 50,     # $50/day
        'monthly_limit': 1000, # $1000/month
        'action': 'rate_limit'
    },
    'railway': {
        'daily_limit': 10,     # $10/day
        'monthly_limit': 200,  # $200/month
        'action': 'scale_down'
    }
}
```

## Performance Operations

### Performance Monitoring
- **Response Times**: API endpoint performance
- **Throughput**: Requests per second capacity
- **Resource Usage**: CPU, memory, database performance
- **User Experience**: Frontend loading times, Core Web Vitals

### Performance Optimization
```bash
# Performance baseline
python OPERATIONS/performance/baseline.py --collect

# Performance analysis
python OPERATIONS/performance/analyze.py --period 24h

# Optimization recommendations
python OPERATIONS/performance/optimize.py --auto-apply
```

## Operational Procedures

### Daily Operations Checklist
- [ ] Check system health dashboard
- [ ] Review error rates and logs
- [ ] Monitor API cost spending
- [ ] Verify backup completion
- [ ] Check security alerts

### Weekly Operations Checklist
- [ ] Run comprehensive test suite
- [ ] Review performance metrics
- [ ] Update dependencies
- [ ] Security vulnerability scan
- [ ] Cost optimization review

### Monthly Operations Checklist
- [ ] Disaster recovery test
- [ ] Security audit
- [ ] Performance benchmarking
- [ ] Capacity planning review
- [ ] Documentation updates

## Automation and Workflows

### GitHub Actions Integration
```yaml
# .github/workflows/operations.yml
name: Operations Automation
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run health check
        run: python OPERATIONS/monitoring/health-monitor.py
  
  cost-monitoring:
    runs-on: ubuntu-latest
    steps:
      - name: Monitor costs
        run: python OPERATIONS/monitoring/cost-tracker.py
```

### Slack Integration
```python
# Slack notification system
class SlackNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def send_alert(self, severity, message, details=None):
        payload = {
            "text": f"🚨 {severity.upper()}: {message}",
            "attachments": [{
                "color": self.get_color(severity),
                "fields": [
                    {"title": "Details", "value": details, "short": False}
                ]
            }]
        }
        requests.post(self.webhook_url, json=payload)
```

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: High API Response Times
```bash
# Diagnosis
python OPERATIONS/monitoring/performance.py --analyze-bottlenecks

# Solutions
1. Check database connection pool
2. Verify Redis cache performance
3. Monitor OpenAI API latency
4. Scale backend if needed
```

#### Issue: Increased Error Rates
```bash
# Diagnosis
python OPERATIONS/monitoring/health-monitor.py --error-analysis

# Solutions
1. Check recent deployments
2. Review error logs
3. Verify external service status
4. Consider rollback if critical
```

#### Issue: Cost Spike Alerts
```bash
# Diagnosis
python OPERATIONS/cost/analyze-costs.py --spike-analysis

# Solutions
1. Check for API abuse
2. Tighten rate limiting
3. Optimize OpenAI usage
4. Review user behavior patterns
```

## Emergency Procedures

### System Down Emergency
1. **Immediate**: Check status pages (Railway, Vercel, Upstash)
2. **Assess**: Determine scope of outage
3. **Communicate**: Update status page and notify users
4. **Recover**: Execute recovery procedures
5. **Monitor**: Verify recovery and stability

### Security Breach Emergency
1. **Isolate**: Immediately secure compromised systems
2. **Assess**: Determine scope of breach
3. **Notify**: Alert relevant stakeholders
4. **Recover**: Restore systems securely
5. **Document**: Complete post-incident analysis

### Cost Emergency (API Abuse)
1. **Immediate**: Implement emergency rate limiting
2. **Identify**: Find source of unusual usage
3. **Block**: Block abusive users/IPs
4. **Monitor**: Watch for continued abuse
5. **Optimize**: Implement permanent protections

---

**🔧 Complete operational framework supporting 99.9% uptime and cost-effective scaling**

*Comprehensive operations ensuring reliable, secure, and cost-effective service delivery*