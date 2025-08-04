const fs = require('fs');
const path = require('path');

// Build script for Threadr frontend
// SECURITY FIX: No sensitive data injection for enhanced security

console.log('Building Threadr frontend (secure mode - no API key injection)...');

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

// Copy all files (no processing needed - no sensitive data to inject)
copyDirectory(sourceDir, distDir);

console.log('✅ Build completed successfully (secure mode)');
console.log(`📁 Output directory: ${distDir}`);
console.log('🔐 Security: No API keys or sensitive data in frontend');