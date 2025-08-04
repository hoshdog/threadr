/**
 * Comprehensive Functionality Test Suite for Threadr Next.js Application
 * 
 * This test suite verifies what's actually working vs what we think is working
 * by testing all critical user flows with real API calls and UI interactions.
 * 
 * Test Coverage:
 * 1. API Connectivity & Health Checks
 * 2. User Registration Flow
 * 3. User Login Flow  
 * 4. Thread Generation Functionality
 * 5. Dashboard Access & Protected Routes
 * 6. Stripe Payment Integration
 * 
 * Run with: node comprehensive-functionality-test.js
 */

const axios = require('axios');
const fs = require('fs');

// Test Configuration
const TEST_CONFIG = {
  API_BASE_URL: 'https://threadr-production.up.railway.app/api',
  FRONTEND_BASE_URL: 'http://localhost:3000', // Adjust for your dev server
  TEST_USER: {
    email: `test_${Date.now()}@example.com`,
    password: 'TestPassword123!',
    name: 'Test User'
  },
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  DELAY_BETWEEN_TESTS: 1000, // 1 second
};

// Test Results Storage
const testResults = {
  summary: {
    total: 0,
    passed: 0,
    failed: 0,
    skipped: 0,
    startTime: new Date().toISOString(),
    endTime: null,
  },
  details: [],
  failures: [],
  recommendations: []
};

