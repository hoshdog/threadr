#!/usr/bin/env node

/**
 * Script to verify logo files are properly deployed
 * Run this locally or in CI to ensure logos are accessible
 */

const fs = require('fs');
const path = require('path');

const FRONTEND_DIR = path.join(__dirname, '..', 'frontend', 'src');
const LOGOS_DIR = path.join(FRONTEND_DIR, 'logos');

const requiredLogos = [
    'threadrLogo_White.png',
    'threadrLogo_Black.png',
    'threadrBanner_White.png',
    'threadrBanner_Black.png'
];

console.log('🔍 Verifying Threadr logos...\n');

// Check if logos directory exists
if (!fs.existsSync(LOGOS_DIR)) {
    console.error('❌ Error: Logos directory not found at:', LOGOS_DIR);
    process.exit(1);
}

console.log('✅ Logos directory found:', LOGOS_DIR);

// Check each required logo file
let allLogosFound = true;
requiredLogos.forEach(logo => {
    const logoPath = path.join(LOGOS_DIR, logo);
    if (fs.existsSync(logoPath)) {
        const stats = fs.statSync(logoPath);
        console.log(`✅ ${logo} - ${(stats.size / 1024).toFixed(2)} KB`);
    } else {
        console.error(`❌ ${logo} - NOT FOUND`);
        allLogosFound = false;
    }
});

// Check logo references in index.html
console.log('\n🔍 Checking logo references in index.html...\n');
const indexPath = path.join(FRONTEND_DIR, 'index.html');
const indexContent = fs.readFileSync(indexPath, 'utf8');

const logoPattern = /src=["']([^"']*logos\/[^"']+)["']/g;
let match;
const foundReferences = [];

while ((match = logoPattern.exec(indexContent)) !== null) {
    foundReferences.push(match[1]);
}

console.log(`Found ${foundReferences.length} logo references:`);
foundReferences.forEach(ref => {
    if (ref.startsWith('./logos/')) {
        console.log(`✅ ${ref} - Correct relative path`);
    } else {
        console.log(`⚠️  ${ref} - Unexpected path format`);
    }
});

// Deployment recommendations
console.log('\n📋 Deployment Checklist:');
console.log('1. Clear Vercel build cache: Project Settings > General > Build Cache > Clear Cache');
console.log('2. Redeploy: git push or trigger deployment from Vercel dashboard');
console.log('3. Test logos at: https://your-app.vercel.app/test-logos.html');
console.log('4. Check browser console for any 404 errors');
console.log('5. Verify logos load in both development and production');

if (allLogosFound) {
    console.log('\n✅ All logos verified successfully!');
} else {
    console.log('\n❌ Some logos are missing. Please check the errors above.');
    process.exit(1);
}