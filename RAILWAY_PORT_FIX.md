# Railway Port Mismatch Fix

## Problem Identified
- Railway PORT env var: 8080 (internal)
- Railway Public Networking: Port 8000 (external)
- Result: 502 error - traffic can't route properly

## Railway Port Mapping Rules

Railway uses this port mapping system:
1. **Public Networking Port** = External port (what users access)
2. **PORT Environment Variable** = Internal port (what your app binds to)
3. **THESE MUST MATCH** for traffic to route correctly

## SOLUTION: Update Railway Dashboard

### Step 1: Fix Railway Service Port
1. Open Railway Dashboard → Your Project
2. Click on your service
3. Go to **Settings** → **Networking**  
4. In **"Public Networking"** section:
   - Change port from **8000** to **8080**
   - Save changes

### Step 2: Alternative - Force PORT to 8000

If you prefer to keep external port as 8000, force Railway to use PORT=8000:

Add to nixpacks.toml [variables] section:
```toml
PORT = "8000"
```

**BUT**: This overrides Railway's automatic port assignment, which may cause issues.

### Step 3: Verify Fix

After making the change, redeploy and check:
```bash
curl https://threadr-production.up.railway.app/health
```

Should return 200 OK with health data.

## Railway Best Practices

1. **Let Railway set PORT automatically** (recommended)
2. **Match Public Networking port to Railway's PORT env var**
3. **Don't hardcode ports in nixpacks.toml**
4. **Use `--port $PORT` in start command** (already correct)

## Current Configuration Status

✅ nixpacks.toml correctly uses `--port $PORT`
✅ App correctly reads PORT from environment  
❌ Railway Public Networking port mismatch (8000 vs 8080)

## Next Steps

1. Update Railway Dashboard port to 8080
2. Redeploy (Railway should automatically trigger)
3. Test endpoint accessibility
4. Verify logs show consistent port usage