# 🚨 VERCEL ENVIRONMENT VARIABLE NAME FIX

## The Problem You Encountered

When you tried to add `threadr-api-key`, Vercel showed:
> "The name contains invalid characters. Only letters, digits, and underscores are allowed."

## The Solution

### ❌ DON'T USE THIS:
```
threadr-api-key
```
*(Contains hyphen - not allowed)*

### ✅ USE THIS INSTEAD:
```
THREADR_API_KEY
```
*(Underscores are allowed)*

## Visual Guide - Exactly What to Type

In the Vercel Environment Variables form:

```
┌─────────────────────────────────────────────┐
│ Add Environment Variable                     │
├─────────────────────────────────────────────┤
│                                             │
│ Name:                                       │
│ ┌─────────────────────────────────────────┐ │
│ │ THREADR_API_KEY                         │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ Value:                                      │
│ ┌─────────────────────────────────────────┐ │
│ │ zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8 │
│ └─────────────────────────────────────────┘ │
│                                             │
│ Environment:                                │
│ ☑ Production                                │
│ ☑ Preview                                   │
│ ☑ Development                               │
│                                             │
│ ☑ Sensitive - This value will be encrypted │
│                                             │
│ [Save]                                      │
└─────────────────────────────────────────────┘
```

## Copy-Paste Values

**Variable Name** (copy this exactly):
```
THREADR_API_KEY
```

**Variable Value** (copy this exactly):
```
zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8
```

## Why This Matters

- **Security**: This moves your API key out of source code
- **No More Exposure**: API key won't be visible to users
- **Easy Rotation**: Change keys without code changes
- **Best Practice**: Environment variables for secrets

## After Adding the Variable

1. Click **Save**
2. Vercel will show: "Updated environment variables"
3. Click **Redeploy** to apply changes
4. Wait 2-3 minutes for deployment

## Verification

After deployment:
1. Visit https://threadr-plum.vercel.app
2. Open DevTools (F12) → Console
3. Should NOT see: "Using fallback API key"
4. Check Sources → config.js → API key should be hidden

## Common Mistakes to Avoid

| Wrong | Right | Why |
|-------|-------|-----|
| `threadr-api-key` | `THREADR_API_KEY` | No hyphens allowed |
| `threadr_api_key` | `THREADR_API_KEY` | Use uppercase by convention |
| `"THREADR_API_KEY"` | `THREADR_API_KEY` | No quotes in name field |
| Space before/after | No spaces | Trim whitespace |

## Still Having Issues?

1. **Double-check spelling**: Must be exactly `THREADR_API_KEY`
2. **No extra spaces**: Check for accidental spaces
3. **All environments selected**: Production, Preview, and Development
4. **Deployment completed**: Wait for full deployment
5. **Clear browser cache**: Ctrl+Shift+R after deployment

---

**Remember**: The fix is simple - just use `THREADR_API_KEY` with underscores instead of `threadr-api-key` with hyphens!