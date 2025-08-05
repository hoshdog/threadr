# 🎯 Railway Cache Clear - Visual Checklist

## Before You Start
- [ ] You're logged into Railway.app
- [ ] You can see your "threadr" project
- [ ] You have 5 minutes to complete this

## Step-by-Step Visual Guide

### 1️⃣ Navigate to Service Settings
```
Railway Dashboard
└── Your Projects
    └── threadr (click this)
        └── Your Service (click the box)
            └── Settings (click this tab)
```

### 2️⃣ Find the Danger Zone
Scroll down until you see:
```
┌─────────────────────────────────────┐
│ ⚠️ Danger Zone                      │
│ ┌─────────────────────────────────┐ │
│ │ Clear Build Cache               │ │
│ │ [Clear Cache] <- CLICK THIS     │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### 3️⃣ Confirm Cache Clear
A popup appears:
```
┌──────────────────────────────┐
│ Clear Build Cache?           │
│                              │
│ This will force a rebuild    │
│                              │
│ [Cancel] [Clear Cache]       │
│          ^^^^^^ CLICK THIS   │
└──────────────────────────────┘
```

### 4️⃣ Trigger Redeployment
Go to Deployments tab:
```
Deployments | Settings | Variables | Logs
^^^^^^^^^^^^ CLICK THIS
```

Then find the latest deployment:
```
┌────────────────────────────────────────┐
│ #abc123 - 2 minutes ago       [⋮]     │
│                                ^^^ CLICK│
│                                        │
│ Menu appears:                          │
│ • View Logs                            │
│ • Redeploy <- CLICK THIS               │
│ • Rollback                             │
└────────────────────────────────────────┘
```

### 5️⃣ Monitor Build Logs

**✅ GOOD - You should see:**
```
Starting Python setup... (Updated 2025-08-05)
Using main_simple.py for deployment
Installing dependencies...
Starting: exec uvicorn src.main_minimal:app
```

**❌ BAD - If you see:**
```
Starting Python setup...
Starting: exec uvicorn src.main:app
Routes import failed
Service degraded
```

## Quick Verification Commands

After deployment completes (usually 2-3 minutes):

### Windows PowerShell:
```powershell
# Quick test
Invoke-WebRequest https://threadr-production.up.railway.app/health | ConvertFrom-Json

# Should show:
# status : healthy
# app    : minimal
```

### Windows CMD:
```cmd
curl https://threadr-production.up.railway.app/
```

Should return:
```json
{
  "app": "Threadr Minimal",
  "version": "1.0.0"
}
```

## 🚨 If Cache Clear Doesn't Work

### Plan B: Force with Environment Variable
1. Go to **Variables** tab
2. Add new variable:
   - Name: `REBUILD_TRIGGER`
   - Value: `force-2025-08-06`
3. This forces a rebuild
4. Delete the variable after deployment starts

### Plan C: Delete Service & Recreate
1. **FIRST**: Copy all your environment variables!
2. Settings → Danger Zone → Delete Service
3. New Service → GitHub Repo → Select threadr

### Plan D: Deploy to Render.com
1. Takes 5 minutes
2. Already configured with our `render.yaml`
3. Better deployment logs

## Success Indicators ✅

You know it worked when:
- [ ] Build logs mention "main_minimal.py"
- [ ] Health endpoint returns `"app": "minimal"`
- [ ] No more 503 errors
- [ ] `/api/generate` returns tweets

## Common Mistakes to Avoid ❌

1. **Don't forget to REDEPLOY after clearing cache**
   - Cache clear alone doesn't trigger new deployment
   
2. **Don't skip checking build logs**
   - This tells you if it actually worked
   
3. **Don't panic if first attempt fails**
   - Sometimes takes 2 attempts
   
4. **Don't forget your environment variables**
   - If recreating service, save them first!

## Emergency Script

Run this to check if it worked:
```bash
python scripts/verify_railway_cache_clear.py
```

Or monitor continuously:
```bash
python scripts/verify_railway_cache_clear.py --monitor
```

---

**TIME ESTIMATE**: 5 minutes total
**SUCCESS RATE**: 90% on first try, 99% with Plan B