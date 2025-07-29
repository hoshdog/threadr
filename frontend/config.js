// Configuration for Threadr frontend
const config = {
    // API URL configuration - auto-detects environment
    API_URL: (() => {
        // Check if we're in development
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:8000';
        }
        
        // Production environment - auto-detect from environment or use default
        // This can be overridden by setting VITE_API_URL in Vercel environment variables
        const envApiUrl = window.THREADR_API_URL || process?.env?.VITE_API_URL;
        if (envApiUrl) {
            return envApiUrl;
        }
        
        // Default production API URL
        // Update this to match your Railway deployment URL
        return 'https://threadr-backend-production.up.railway.app';
    })(),
    
    // Rate limiting configuration (should match backend)
    RATE_LIMIT: {
        requests: 10,
        windowHours: 1
    },
    
    // UI Configuration
    MAX_TWEET_LENGTH: 280,
    MAX_TEXT_INPUT_LENGTH: 10000,
    
    // Feature flags
    FEATURES: {
        EMAIL_CAPTURE: true,
        ANALYTICS: window.location.hostname !== 'localhost'
    }
};

// Freeze config to prevent modifications
Object.freeze(config);

// Log configuration in development
if (window.location.hostname === 'localhost') {
    console.log('Threadr Config:', config);
}