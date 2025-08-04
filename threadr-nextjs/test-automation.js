/**
 * Threadr App - Automated Test Suite
 * Run this in browser console to test core functionality
 */

class ThreadrTestSuite {
  constructor() {
    this.baseUrl = 'http://localhost:3000';
    this.apiUrl = 'https://threadr-production.up.railway.app/api';
    this.results = [];
    this.testEmail = `test+${Date.now()}@example.com`;
    this.testPassword = 'TestPass123!';
  }

  log(test, status, message, details = null) {
    const result = {
      test,
      status,
      message,
      details,
      timestamp: new Date().toISOString()
    };
    this.results.push(result);
    
    const emoji = status === 'PASS' ? '✅' : status === 'FAIL' ? '❌' : '⏳';
    console.log(`${emoji} ${test}: ${message}`);
    if (details) console.log('   Details:', details);
  }

  async sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async runAllTests() {
    console.log('🚀 Starting Threadr App Test Suite...\n');
    
    await this.testBackendConnection();
    await this.testThreadGeneration();
    await this.testAuthentication();
    await this.testRateLimiting();
    await this.testPremiumFeatures();
    
    this.generateReport();
  }

  async testBackendConnection() {
    console.log('\n📡 Testing Backend Connection...');
    
    try {
      const response = await fetch(`${this.apiUrl}/health`);
      const data = await response.json();
      
      if (response.ok && data.status === 'healthy') {
        this.log('Backend Health', 'PASS', 'Backend is responding correctly', data);
      } else {
        this.log('Backend Health', 'FAIL', 'Backend health check failed', data);
      }
    } catch (error) {
      this.log('Backend Health', 'FAIL', 'Failed to connect to backend', error.message);
    }

    // Test CORS
    try {
      const corsResponse = await fetch(`${this.apiUrl}/usage-stats`);
      if (corsResponse.ok || corsResponse.status === 401) {
        this.log('CORS Configuration', 'PASS', 'CORS headers allow frontend access');
      } else {
        this.log('CORS Configuration', 'FAIL', 'CORS may be misconfigured', corsResponse.status);
      }
    } catch (error) {
      this.log('CORS Configuration', 'FAIL', 'CORS error detected', error.message);
    }
  }

