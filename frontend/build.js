const fs = require('fs');
const path = require('path');

// Build script for Threadr frontend
// This script injects environment variables during build time for security

console.log('Building Threadr frontend...');

// Source and destination directories
const sourceDir = path.join(__dirname, 'public');
const distDir = path.join(__dirname, 'dist');

// Create dist directory if it doesn't exist
if (!fs.existsSync(distDir)) {
    fs.mkdirSync(distDir, { recursive: true });
}

// Copy all files from public to dist
function copyDirectory(src, dest) {
    const entries = fs.readdirSync(src, { withFileTypes: true });
    
    if (!fs.existsSync(dest)) {
        fs.mkdirSync(dest, { recursive: true });
    }
    
    for (const entry of entries) {
        const srcPath = path.join(src, entry.name);
        const destPath = path.join(dest, entry.name);
        
        if (entry.isDirectory()) {
            copyDirectory(srcPath, destPath);
        } else {
            fs.copyFileSync(srcPath, destPath);
        }
    }
}

// Copy all files
copyDirectory(sourceDir, distDir);

// Process index.html to inject environment variables
const indexPath = path.join(distDir, 'index.html');
let indexContent = fs.readFileSync(indexPath, 'utf8');

// Get environment variable
const apiKey = process.env.THREADR_API_KEY || '';

console.log('🔍 Environment variables:', {
    NODE_ENV: process.env.NODE_ENV,
    THREADR_API_KEY: apiKey ? '[REDACTED]' : 'not set',
    allEnvKeys: Object.keys(process.env).filter(key => key.includes('THREADR')).join(', ') || 'none'
});

// Inject the actual API key or empty string
if (apiKey) {
    console.log('✅ Injecting API key from environment variable');
    indexContent = indexContent.replace(
        "window.THREADR_API_KEY = 'VERCEL_INJECT_API_KEY';",
        `window.THREADR_API_KEY = '${apiKey}';`
    );
} else {
    console.log('⚠️  No THREADR_API_KEY environment variable found - will use fallback');
    indexContent = indexContent.replace(
        "window.THREADR_API_KEY = 'VERCEL_INJECT_API_KEY';",
        "// No THREADR_API_KEY environment variable configured"
    );
}

// Write the modified index.html
fs.writeFileSync(indexPath, indexContent);

console.log('✅ Build completed successfully');
console.log(`📁 Output directory: ${distDir}`);
console.log(`🔐 API Key configured: ${!!apiKey}`);