// Utility Functions
function log(message, level = 'INFO') {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${level}: ${message}`;
  console.log(logMessage);
}

function logTest(testName, status, details = '', error = null) {
  const result = {
    testName,
    status,
    details,
    error: error ? error.message : null,
    timestamp: new Date().toISOString()
  };
  
  testResults.details.push(result);
  testResults.summary.total++;
  
  if (status === 'PASS') {
    testResults.summary.passed++;
    log(`✅ PASS: ${testName} - ${details}`, 'TEST');
  } else if (status === 'FAIL') {
    testResults.summary.failed++;
    testResults.failures.push(result);
    log(`❌ FAIL: ${testName} - ${details}${error ? ` (${error.message})` : ''}`, 'TEST');
  } else if (status === 'SKIP') {
    testResults.summary.skipped++;
    log(`⏭️  SKIP: ${testName} - ${details}`, 'TEST');
  }
}

async function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function makeRequest(method, url, data = null, headers = {}) {
  try {
    const config = {
      method,
      url,
      timeout: TEST_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      }
    };
    
    if (data) {
      config.data = data;
    }
    
    const response = await axios(config);
    return { success: true, data: response.data, status: response.status, headers: response.headers };
  } catch (error) {
    return { 
      success: false, 
      error: error.message, 
      status: error.response?.status,
      data: error.response?.data 
    };
  }
}

// Test Suite Functions

/**
 * Test 1: API Connectivity & Health Checks
 */
async function testApiConnectivity() {
  log('Starting API Connectivity Tests...');
  
  // Test 1.1: Basic Health Check
  try {
    const response = await makeRequest('GET', `${TEST_CONFIG.API_BASE_URL}/../health`);
    if (response.success) {
      logTest('API Health Check', 'PASS', `Backend is accessible (${response.status})`);
    } else {
      logTest('API Health Check', 'FAIL', `Backend not accessible`, new Error(response.error));
    }
  } catch (error) {
    logTest('API Health Check', 'FAIL', 'Backend connection failed', error);
  }
  
  // Test 1.2: API Base URL Accessibility
  try {
    const response = await makeRequest('GET', `${TEST_CONFIG.API_BASE_URL}/test`);
    if (response.success || response.status === 404) {
      logTest('API Base URL Access', 'PASS', 'API endpoint responds');
    } else {
      logTest('API Base URL Access', 'FAIL', 'API endpoint not accessible', new Error(response.error));
    }
  } catch (error) {
    logTest('API Base URL Access', 'FAIL', 'API base URL connection failed', error);
  }
  
  // Test 1.3: CORS Configuration
  try {
    const response = await makeRequest('OPTIONS', `${TEST_CONFIG.API_BASE_URL}/generate`);
    const corsHeaders = response.headers && (
      response.headers['access-control-allow-origin'] || 
      response.headers['Access-Control-Allow-Origin']
    );
    if (corsHeaders) {
      logTest('CORS Configuration', 'PASS', `CORS headers present: ${corsHeaders}`);
    } else {
      logTest('CORS Configuration', 'FAIL', 'CORS headers missing');
    }
  } catch (error) {
    logTest('CORS Configuration', 'FAIL', 'CORS check failed', error);
  }
}

/**
 * Test 2: User Registration Flow
 */
async function testUserRegistration() {
  log('Starting User Registration Tests...');
  
  // Test 2.1: Registration Endpoint Exists
  try {
    const response = await makeRequest('POST', `${TEST_CONFIG.API_BASE_URL}/auth/register`, {
      email: TEST_CONFIG.TEST_USER.email,
      password: TEST_CONFIG.TEST_USER.password,
      confirm_password: TEST_CONFIG.TEST_USER.password
    });
    
    if (response.success && response.data.success) {
      logTest('User Registration', 'PASS', 'User registered successfully');
      // Store token for later tests
      if (response.data.data && response.data.data.access_token) {
        TEST_CONFIG.AUTH_TOKEN = response.data.data.access_token;
        TEST_CONFIG.USER_ID = response.data.data.user?.user_id;
      }
    } else if (response.status === 400 && response.data?.error?.includes('already exists')) {
      logTest('User Registration', 'PASS', 'Registration validation working (user already exists)');
    } else {
      logTest('User Registration', 'FAIL', `Registration failed: ${response.error || JSON.stringify(response.data)}`);
    }
  } catch (error) {
    logTest('User Registration', 'FAIL', 'Registration endpoint failed', error);
  }
  
  // Test 2.2: Registration Validation
  try {
    const response = await makeRequest('POST', `${TEST_CONFIG.API_BASE_URL}/auth/register`, {
      email: 'invalid-email',
      password: '123'
    });
    
    if (!response.success || response.data?.error) {
      logTest('Registration Validation', 'PASS', 'Input validation working');
    } else {
      logTest('Registration Validation', 'FAIL', 'Validation should reject invalid inputs');
    }
  } catch (error) {
    logTest('Registration Validation', 'PASS', 'Validation working (threw error for invalid input)');
  }
}

/**
 * Test 3: User Login Flow
 */
async function testUserLogin() {
  log('Starting User Login Tests...');
  
  // Test 3.1: Login with Valid Credentials
  try {
    const response = await makeRequest('POST', `${TEST_CONFIG.API_BASE_URL}/auth/login`, {
      email: TEST_CONFIG.TEST_USER.email,
      password: TEST_CONFIG.TEST_USER.password
    });
    
    if (response.success && response.data.success && response.data.data.access_token) {
      logTest('User Login', 'PASS', 'Login successful with valid credentials');
      TEST_CONFIG.AUTH_TOKEN = response.data.data.access_token;
      TEST_CONFIG.USER_ID = response.data.data.user?.user_id;
    } else {
      logTest('User Login', 'FAIL', `Login failed: ${response.error || JSON.stringify(response.data)}`);
    }
  } catch (error) {
    logTest('User Login', 'FAIL', 'Login endpoint failed', error);
  }
  
  // Test 3.2: Login with Invalid Credentials
  try {
    const response = await makeRequest('POST', `${TEST_CONFIG.API_BASE_URL}/auth/login`, {
      email: TEST_CONFIG.TEST_USER.email,
      password: 'wrongpassword'
    });
    
    if (!response.success || (response.data && !response.data.success)) {
      logTest('Login Validation', 'PASS', 'Invalid credentials properly rejected');
    } else {
      logTest('Login Validation', 'FAIL', 'Should reject invalid credentials');
    }
  } catch (error) {
    logTest('Login Validation', 'PASS', 'Invalid credentials properly rejected (threw error)');
  }
  
  // Test 3.3: Protected Profile Endpoint
  if (TEST_CONFIG.AUTH_TOKEN) {
    try {
      const response = await makeRequest('GET', `${TEST_CONFIG.API_BASE_URL}/auth/me`, null, {
        'Authorization': `Bearer ${TEST_CONFIG.AUTH_TOKEN}`
      });
      
      if (response.success && response.data.success) {
        logTest('Protected Route Access', 'PASS', 'Auth token works for protected routes');
      } else {
        logTest('Protected Route Access', 'FAIL', 'Auth token not working for protected routes');
      }
    } catch (error) {
      logTest('Protected Route Access', 'FAIL', 'Protected route access failed', error);
    }
  } else {
    logTest('Protected Route Access', 'SKIP', 'No auth token available');
  }
}

/**
 * Test 4: Thread Generation Functionality
 */
async function testThreadGeneration() {
  log('Starting Thread Generation Tests...');
  
  // Test 4.1: Generate Thread from Text
  try {
    const testContent = "This is a test article about technology trends. Artificial intelligence is revolutionizing how we work and live. Machine learning algorithms are becoming more sophisticated every day.";
    
    const response = await makeRequest('POST', `${TEST_CONFIG.API_BASE_URL}/generate`, {
      text: testContent
    });
    
    if (response.success && response.data.success && response.data.data.tweets) {
      const tweets = response.data.data.tweets;
      logTest('Thread Generation (Text)', 'PASS', `Generated ${tweets.length} tweets from text`);
    } else {
      logTest('Thread Generation (Text)', 'FAIL', `Generation failed: ${response.error || JSON.stringify(response.data)}`);
    }
  } catch (error) {
    logTest('Thread Generation (Text)', 'FAIL', 'Text generation failed', error);
  }
  
  // Test 4.2: Generate Thread from URL (if URL scraping is enabled)
  try {
    const response = await makeRequest('POST', `${TEST_CONFIG.API_BASE_URL}/generate`, {
      url: 'https://example.com'
    });
    
    if (response.success && response.data.success) {
      logTest('Thread Generation (URL)', 'PASS', 'URL generation working');
    } else if (response.data?.error?.includes('domain not allowed')) {
      logTest('Thread Generation (URL)', 'PASS', 'URL validation working (domain restrictions)');
    } else {
      logTest('Thread Generation (URL)', 'FAIL', `URL generation failed: ${response.error || JSON.stringify(response.data)}`);
    }
  } catch (error) {
    logTest('Thread Generation (URL)', 'FAIL', 'URL generation failed', error);
  }
  
  // Test 4.3: Rate Limiting
  try {
    // Make multiple requests quickly to test rate limiting
    const requests = [];
    for (let i = 0; i < 6; i++) {
      requests.push(makeRequest('POST', `${TEST_CONFIG.API_BASE_URL}/generate`, {
        text: `Test content ${i}`
      }));
    }
    
    const responses = await Promise.all(requests);
    const rateLimited = responses.some(r => !r.success && (r.status === 429 || r.data?.error?.includes('rate limit')));
    
    if (rateLimited) {
      logTest('Rate Limiting', 'PASS', 'Rate limiting is working');
    } else {
      logTest('Rate Limiting', 'FAIL', 'Rate limiting may not be working properly');
    }
  } catch (error) {
    logTest('Rate Limiting', 'FAIL', 'Rate limiting test failed', error);
  }
  
  // Test 4.4: Usage Stats
  try {
    const response = await makeRequest('GET', `${TEST_CONFIG.API_BASE_URL}/usage-stats`);
    
    if (response.success && response.data.success) {
      logTest('Usage Statistics', 'PASS', 'Usage stats endpoint working');
    } else {
      logTest('Usage Statistics', 'FAIL', 'Usage stats not available');
    }
  } catch (error) {
    logTest('Usage Statistics', 'FAIL', 'Usage stats test failed', error);
  }
}

/**
 * Test 5: Dashboard Access & Protected Routes
 */
async function testDashboardAccess() {
  log('Starting Dashboard Access Tests...');
  
  if (!TEST_CONFIG.AUTH_TOKEN) {
    logTest('Dashboard Access', 'SKIP', 'No auth token available');
    return;
  }
  
  // Test 5.1: Thread History
  try {
    const response = await makeRequest('GET', `${TEST_CONFIG.API_BASE_URL}/threads`, null, {
      'Authorization': `Bearer ${TEST_CONFIG.AUTH_TOKEN}`
    });
    
    if (response.success && response.data.success) {
      logTest('Thread History', 'PASS', 'Thread history endpoint working');
    } else {
      logTest('Thread History', 'FAIL', `Thread history failed: ${response.error || JSON.stringify(response.data)}`);
    }
  } catch (error) {
    logTest('Thread History', 'FAIL', 'Thread history test failed', error);
  }
  
  // Test 5.2: Analytics Dashboard
  try {
    const response = await makeRequest('GET', `${TEST_CONFIG.API_BASE_URL}/analytics/dashboard`, null, {
      'Authorization': `Bearer ${TEST_CONFIG.AUTH_TOKEN}`
    });
    
    if (response.success && response.data.success) {
      logTest('Analytics Dashboard', 'PASS', 'Analytics dashboard working');
    } else if (response.status === 404) {
      logTest('Analytics Dashboard', 'SKIP', 'Analytics endpoint not implemented yet');
    } else {
      logTest('Analytics Dashboard', 'FAIL', `Analytics failed: ${response.error || JSON.stringify(response.data)}`);
    }
  } catch (error) {
    logTest('Analytics Dashboard', 'FAIL', 'Analytics test failed', error);
  }
  
  // Test 5.3: Templates
  try {
    const response = await makeRequest('GET', `${TEST_CONFIG.API_BASE_URL}/templates`);
    
    if (response.success && response.data.success) {
      logTest('Templates', 'PASS', 'Templates endpoint working');
    } else if (response.status === 404) {
      logTest('Templates', 'SKIP', 'Templates endpoint not implemented yet');
    } else {
      logTest('Templates', 'FAIL', `Templates failed: ${response.error || JSON.stringify(response.data)}`);
    }
  } catch (error) {
    logTest('Templates', 'FAIL', 'Templates test failed', error);
  }
}

/**
 * Test 6: Stripe Payment Integration
 */
async function testStripeIntegration() {
  log('Starting Stripe Payment Tests...');
  
  // Test 6.1: Payment Configuration
  try {
    const response = await makeRequest('GET', `${TEST_CONFIG.API_BASE_URL}/payment/config`);
    
    if (response.success && response.data.success) {
      logTest('Payment Config', 'PASS', 'Payment configuration endpoint working');
    } else {
      logTest('Payment Config', 'FAIL', `Payment config failed: ${response.error || JSON.stringify(response.data)}`);
    }
  } catch (error) {
    logTest('Payment Config', 'FAIL', 'Payment config test failed', error);
  }
  
  // Test 6.2: Checkout Session Creation
  try {
    const response = await makeRequest('POST', `${TEST_CONFIG.API_BASE_URL}/stripe/create-checkout-session`, {
      priceId: 'test-price-id',
      successUrl: 'https://example.com/success',
      cancelUrl: 'https://example.com/cancel'
    });
    
    if (response.success && response.data.success) {
      logTest('Stripe Checkout', 'PASS', 'Checkout session creation working');
    } else if (response.data?.error?.includes('price') || response.data?.error?.includes('Stripe')) {
      logTest('Stripe Checkout', 'PASS', 'Stripe integration configured (validation working)');
    } else {
      logTest('Stripe Checkout', 'FAIL', `Checkout failed: ${response.error || JSON.stringify(response.data)}`);
    }
  } catch (error) {
    logTest('Stripe Checkout', 'FAIL', 'Stripe checkout test failed', error);
  }
  
  // Test 6.3: Premium Status Check
  try {
    const response = await makeRequest('GET', `${TEST_CONFIG.API_BASE_URL}/premium/check`);
    
    if (response.success && response.data.success) {
      logTest('Premium Status', 'PASS', 'Premium status check working');
    } else {
      logTest('Premium Status', 'FAIL', `Premium status failed: ${response.error || JSON.stringify(response.data)}`);
    }
  } catch (error) {
    logTest('Premium Status', 'FAIL', 'Premium status test failed', error);
  }
}

/**
 * Generate Final Report
 */
function generateReport() {
  testResults.summary.endTime = new Date().toISOString();
  
  const report = `
# Comprehensive Functionality Test Report
**Generated:** ${testResults.summary.endTime}
**Test Duration:** ${Math.round((new Date(testResults.summary.endTime) - new Date(testResults.summary.startTime)) / 1000)}s

## Summary
- **Total Tests:** ${testResults.summary.total}
- **Passed:** ${testResults.summary.passed} ✅
- **Failed:** ${testResults.summary.failed} ❌
- **Skipped:** ${testResults.summary.skipped} ⏭️
- **Success Rate:** ${testResults.summary.total > 0 ? Math.round((testResults.summary.passed / testResults.summary.total) * 100) : 0}%

## Test Results Details

${testResults.details.map(test => 
  `### ${test.status === 'PASS' ? '✅' : test.status === 'FAIL' ? '❌' : '⏭️'} ${test.testName}
**Status:** ${test.status}
**Details:** ${test.details}
${test.error ? `**Error:** ${test.error}` : ''}
**Timestamp:** ${test.timestamp}
`).join('\n')}

## Critical Failures
${testResults.failures.length > 0 ? testResults.failures.map(failure => 
  `- **${failure.testName}:** ${failure.details} ${failure.error ? `(${failure.error})` : ''}`
).join('\n') : 'No critical failures detected.'}

## Recommendations

${testResults.failures.length > 0 ? 
  testResults.failures.map(failure => {
    if (failure.testName.includes('API Health')) {
      return '- **Backend Connectivity Issue:** Verify Railway deployment is running and accessible';
    } else if (failure.testName.includes('Registration') || failure.testName.includes('Login')) {
      return '- **Authentication Issues:** Check auth endpoints and database connectivity';
    } else if (failure.testName.includes('Thread Generation')) {
      return '- **Core Functionality Issue:** Verify OpenAI API key and thread generation logic';
    } else if (failure.testName.includes('Dashboard') || failure.testName.includes('Protected')) {
      return '- **Authorization Issues:** Check JWT token handling and middleware';
    } else if (failure.testName.includes('Stripe') || failure.testName.includes('Payment')) {
      return '- **Payment Integration Issues:** Verify Stripe API keys and webhook configuration';
    }
    return `- **${failure.testName}:** Review implementation and error details`;
  }).join('\n') : 
  '- All critical functionality is working properly\n- Continue with frontend UI integration testing'
}

## Next Steps

${testResults.summary.failed > 0 ? 
  `1. **Priority 1:** Fix the ${testResults.summary.failed} failing test(s) listed above
2. **Priority 2:** Test frontend UI integration with working backend endpoints
3. **Priority 3:** Implement missing features identified as "SKIP" in tests` :
  `1. **Frontend Integration:** All backend functionality is working - focus on UI integration
2. **User Acceptance Testing:** Run manual tests with real users
3. **Performance Testing:** Test with higher loads and concurrent users`
}

---
*This report was generated by the Threadr Comprehensive Functionality Test Suite*
`;

  return report;
}

/**
 * Main Test Runner
 */
async function runAllTests() {
  log('🚀 Starting Comprehensive Functionality Test Suite...');
  log(`Testing against: ${TEST_CONFIG.API_BASE_URL}`);
  
  try {
    // Run all test suites
    await testApiConnectivity();
    await delay(TEST_CONFIG.DELAY_BETWEEN_TESTS);
    
    await testUserRegistration();
    await delay(TEST_CONFIG.DELAY_BETWEEN_TESTS);
    
    await testUserLogin();
    await delay(TEST_CONFIG.DELAY_BETWEEN_TESTS);
    
    await testThreadGeneration();
    await delay(TEST_CONFIG.DELAY_BETWEEN_TESTS);
    
    await testDashboardAccess();
    await delay(TEST_CONFIG.DELAY_BETWEEN_TESTS);
    
    await testStripeIntegration();
    
    // Generate final report
    const report = generateReport();
    
    // Save report to file
    const reportPath = `C:\\Users\\HoshitoPowell\\Desktop\\Threadr\\threadr-nextjs\\test-report-${Date.now()}.md`;
    fs.writeFileSync(reportPath, report);
    
    log(`📋 Test Report saved to: ${reportPath}`);
    log('🏁 Test Suite Completed!');
    
    // Print summary to console
    console.log('\n' + '='.repeat(60));
    console.log('COMPREHENSIVE FUNCTIONALITY TEST RESULTS');
    console.log('='.repeat(60));
    console.log(`✅ Passed: ${testResults.summary.passed}`);
    console.log(`❌ Failed: ${testResults.summary.failed}`);
    console.log(`⏭️  Skipped: ${testResults.summary.skipped}`);
    console.log(`📊 Success Rate: ${testResults.summary.total > 0 ? Math.round((testResults.summary.passed / testResults.summary.total) * 100) : 0}%`);
    console.log('='.repeat(60));
    
    if (testResults.failures.length > 0) {
      console.log('\n🚨 CRITICAL FAILURES:');
      testResults.failures.forEach(failure => {
        console.log(`   - ${failure.testName}: ${failure.details}`);
      });
    }
    
    console.log(`\n📋 Full report: ${reportPath}`);
    
    return testResults;
    
  } catch (error) {
    log(`Fatal error during test execution: ${error.message}`, 'ERROR');
    throw error;
  }
}

// Run tests if this file is executed directly
if (require.main === module) {
  runAllTests()
    .then((results) => {
      process.exit(results.summary.failed > 0 ? 1 : 0);
    })
    .catch((error) => {
      console.error('Test suite crashed:', error);
      process.exit(1);
    });
}

module.exports = {
  runAllTests,
  testResults,
  TEST_CONFIG
};