  async testThreadGeneration() {
    console.log('\n🧵 Testing Thread Generation...');

    // Test with sample text
    const testContent = "Content marketing is the strategic approach focused on creating valuable content to attract customers. It builds trust and establishes authority in your industry.";
    
    try {
      const response = await fetch(`${this.apiUrl}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: testContent
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.tweets && Array.isArray(data.tweets) && data.tweets.length > 0) {
          this.log('Text Generation', 'PASS', `Generated ${data.tweets.length} tweets`, {
            tweetCount: data.tweets.length,
            firstTweet: data.tweets[0]?.substring(0, 100) + '...'
          });
          
          // Verify character limits
          const longTweets = data.tweets.filter(tweet => tweet.length > 280);
          if (longTweets.length === 0) {
            this.log('Character Limits', 'PASS', 'All tweets under 280 characters');
          } else {
            this.log('Character Limits', 'FAIL', `${longTweets.length} tweets exceed 280 chars`, longTweets);
          }
        } else {
          this.log('Text Generation', 'FAIL', 'Invalid response format', data);
        }
      } else {
        const errorData = await response.text();
        this.log('Text Generation', 'FAIL', `API returned ${response.status}`, errorData);
      }
    } catch (error) {
      this.log('Text Generation', 'FAIL', 'Network error during generation', error.message);
    }

    // Test URL generation (if supported)
    try {
      const urlResponse = await fetch(`${this.apiUrl}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: 'https://medium.com/@test/sample-article'
        })
      });

      if (urlResponse.ok) {
        const urlData = await urlResponse.json();
        this.log('URL Generation', 'PASS', 'URL processing works', {
          tweetCount: urlData.tweets?.length || 0
        });
      } else {
        this.log('URL Generation', 'INFO', 'URL generation may not work with test URL', urlResponse.status);
      }
    } catch (error) {
      this.log('URL Generation', 'INFO', 'URL generation test skipped', error.message);
    }
  }

  async testAuthentication() {
    console.log('\n🔐 Testing Authentication...');

    // Test user registration
    try {
      const registerResponse = await fetch(`${this.apiUrl}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: this.testEmail,
          password: this.testPassword,
          confirmPassword: this.testPassword
        })
      });

      if (registerResponse.ok) {
        const registerData = await registerResponse.json();
        if (registerData.token) {
          this.log('User Registration', 'PASS', 'Registration successful with JWT token');
          this.authToken = registerData.token;
          
          // Store token in localStorage like the app would
          localStorage.setItem('auth-token', this.authToken);
        } else {
          this.log('User Registration', 'FAIL', 'Registration succeeded but no token', registerData);
        }
      } else {
        const errorData = await registerResponse.text();
        this.log('User Registration', 'FAIL', `Registration failed: ${registerResponse.status}`, errorData);
      }
    } catch (error) {
      this.log('User Registration', 'FAIL', 'Registration network error', error.message);
    }

    // Test login with created account
    try {
      const loginResponse = await fetch(`${this.apiUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: this.testEmail,
          password: this.testPassword
        })
      });

      if (loginResponse.ok) {
        const loginData = await loginResponse.json();
        if (loginData.token) {
          this.log('User Login', 'PASS', 'Login successful');
          this.authToken = loginData.token;
        } else {
          this.log('User Login', 'FAIL', 'Login succeeded but no token', loginData);
        }
      } else {
        const errorData = await loginResponse.text();
        this.log('User Login', 'FAIL', `Login failed: ${loginResponse.status}`, errorData);
      }
    } catch (error) {
      this.log('User Login', 'FAIL', 'Login network error', error.message);
    }

    // Test protected endpoint access
    if (this.authToken) {
      try {
        const profileResponse = await fetch(`${this.apiUrl}/auth/me`, {
          headers: {
            'Authorization': `Bearer ${this.authToken}`
          }
        });

        if (profileResponse.ok) {
          const profileData = await profileResponse.json();
          this.log('Protected Route Access', 'PASS', 'JWT authentication works', {
            email: profileData.email,
            isPremium: profileData.isPremium
          });
        } else {
          this.log('Protected Route Access', 'FAIL', 'JWT token not accepted', profileResponse.status);
        }
      } catch (error) {
        this.log('Protected Route Access', 'FAIL', 'Error accessing protected route', error.message);
      }
    }
  }

  async testRateLimiting() {
    console.log('\n⏱️ Testing Rate Limiting...');

    try {
      const usageResponse = await fetch(`${this.apiUrl}/usage-stats`);
      if (usageResponse.ok) {
        const usageData = await usageResponse.json();
        this.log('Usage Stats', 'PASS', 'Usage tracking is working', {
          dailyUsage: usageData.daily_usage,
          monthlyUsage: usageData.monthly_usage,
          hasLimit: usageData.daily_limit || usageData.monthly_limit
        });

        // Check if limits are properly configured
        if (usageData.daily_limit === 5 && usageData.monthly_limit === 20) {
          this.log('Rate Limit Config', 'PASS', 'Free tier limits correctly set (5 daily, 20 monthly)');
        } else {
          this.log('Rate Limit Config', 'FAIL', 'Rate limits not set correctly', {
            expected: { daily: 5, monthly: 20 },
            actual: { daily: usageData.daily_limit, monthly: usageData.monthly_limit }
          });
        }
      } else {
        this.log('Usage Stats', 'FAIL', 'Usage stats endpoint not working', usageResponse.status);
      }
    } catch (error) {
      this.log('Usage Stats', 'FAIL', 'Error fetching usage stats', error.message);
    }

    // Test premium status check
    try {
      const premiumResponse = await fetch(`${this.apiUrl}/premium-status`);
      if (premiumResponse.ok) {
        const premiumData = await premiumResponse.json();
        this.log('Premium Status', 'PASS', 'Premium status tracking works', {
          hasPremium: premiumData.has_premium,
          expiresAt: premiumData.premium_expires_at
        });
      } else {
        this.log('Premium Status', 'FAIL', 'Premium status endpoint error', premiumResponse.status);
      }
    } catch (error) {
      this.log('Premium Status', 'FAIL', 'Error checking premium status', error.message);
    }
  }

  async testPremiumFeatures() {
    console.log('\n✨ Testing Premium Features...');

    // Test template access (if endpoint exists)
    try {
      const templatesResponse = await fetch(`${this.apiUrl}/templates`);
      if (templatesResponse.ok) {
        const templatesData = await templatesResponse.json();
        this.log('Templates Endpoint', 'PASS', 'Templates feature is available', {
          templateCount: templatesData.length || Object.keys(templatesData).length
        });
      } else {
        this.log('Templates Endpoint', 'INFO', 'Templates endpoint may not exist yet', templatesResponse.status);
      }
    } catch (error) {
      this.log('Templates Endpoint', 'INFO', 'Templates feature not implemented', error.message);
    }

    // Test thread history (if endpoint exists)
    if (this.authToken) {
      try {
        const historyResponse = await fetch(`${this.apiUrl}/threads`, {
          headers: {
            'Authorization': `Bearer ${this.authToken}`
          }
        });
        
        if (historyResponse.ok) {
          const historyData = await historyResponse.json();
          this.log('Thread History', 'PASS', 'Thread history feature works', {
            threadCount: historyData.length || 0
          });
        } else {
          this.log('Thread History', 'INFO', 'Thread history may not be implemented', historyResponse.status);
        }
      } catch (error) {
        this.log('Thread History', 'INFO', 'Thread history feature not available', error.message);
      }
    }
  }

  generateReport() {
    console.log('\n📊 TEST SUMMARY REPORT');
    console.log('=' .repeat(50));

    const totalTests = this.results.length;
    const passedTests = this.results.filter(r => r.status === 'PASS').length;
    const failedTests = this.results.filter(r => r.status === 'FAIL').length;
    const infoTests = this.results.filter(r => r.status === 'INFO').length;

    console.log(`Total Tests: ${totalTests}`);
    console.log(`✅ Passed: ${passedTests}`);
    console.log(`❌ Failed: ${failedTests}`);
    console.log(`ℹ️  Info: ${infoTests}`);
    console.log(`Success Rate: ${((passedTests / (totalTests - infoTests)) * 100).toFixed(1)}%`);

    console.log('\n🎯 REVENUE READINESS ASSESSMENT:');
    
    const criticalTests = [
      'Backend Health',
      'Text Generation', 
      'User Registration',
      'User Login',
      'Usage Stats'
    ];

    const criticalFailures = this.results.filter(r => 
      criticalTests.includes(r.test) && r.status === 'FAIL'
    );

    if (criticalFailures.length === 0) {
      console.log('✅ READY FOR REVENUE: All critical systems operational');
      console.log('   Next steps: Deploy to production and start marketing');
    } else {
      console.log('❌ NOT READY: Critical issues must be fixed first');
      console.log('   Critical failures:');
      criticalFailures.forEach(failure => {
        console.log(`   - ${failure.test}: ${failure.message}`);
      });
    }

    console.log('\n💰 MONETIZATION CHECKLIST:');
    const checks = {
      'Thread Generation Works': this.results.some(r => r.test === 'Text Generation' && r.status === 'PASS'),
      'Authentication System': this.results.some(r => r.test === 'User Login' && r.status === 'PASS'),
      'Rate Limiting Active': this.results.some(r => r.test === 'Rate Limit Config' && r.status === 'PASS'),
      'Backend Operational': this.results.some(r => r.test === 'Backend Health' && r.status === 'PASS')
    };

    Object.entries(checks).forEach(([check, passed]) => {
      console.log(`${passed ? '✅' : '❌'} ${check}`);
    });

    const readinessScore = Object.values(checks).filter(Boolean).length / Object.keys(checks).length;
    console.log(`\nReadiness Score: ${(readinessScore * 100).toFixed(0)}%`);

    if (readinessScore >= 0.75) {
      console.log('🚀 App is ready for production launch!');
    } else {
      console.log('⚠️  App needs more work before launch');
    }

    // Cleanup test account
    console.log('\n🧹 Cleaning up test data...');
    localStorage.removeItem('auth-token');
  }
}

// Auto-run if in browser console
if (typeof window !== 'undefined') {
  console.log('🔧 Threadr Test Suite Loaded');
  console.log('📋 Run: new ThreadrTestSuite().runAllTests()');
  
  // Make it globally available
  window.ThreadrTestSuite = ThreadrTestSuite;
}

// Export for use in test files
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ThreadrTestSuite;
}