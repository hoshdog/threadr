'use client';

import { Suspense } from 'react';
import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui';
import { usePremiumStatus } from '@/hooks/api/useSubscription';

function PaymentSuccessContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const templateId = searchParams.get('template');
  const [isVerifying, setIsVerifying] = useState(true);
  const { data: premiumStatus, refetch: refetchPremiumStatus } = usePremiumStatus();

  useEffect(() => {
    // Verify premium access after payment
    const verifyPremiumAccess = async () => {
      try {
        // Wait a moment for webhook processing
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Refetch premium status
        await refetchPremiumStatus();
        
        setIsVerifying(false);
      } catch (error) {
        console.error('Error verifying premium access:', error);
        setIsVerifying(false);
      }
    };

    verifyPremiumAccess();
  }, [refetchPremiumStatus]);

  const handleContinue = () => {
    if (templateId) {
      // If user was trying to access a specific template, redirect back to templates
      router.push('/templates');
    } else {
      // Otherwise, redirect to dashboard
      router.push('/');
    }
  };

  const handleGoToTemplates = () => {
    router.push('/templates');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
        {isVerifying ? (
          // Verifying state
          <>
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              Verifying Payment...
            </h1>
            <p className="text-gray-600 mb-6">
              Please wait while we confirm your premium access.
            </p>
          </>
        ) : premiumStatus?.has_premium ? (
          // Success state
          <>
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              Payment Successful!
            </h1>
            <p className="text-gray-600 mb-6">
              Welcome to Threadr Premium! You now have unlimited access to all features including premium templates and unlimited thread generations.
            </p>
            
            {/* Premium Features List */}
            <div className="bg-green-50 rounded-lg p-4 mb-6 text-left">
              <h3 className="font-semibold text-green-900 mb-2">You now have access to:</h3>
              <ul className="space-y-1 text-sm text-green-800">
                <li className="flex items-center">
                  <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Unlimited thread generations
                </li>
                <li className="flex items-center">
                  <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Access to premium templates
                </li>
                <li className="flex items-center">
                  <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Priority customer support
                </li>
                <li className="flex items-center">
                  <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Advanced analytics and insights
                </li>
              </ul>
            </div>

            <div className="flex space-x-3">
              {templateId && (
                <Button
                  variant="secondary"
                  onClick={handleGoToTemplates}
                  className="flex-1"
                >
                  Browse Templates
                </Button>
              )}
              <Button
                variant="primary"
                onClick={handleContinue}
                className="flex-1 bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700"
              >
                Start Creating
              </Button>
            </div>
          </>
        ) : (
          // Error state
          <>
            <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              Payment Processing
            </h1>
            <p className="text-gray-600 mb-6">
              Your payment was received, but premium access is still being processed. Please check back in a few minutes or contact support if the issue persists.
            </p>
            
            <div className="flex space-x-3">
              <Button
                variant="secondary"
                onClick={() => refetchPremiumStatus()}
                className="flex-1"
              >
                Check Again
              </Button>
              <Button
                variant="primary"
                onClick={handleContinue}
                className="flex-1"
              >
                Continue
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default function PaymentSuccessPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Loading...</h1>
        </div>
      </div>
    }>
      <PaymentSuccessContent />
    </Suspense>
  );
}