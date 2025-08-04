'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/auth';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { apiClient } from '@/lib/api/client';

export default function AuthTestPage() {
  const {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    refreshTokens,
    isTokenValid,
    getAuthHeaders,
  } = useAuth();
  
  const [testResults, setTestResults] = useState<string[]>([]);

  const addResult = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    const formattedMessage = `[${timestamp}] ${type.toUpperCase()}: ${message}`;
    setTestResults(prev => [...prev, formattedMessage]);
  };

  const runTests = async () => {
    setTestResults([]);
    addResult('Starting authentication system tests...');

    // Test 0: API Connection Test
    try {
      addResult('Testing API connection to production backend...');
      const baseUrl = apiClient.getBaseURL();
      addResult(`Base URL: ${baseUrl}`, 'info');
      
      const healthResult = await apiClient.healthCheck();
      addResult(`API Health Check - Status: ${healthResult.status}`, 'success');
      addResult(`Backend Environment: ${(healthResult as any).environment || 'unknown'}`, 'info');
    } catch (error: any) {
      addResult(`API connection failed: ${error.message}`, 'error');
    }

    // Test 1: Check initial state
    addResult(`Initial auth state - Authenticated: ${isAuthenticated}`, 'info');
    addResult(`Current user: ${user?.email || 'None'}`, 'info');
    addResult(`Token valid: ${isTokenValid()}`, 'info');

    // Test 2: Check auth headers
    const headers = getAuthHeaders();
    addResult(`Auth headers: ${Object.keys(headers).length > 0 ? 'Present' : 'None'}`, 'info');

    // Test 3: Manual token refresh (if authenticated)
    if (isAuthenticated) {
      try {
        addResult('Testing manual token refresh...');
        await refreshTokens();
        addResult('Manual token refresh successful', 'success');
      } catch (error: any) {
        addResult(`Manual token refresh failed: ${error.message}`, 'error');
      }
    }

    // Test 4: Test with invalid credentials (will fail intentionally)
    if (!isAuthenticated) {
      try {
        addResult('Testing login with invalid credentials...');
        await login({ email: 'test@invalid.com', password: 'invalid' });
        addResult('Login unexpectedly succeeded', 'error');
      } catch (error: any) {
        addResult(`Login correctly failed: ${error.message}`, 'success');
      }
    }

    addResult('Authentication tests completed!', 'success');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Authentication System Test
          </h1>
          <p className="mt-2 text-gray-600">
            Test and debug the JWT authentication system
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Current State */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Current State</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Authenticated:</span>
                <span className={`font-medium ${isAuthenticated ? 'text-green-600' : 'text-red-600'}`}>
                  {isAuthenticated ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Loading:</span>
                <span className={`font-medium ${isLoading ? 'text-yellow-600' : 'text-gray-900'}`}>
                  {isLoading ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">User Email:</span>
                <span className="font-medium text-gray-900">
                  {user?.email || 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Premium:</span>
                <span className={`font-medium ${user?.isPremium ? 'text-yellow-600' : 'text-gray-600'}`}>
                  {user?.isPremium ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Token Valid:</span>
                <span className={`font-medium ${isTokenValid() ? 'text-green-600' : 'text-red-600'}`}>
                  {isTokenValid() ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Auth Headers:</span>
                <span className="font-medium text-gray-900">
                  {Object.keys(getAuthHeaders()).length > 0 ? 'Present' : 'None'}
                </span>
              </div>
            </div>

            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-800">
                  <strong>Error:</strong> {error}
                </p>
              </div>
            )}
          </Card>

          {/* Actions */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Actions</h2>
            <div className="space-y-4">
              <Button
                onClick={runTests}
                disabled={isLoading}
                className="w-full"
              >
                Run Authentication Tests
              </Button>
              
              <Button
                onClick={async () => {
                  setTestResults([]);
                  try {
                    addResult('Testing API connection...');
                    const baseUrl = apiClient.getBaseURL();
                    addResult(`Base URL: ${baseUrl}`, 'info');
                    
                    const healthResult = await apiClient.healthCheck();
                    addResult(`Health Status: ${healthResult.status}`, 'success');
                    addResult(`Environment: ${(healthResult as any).environment || 'unknown'}`, 'info');
                    addResult(`Version: ${(healthResult as any).version || 'unknown'}`, 'info');
                  } catch (error: any) {
                    addResult(`API connection failed: ${error.message}`, 'error');
                  }
                }}
                variant="secondary"
                className="w-full"
              >
                Test API Connection
              </Button>

              {isAuthenticated ? (
                <>
                  <Button
                    onClick={refreshTokens}
                    disabled={isLoading}
                    variant="secondary"
                    className="w-full"
                  >
                    Refresh Tokens
                  </Button>
                  <Button
                    onClick={logout}
                    disabled={isLoading}
                    variant="secondary"
                    className="w-full"
                  >
                    Logout
                  </Button>
                </>
              ) : (
                <div className="text-center text-gray-600">
                  <p>Go to <a href="/login" className="text-blue-600 hover:text-blue-500">/login</a> to authenticate</p>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Test Results */}
        {testResults.length > 0 && (
          <Card className="p-6 mt-8">
            <h2 className="text-xl font-semibold mb-4">Test Results</h2>
            <div className="bg-gray-900 text-white p-4 rounded-md font-mono text-sm max-h-96 overflow-y-auto">
              {testResults.map((result, index) => (
                <div key={index} className={`
                  ${result.includes('SUCCESS') ? 'text-green-400' : ''}
                  ${result.includes('ERROR') ? 'text-red-400' : ''}
                  ${result.includes('INFO') ? 'text-blue-400' : ''}
                `}>
                  {result}
                </div>
              ))}
            </div>
            <Button
              onClick={() => setTestResults([])}
              variant="secondary"
              size="sm"
              className="mt-4"
            >
              Clear Results
            </Button>
          </Card>
        )}

        {/* Debug Information */}
        <Card className="p-6 mt-8">
          <h2 className="text-xl font-semibold mb-4">Debug Information</h2>
          <div className="bg-gray-50 p-4 rounded-md">
            <pre className="text-sm text-gray-800 whitespace-pre-wrap">
              {JSON.stringify({
                // Authentication State
                isAuthenticated,
                isLoading,
                hasUser: !!user,
                userEmail: user?.email,
                isPremium: user?.isPremium,
                tokenValid: isTokenValid(),
                hasAuthHeaders: Object.keys(getAuthHeaders()).length > 0,
                error: error || null,
                
                // API Configuration
                apiBaseUrl: apiClient.getBaseURL(),
                environmentVars: {
                  NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
                  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
                  NEXT_PUBLIC_API_KEY: process.env.NEXT_PUBLIC_API_KEY ? 'Set' : 'Not Set',
                  NODE_ENV: process.env.NODE_ENV
                }
              }, null, 2)}
            </pre>
          </div>
        </Card>

        {/* Navigation Links */}
        <div className="mt-8 text-center space-x-4">
          <a href="/" className="text-blue-600 hover:text-blue-500">Home</a>
          <a href="/login" className="text-blue-600 hover:text-blue-500">Login</a>
          <a href="/register" className="text-blue-600 hover:text-blue-500">Register</a>
          <a href="/dashboard" className="text-blue-600 hover:text-blue-500">Dashboard</a>
        </div>
      </div>
    </div>
  );
}