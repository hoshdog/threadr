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
    
    // API Authentication
    API_KEY: (() => {
        const hostname = window.location.hostname;
        
        // No API key needed in development
        if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname.startsWith('192.168.')) {
            return null;
        }
        
        // Production API key for ALL non-localhost deployments
        // This includes Vercel preview deployments, production, and any custom domains
        return 'zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8';
    })(),
    
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
    console.log('API Key:', config.API_KEY ? '[HIDDEN]' : 'null');
}

// Also log in production for debugging (temporary)
if (!config.FEATURES.DEBUG_MODE && window.location.hostname.includes('vercel')) {
    console.log('Production Debug - Hostname:', window.location.hostname);
    console.log('Production Debug - API Key configured:', !!config.API_KEY);
}