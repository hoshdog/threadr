// Configuration for Threadr frontend
const config = {
    // Environment detection
    ENV: (() => {
        const hostname = window.location.hostname;
        if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.')) {
            return 'development';
        } else if (hostname.includes('vercel.app') || hostname.includes('--')) {
            return 'preview';
        } else {
            return 'production';
        }
    })(),

    // API URL configuration - auto-detects environment
    API_URL: (() => {
        const hostname = window.location.hostname;
        
        // Check if we're in development
        if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.')) {
            return 'http://localhost:8000';
        }
        
        // Check for explicit environment variable override
        // This supports both Vercel environment variables and manual overrides
        const envApiUrl = window.THREADR_API_URL || 
                         (typeof process !== 'undefined' ? process.env?.VITE_API_URL : null) ||
                         (typeof process !== 'undefined' ? process.env?.REACT_APP_API_URL : null);
        
        if (envApiUrl) {
            return envApiUrl;
        }
        
        // Default production API URL - Railway deployment
        return 'https://threadr-production.up.railway.app';
    })(),
    
    // Rate limiting configuration (should match backend)
    RATE_LIMIT: {
        requests: 10,
        windowHours: 1
    },
    
    // UI Configuration
    MAX_TWEET_LENGTH: 280,
    MAX_TEXT_INPUT_LENGTH: 10000,
    
    // SECURITY FIX v2.0: API keys completely removed from frontend for security
    // Backend now handles all authentication internally using IP-based rate limiting
    // No API keys are required or used in frontend requests
    // Version: 2025-08-04-SECURITY_FIX_v2
    
    // Feature flags based on environment
    FEATURES: {
        EMAIL_CAPTURE: true,
        ANALYTICS: (() => {
            const hostname = window.location.hostname;
            return !(hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.'));
        })(),
        DEBUG_MODE: (() => {
            const hostname = window.location.hostname;
            return hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.');
        })()
    }
};

// Freeze config to prevent modifications
Object.freeze(config);

// Log configuration in development
if (config.FEATURES.DEBUG_MODE) {
    console.log('Threadr Config:', config);
    console.log('Environment:', config.ENV);
    console.log('API URL:', config.API_URL);
    console.log('Security Model: IP-based rate limiting (no API keys)');
}

// Also log in production for debugging (temporary)
if (!config.FEATURES.DEBUG_MODE && window.location.hostname.includes('vercel')) {
    console.log('Production Debug - Hostname:', window.location.hostname);
    console.log('Production Debug - Security: Backend IP-based authentication');
}