# Frontend API Key Header Fix

## Problem Identified
The frontend was not sending the `X-API-Key` header to the backend, resulting in 401 Unauthorized errors. The issue was in the conditional logic that checked `if (config.API_KEY)` which could evaluate to false on certain Vercel deployments.

## Root Causes
1. **Hostname Detection**: The config.js file was checking for specific hostname patterns that might not match all Vercel deployment URLs
2. **Conditional Logic**: The `if (config.API_KEY)` check could fail if config.API_KEY returned null/undefined
3. **No Fallback**: There was no fallback mechanism to ensure the API key was always sent in production

## Fixes Applied

### 1. Updated index.html (2 locations)
- Added debug logging to help diagnose the issue
- Changed from relying on config.API_KEY to direct hostname detection
- Added fallback to hardcoded API key if config.API_KEY is null
- Improved error handling for 401 errors

### 2. Updated config.js
- Simplified API_KEY logic to return the key for ALL non-localhost environments
- Added production debug logging for Vercel deployments
- Removed complex hostname pattern matching that could fail

## Key Changes

### Before (index.html):
```javascript
if (config.API_KEY) {
    headers['X-API-Key'] = config.API_KEY;
}
```

### After (index.html):
```javascript
const hostname = window.location.hostname;
const isDevelopment = hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.');

if (!isDevelopment) {
    headers['X-API-Key'] = config.API_KEY || 'your-api-key-here';
    console.log('API Key header added:', headers['X-API-Key']);
}
```

### Before (config.js):
```javascript
if (hostname.includes('vercel.app') || hostname.includes('threadr.app')) {
    return 'your-api-key-here';
}
```

### After (config.js):
```javascript
// Production API key for ALL non-localhost deployments
return 'your-api-key-here';
```

## Testing Instructions
1. Deploy to Vercel
2. Open browser console
3. Try to generate a thread
4. Check console for:
   - "API Key header added: your-api-key-here"
   - No 401 errors
5. Verify thread generation works

## Debug Output
The updated code will log:
- Environment detection
- API URL being used
- Whether API key is present
- Current hostname
- When API key header is added

## Rollback Plan
If issues persist:
1. Check Railway backend logs for incoming headers
2. Use browser network tab to inspect request headers
3. Temporarily hardcode the API key directly in the fetch call
4. Verify the API key matches what's configured in Railway