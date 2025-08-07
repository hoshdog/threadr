// Debug script to investigate 403 Forbidden errors
const baseUrl = 'https://threadr-pw0s.onrender.com/api';

console.log('🔍 Debugging 403 Forbidden errors...\n');

// Test URL matching logic from client.ts
const publicEndpoints = [
  '/auth/login',
  '/auth/register', 
  '/auth/forgot-password',
  '/auth/reset-password',
  '/subscriptions/plans',  // This should be public
  '/health',
  '/readiness'
];

function isPublicEndpoint(url) {
  // Mimic the logic from client.ts line 124-127
  return publicEndpoints.some(endpoint => {
    // Handle exact match or endpoint at end of URL
    const exactMatch = url === endpoint;
    const endsWith = url?.endsWith(endpoint);
    console.log(`  Checking: ${url} vs ${endpoint} - exact: ${exactMatch}, endsWith: ${endsWith}`);
    return exactMatch || endsWith;
  });
}

// Test cases that should be public
const testCases = [
  '/subscriptions/plans',
  '/api/subscriptions/plans',
  'https://threadr-pw0s.onrender.com/api/subscriptions/plans',
  '/subscriptions/current'  // This should be protected
];

console.log('🧪 Testing URL matching logic:\n');
testCases.forEach(testUrl => {
  const isPublic = isPublicEndpoint(testUrl);
  console.log(`${isPublic ? '🔓' : '🔒'} ${testUrl} → ${isPublic ? 'PUBLIC' : 'PROTECTED'}`);
});

console.log('\n🌐 Testing actual requests:\n');

// Test direct curl vs frontend behavior
async function testEndpoint(endpoint, description) {
  try {
    console.log(`Testing: ${description}`);
    console.log(`URL: ${baseUrl}${endpoint}`);
    
    const response = await fetch(`${baseUrl}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'ThreadrNextJS/1.0 (Debug Script)'
      }
    });
    
    console.log(`Status: ${response.status} ${response.statusText}`);
    console.log(`Headers: ${JSON.stringify([...response.headers.entries()], null, 2)}`);
    
    if (response.status === 200) {
      const data = await response.json();
      console.log(`Data: ${JSON.stringify(data, null, 2)}`);
    } else {
      const errorText = await response.text();
      console.log(`Error: ${errorText}`);
    }
    
  } catch (error) {
    console.log(`Fetch Error: ${error.message}`);
  }
  console.log('---');
}

// Run tests
async function runTests() {
  await testEndpoint('/subscriptions/plans', 'Public subscription plans');
  await testEndpoint('/subscriptions/current', 'Protected current subscription (should fail without auth)');
  await testEndpoint('/health', 'Public health check');
}

// Check if we're in Node.js or browser environment
if (typeof window === 'undefined') {
  // Node.js
  const fetch = require('node-fetch');
  runTests();
} else {
  // Browser
  runTests();
}