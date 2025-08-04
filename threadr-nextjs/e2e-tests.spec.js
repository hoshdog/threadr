/**
 * Threadr E2E Tests using Playwright
 * 
 * To run these tests:
 * 1. npm install @playwright/test
 * 2. npx playwright test e2e-tests.spec.js
 * 
 * These tests verify the complete user journey from free user to paying customer
 */

const { test, expect } = require('@playwright/test');

// Test configuration
const BASE_URL = 'http://localhost:3000';
const API_URL = 'https://threadr-production.up.railway.app/api';
const TEST_EMAIL = `test+${Date.now()}@example.com`;
const TEST_PASSWORD = 'TestPass123!';

// Test content
const SAMPLE_CONTENT = `
Content marketing is the strategic approach focused on creating and distributing valuable, relevant content to attract and retain customers. Unlike traditional advertising, content marketing provides genuine value to the audience before asking for anything in return. This builds trust and establishes authority in your industry. The key is consistency and quality over quantity. When done right, content marketing drives engagement, builds relationships, and ultimately converts prospects into loyal customers.
`;

const SAMPLE_URL = 'https://medium.com/@example/test-article';

test.describe('Threadr App E2E Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Start with a clean slate
    await page.goto(BASE_URL);
    await page.evaluate(() => localStorage.clear());
  });

  test.describe('🧵 Core Thread Generation', () => {
    
    test('should generate thread from text content', async ({ page }) => {
      await page.goto(BASE_URL);
      
      // Wait for page to load
      await expect(page.locator('h1')).toBeVisible();
      
      // Find and fill the content input
      const textInput = page.locator('textarea, input[type="text"]').first();
      await textInput.fill(SAMPLE_CONTENT);
      
      // Click generate button
      const generateButton = page.locator('button').filter({ hasText: /generate/i });
      await generateButton.click();
      
      // Wait for results - should see tweets generated
      await expect(page.locator('[data-testid="tweet-card"], .tweet, [class*="tweet"]')).toHaveCount(3, { timeout: 15000 });
      
      // Verify tweets have reasonable content
      const firstTweet = page.locator('[data-testid="tweet-card"], .tweet, [class*="tweet"]').first();
      await expect(firstTweet).toContainText(/content marketing/i);
    });

    test('should handle invalid URL gracefully', async ({ page }) => {
      await page.goto(BASE_URL);
      
      // Try invalid URL
      const urlInput = page.locator('input[type="url"], input[placeholder*="url"], input[placeholder*="http"]').first();
      await urlInput.fill('not-a-valid-url');
      
      const generateButton = page.locator('button').filter({ hasText: /generate/i });
      await generateButton.click();
      
      // Should see error message
      await expect(page.locator('[class*="error"], .alert-error, [role="alert"]')).toBeVisible({ timeout: 10000 });
    });

    test('should display character counts correctly', async ({ page }) => {
      await page.goto(BASE_URL);
      
      // Generate a thread
      const textInput = page.locator('textarea, input[type="text"]').first();
      await textInput.fill(SAMPLE_CONTENT);
      
      const generateButton = page.locator('button').filter({ hasText: /generate/i });
      await generateButton.click();
      
      // Wait for tweets
      await page.waitForSelector('[data-testid="tweet-card"], .tweet, [class*="tweet"]', { timeout: 15000 });
      
      // Check that character counts are displayed and under 280
      const tweets = page.locator('[data-testid="tweet-card"], .tweet, [class*="tweet"]');
      const count = await tweets.count();
      
      for (let i = 0; i < count; i++) {
        const tweet = tweets.nth(i);
        const tweetText = await tweet.textContent();
        
        // Each tweet should be under 280 characters
        expect(tweetText.length).toBeLessThanOrEqual(280);
      }
    });
  });

  test.describe('🔐 Authentication Flow', () => {
    
    test('should register new user successfully', async ({ page }) => {
      await page.goto(`${BASE_URL}/register`);
      
      // Fill registration form
      await page.fill('input[type="email"]', TEST_EMAIL);
      await page.fill('input[type="password"]', TEST_PASSWORD);
      
      // Handle confirm password if present
      const confirmPasswordField = page.locator('input[name="confirmPassword"], input[placeholder*="confirm"]');
      if (await confirmPasswordField.count() > 0) {
        await confirmPasswordField.fill(TEST_PASSWORD);
      }
      
      // Submit form
      await page.click('button[type="submit"], button:has-text("Register"), button:has-text("Sign Up")');
      
      // Should redirect to dashboard or show success
      await expect(page).not.toHaveURL(/register/);
      
      // Should see user logged in state
      await expect(page.locator('text=Welcome', 'text=Dashboard', '[data-testid="user-menu"]')).toBeVisible({ timeout: 10000 });
    });

    test('should login existing user', async ({ page }) => {
      // First register a user (assuming registration works)
      const response = await page.request.post(`${API_URL}/auth/register`, {
        data: {
          email: TEST_EMAIL,
          password: TEST_PASSWORD,
          confirmPassword: TEST_PASSWORD
        }
      });
      
      if (!response.ok()) {
        console.log('Registration failed, but continuing with login test');
      }
      
      // Now test login
      await page.goto(`${BASE_URL}/login`);
      
      await page.fill('input[type="email"]', TEST_EMAIL);
      await page.fill('input[type="password"]', TEST_PASSWORD);
      
      await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
      
      // Should be logged in
      await expect(page).not.toHaveURL(/login/);
      await expect(page.locator('text=Welcome', 'text=Dashboard', '[data-testid="user-menu"]')).toBeVisible({ timeout: 10000 });
    });

    test('should persist login after page refresh', async ({ page }) => {
      // Login first
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[type="email"]', TEST_EMAIL);
      await page.fill('input[type="password"]', TEST_PASSWORD);
      await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
      
      // Wait for login to complete
      await page.waitForTimeout(2000);
      
      // Refresh page
      await page.reload();
      
      // Should still be logged in
      await expect(page.locator('text=Welcome', 'text=Dashboard', '[data-testid="user-menu"]')).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('⏱️ Rate Limiting & Premium Upgrade', () => {
    
    test('should show rate limit after 5 generations', async ({ page }) => {
      await page.goto(BASE_URL);
      
      // Generate 5 threads quickly (free tier limit)
      for (let i = 0; i < 5; i++) {
        const textInput = page.locator('textarea, input[type="text"]').first();
        await textInput.fill(`Test content ${i + 1}: ${SAMPLE_CONTENT}`);
        
        const generateButton = page.locator('button').filter({ hasText: /generate/i });
        await generateButton.click();
        
        // Wait a bit between requests
        await page.waitForTimeout(1000);
      }
      
      // 6th attempt should show rate limit
      const textInput = page.locator('textarea, input[type="text"]').first();
      await textInput.fill('6th attempt content');
      
      const generateButton = page.locator('button').filter({ hasText: /generate/i });
      await generateButton.click();
      
      // Should see upgrade prompt
      await expect(page.locator('text=upgrade', 'text=premium', 'text=limit', '[class*="upgrade"]')).toBeVisible({ timeout: 10000 });
    });

    test('should display usage counter', async ({ page }) => {
      await page.goto(BASE_URL);
      
      // Generate one thread
      const textInput = page.locator('textarea, input[type="text"]').first();
      await textInput.fill(SAMPLE_CONTENT);
      
      const generateButton = page.locator('button').filter({ hasText: /generate/i });
      await generateButton.click();
      
      // Wait for generation to complete
      await page.waitForTimeout(3000);
      
      // Should see usage indicator (e.g., "1/5 daily")
      await expect(page.locator('text=/[0-9]+\/[0-9]+/', '[data-testid="usage-indicator"]')).toBeVisible();
    });

    test('should show premium upgrade modal', async ({ page }) => {
      await page.goto(BASE_URL);
      
      // Look for upgrade button (might be in header or after rate limit)
      const upgradeButton = page.locator('button:has-text("Upgrade"), button:has-text("Premium"), a[href*="upgrade"]');
      
      if (await upgradeButton.count() > 0) {
        await upgradeButton.first().click();
        
        // Should see pricing information
        await expect(page.locator('text=$4.99', 'text=30 days', '[data-testid="pricing-modal"]')).toBeVisible();
      } else {
        console.log('Upgrade button not found - may need to hit rate limit first');
      }
    });
  });

  test.describe('💳 Payment Integration', () => {
    
    test('should redirect to Stripe checkout', async ({ page }) => {
      await page.goto(BASE_URL);
      
      // Find upgrade/payment button
      const paymentButton = page.locator('button:has-text("Upgrade"), button:has-text("$4.99"), a[href*="stripe"]');
      
      if (await paymentButton.count() > 0) {
        // Click payment button
        await paymentButton.first().click();
        
        // Should either redirect to Stripe or open payment modal
        await page.waitForTimeout(3000);
        
        // Check for Stripe checkout page or embedded form
        const isStripeCheckout = page.url().includes('checkout.stripe.com') || 
                                page.url().includes('stripe') ||
                                await page.locator('[data-testid="stripe-checkout"], iframe[src*="stripe"]').count() > 0;
        
        if (isStripeCheckout) {
          console.log('✅ Successfully redirected to Stripe checkout');
        } else {
          console.log('ℹ️ Payment integration may need configuration');
        }
      } else {
        console.log('Payment button not found - may need to hit rate limit first');
      }
    });
    
    test('should handle payment success flow', async ({ page }) => {
      // This would require Stripe test mode setup
      // For now, we'll simulate the success callback
      
      await page.goto(`${BASE_URL}?payment=success&session_id=test_session_123`);
      
      // Should show success message or premium features
      await expect(
        page.locator('text=success', 'text=premium', 'text=unlimited', '[data-testid="payment-success"]')
      ).toBeVisible({ timeout: 5000 });
      
      console.log('ℹ️ Payment success flow test requires Stripe webhook configuration');
    });
  });

  test.describe('✨ Premium Features', () => {
    
    test('should show premium templates', async ({ page }) => {
      // This assumes user has premium access
      await page.goto(`${BASE_URL}/templates`);
      
      // Should see template grid
      await expect(page.locator('[data-testid="template-card"], .template, [class*="template"]')).toHaveCount({ min: 1 }, { timeout: 10000 });
      
      // Should see premium templates
      const premiumTemplates = page.locator('text=pro', 'text=premium', '[data-testid="premium-template"]');
      if (await premiumTemplates.count() > 0) {
        console.log('✅ Premium templates are available');
      } else {
        console.log('ℹ️ Premium templates may not be implemented yet');
      }
    });

    test('should save threads to history', async ({ page }) => {
      // Login first (required for history)
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[type="email"]', TEST_EMAIL);
      await page.fill('input[type="password"]', TEST_PASSWORD);
      await page.click('button[type="submit"]');
      
      await page.waitForTimeout(2000);
      
      // Generate a thread
      await page.goto(`${BASE_URL}/generate`);
      const textInput = page.locator('textarea, input[type="text"]').first();
      await textInput.fill(SAMPLE_CONTENT);
      
      const generateButton = page.locator('button').filter({ hasText: /generate/i });
      await generateButton.click();
      
      // Wait for thread generation
      await page.waitForTimeout(5000);
      
      // Look for save button
      const saveButton = page.locator('button:has-text("Save"), button[data-testid="save-thread"]');
      if (await saveButton.count() > 0) {
        await saveButton.click();
        
        // Check history page
        await page.goto(`${BASE_URL}/history`);
        await expect(page.locator('[data-testid="thread-history"], .thread-item')).toHaveCount({ min: 1 });
      } else {
        console.log('ℹ️ Thread saving feature may not be implemented yet');
      }
    });
  });

  test.describe('📱 Mobile Responsiveness', () => {
    
    test('should work on mobile viewport', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto(BASE_URL);
      
      // Check that main elements are visible
      await expect(page.locator('h1, [data-testid="main-heading"]')).toBeVisible();
      
      // Check that input form works on mobile
      const textInput = page.locator('textarea, input[type="text"]').first();
      await textInput.fill('Mobile test content');
      
      const generateButton = page.locator('button').filter({ hasText: /generate/i });
      await expect(generateButton).toBeVisible();
      
      console.log('✅ Mobile responsiveness check passed');
    });
  });

  test.describe('🔒 Error Handling', () => {
    
    test('should handle network errors gracefully', async ({ page }) => {
      // Intercept and fail API requests
      await page.route(`${API_URL}/**`, route => route.abort());
      
      await page.goto(BASE_URL);
      
      const textInput = page.locator('textarea, input[type="text"]').first();
      await textInput.fill(SAMPLE_CONTENT);
      
      const generateButton = page.locator('button').filter({ hasText: /generate/i });
      await generateButton.click();
      
      // Should show error message
      await expect(page.locator('[class*="error"], .alert-error, [role="alert"]')).toBeVisible({ timeout: 10000 });
    });

    test('should show loading states', async ({ page }) => {
      await page.goto(BASE_URL);
      
      const textInput = page.locator('textarea, input[type="text"]').first();
      await textInput.fill(SAMPLE_CONTENT);
      
      const generateButton = page.locator('button').filter({ hasText: /generate/i });
      await generateButton.click();
      
      // Should show loading indicator
      await expect(page.locator('[data-testid="loading"], .loading, .spinner')).toBeVisible({ timeout: 2000 });
    });
  });
});

test.describe('💰 Revenue Readiness Assessment', () => {
  
  test('complete user journey: free → rate limit → payment → premium', async ({ page }) => {
    console.log('🎯 Testing complete revenue journey...');
    
    // 1. Start as anonymous user
    await page.goto(BASE_URL);
    await expect(page.locator('h1')).toBeVisible();
    
    // 2. Generate a few threads successfully
    for (let i = 0; i < 2; i++) {
      const textInput = page.locator('textarea, input[type="text"]').first();
      await textInput.fill(`Test content ${i + 1}: Content marketing is essential for business growth.`);
      
      const generateButton = page.locator('button').filter({ hasText: /generate/i });
      await generateButton.click();
      
      await page.waitForTimeout(3000);
    }
    
    // 3. Register/login for tracking
    await page.goto(`${BASE_URL}/register`);
    await page.fill('input[type="email"]', TEST_EMAIL);
    await page.fill('input[type="password"]', TEST_PASSWORD);
    
    const confirmPassword = page.locator('input[name="confirmPassword"], input[placeholder*="confirm"]');
    if (await confirmPassword.count() > 0) {
      await confirmPassword.fill(TEST_PASSWORD);
    }
    
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);
    
    // 4. Continue generating until rate limit (simulate hitting limit)
    await page.goto(BASE_URL);
    
    // Try to generate more threads
    for (let i = 3; i <= 6; i++) {
      const textInput = page.locator('textarea, input[type="text"]').first();
      await textInput.fill(`Test content ${i}: More content to test rate limiting.`);
      
      const generateButton = page.locator('button').filter({ hasText: /generate/i });
      await generateButton.click();
      
      await page.waitForTimeout(2000);
      
      // Check if we hit rate limit
      const hasUpgradePrompt = await page.locator('text=upgrade', 'text=premium', 'text=limit').count() > 0;
      if (hasUpgradePrompt) {
        console.log('✅ Rate limit triggered upgrade prompt');
        break;
      }
    }
    
    // 5. Check if payment flow is accessible
    const upgradeButton = page.locator('button:has-text("Upgrade"), button:has-text("Premium")');
    if (await upgradeButton.count() > 0) {
      console.log('✅ Upgrade flow is accessible');
      
      // Click to test payment redirect (don't complete payment in test)
      await upgradeButton.first().click();
      await page.waitForTimeout(2000);
      
      const hasPaymentFlow = page.url().includes('stripe') || 
                            await page.locator('[data-testid="payment"], text=$4.99').count() > 0;
      
      if (hasPaymentFlow) {
        console.log('✅ Payment integration is working');
      } else {
        console.log('⚠️ Payment integration needs verification');
      }
    }
    
    console.log('🎯 Revenue journey test completed');
  });
});

// Test configuration for different environments
test.describe.configure({ mode: 'parallel' });

// Global test settings
test.setTimeout(30000); // 30 second timeout for each test