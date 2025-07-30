# 🔑 Your Generated API Keys

## Secure API Keys (Generated: 2025-07-30)

**API Key 1**: `zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8`
**API Key 2**: `FFAvIrarUm32RGDntib20DzSU21-B_zJ4w8mzaSz1So`

## 🚀 Railway Configuration

Copy this exact line to Railway Variables:
```
API_KEYS=zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8,FFAvIrarUm32RGDntib20DzSU21-B_zJ4w8mzaSz1So
```

## 🧪 Testing Your API

### Valid Request (should work):
```bash
curl -X POST https://your-railway-url.up.railway.app/api/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8" \
  -d '{"text": "Test article content for thread generation"}'
```

### Invalid Request (should return 401):
```bash
curl -X POST https://your-railway-url.up.railway.app/api/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "This should fail without API key"}'
```

## 📱 Frontend Integration

Add this header to all your frontend API calls:
```javascript
const response = await fetch('https://your-railway-url.up.railway.app/api/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8'  // Use either key
  },
  body: JSON.stringify({
    url: 'https://example.com/article'
  })
});
```

## 🔒 Security Notes

- **Keep these keys secret** - don't commit to public repositories
- **Use different keys** for different environments/clients if needed
- **Rotate keys** periodically for maximum security
- **Key 1** for your frontend, **Key 2** for testing/backup

## 📋 Complete Railway Variables Checklist

- [ ] `API_KEYS=zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8,FFAvIrarUm32RGDntib20DzSU21-B_zJ4w8mzaSz1So`
- [ ] `OPENAI_API_KEY=sk-your-actual-openai-key`
- [ ] `CORS_ORIGINS=https://your-actual-frontend-domain.vercel.app`
- [ ] `REDIS_URL=your-redis-connection-url`
- [ ] `ENVIRONMENT=production`

---
*Generated on 2025-07-30 using cryptographically secure random tokens*