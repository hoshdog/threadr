'use client';

import React, { useState } from 'react';
import { ThreadGenerator } from '@/components/thread/ThreadGenerator';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { UpgradeModal } from '@/components/ui';

// Auth Modal Component
const AuthModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  mode: 'login' | 'register';
  onModeChange: (mode: 'login' | 'register') => void;
}> = ({ isOpen, onClose, mode, onModeChange }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-x-black/75 flex items-center justify-center p-4 z-50">
      <div className="bg-x-dark rounded-2xl border border-x-border p-8 max-w-md w-full">
        <div className="text-center space-y-6">
          <div>
            <h3 className="text-2xl font-bold text-white mb-2">
              {mode === 'login' ? 'Welcome Back' : 'Create Account'}
            </h3>
            <p className="text-gray-300">
              {mode === 'login' 
                ? 'Sign in to access your saved threads and premium features.'
                : 'Join thousands of creators using Threadr to grow their audience.'
              }
            </p>
          </div>

          <form className="space-y-4">
            <input
              type="email"
              placeholder="Email address"
              className="w-full px-4 py-3 rounded-lg bg-x-black border border-x-border text-white placeholder-x-gray focus:outline-none focus:ring-2 focus:ring-x-blue"
            />
            <input
              type="password"
              placeholder="Password"
              className="w-full px-4 py-3 rounded-lg bg-x-black border border-x-border text-white placeholder-x-gray focus:outline-none focus:ring-2 focus:ring-x-blue"
            />
            {mode === 'register' && (
              <input
                type="password"
                placeholder="Confirm password"
                className="w-full px-4 py-3 rounded-lg bg-x-black border border-x-border text-white placeholder-x-gray focus:outline-none focus:ring-2 focus:ring-x-blue"
              />
            )}
          </form>

          <div className="flex space-x-3">
            <Button
              variant="secondary"
              onClick={onClose}
              className="flex-1 btn-twitter-secondary text-x-gray border-x-border hover:text-white hover:border-x-gray"
            >
              Cancel
            </Button>
            <Button
              onClick={() => {
                // Implement auth logic
                console.log(`${mode} clicked`);
                onClose();
              }}
              className="flex-1 btn-twitter-primary bg-x-blue hover:bg-x-blue-hover text-white font-semibold"
            >
              {mode === 'login' ? 'Sign In' : 'Create Account'}
            </Button>
          </div>

          <div className="text-center">
            <button
              onClick={() => onModeChange(mode === 'login' ? 'register' : 'login')}
              className="text-blue-400 hover:text-blue-300 text-sm"
            >
              {mode === 'login' 
                ? "Don't have an account? Sign up"
                : "Already have an account? Sign in"
              }
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default function GeneratePage() {
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');

  const handleUpgrade = () => {
    setShowPaymentModal(true);
  };

  const handleLogin = () => {
    setShowAuthModal(true);
  };

  return (
    <div className="min-h-screen bg-x-black text-white">
      {/* Header */}
      <div className="border-b border-x-border bg-x-dark/95 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">T</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Thread Generator</h1>
                <p className="text-x-gray text-sm hidden sm:block">
                  Convert articles and content into engaging Twitter threads
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button
                variant="secondary"
                onClick={handleLogin}
                className="btn-twitter-secondary text-x-gray border-x-border hover:text-white hover:border-x-gray"
              >
                Sign In
              </Button>
              <Button
                onClick={handleUpgrade}
                className="btn-twitter-primary bg-gradient-to-r from-x-blue to-purple-600 hover:from-x-blue-hover hover:to-purple-700 text-white font-semibold"
              >
                Upgrade
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-white mb-4">
            Transform Content into 
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400"> Viral Threads</span>
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Paste any URL or content and our AI will create an engaging Twitter thread that captures your audience's attention.
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <Card className="bg-x-dark border-x-border p-6 text-center">
            <div className="w-12 h-12 mx-auto mb-4 bg-blue-600/20 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">URL Support</h3>
            <p className="text-x-gray text-sm">
              Works with Medium, Dev.to, Substack, and 15+ other platforms
            </p>
          </Card>

          <Card className="bg-x-dark border-x-border p-6 text-center">
            <div className="w-12 h-12 mx-auto mb-4 bg-purple-600/20 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a1 1 0 01-1-1V9a1 1 0 011-1h1a2 2 0 100-4H4a1 1 0 01-1-1V4a1 1 0 011-1h3a1 1 0 011 1v1a2 2 0 104 0V4z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">AI-Powered</h3>
            <p className="text-x-gray text-sm">
              Advanced AI that understands context and creates engaging content
            </p>
          </Card>

          <Card className="bg-x-dark border-x-border p-6 text-center">
            <div className="w-12 h-12 mx-auto mb-4 bg-green-600/20 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Full Control</h3>
            <p className="text-x-gray text-sm">
              Edit every tweet, check character counts, and preview before posting
            </p>
          </Card>
        </div>

        {/* Thread Generator */}
        <ThreadGenerator
          onUpgrade={handleUpgrade}
          onLogin={handleLogin}
        />
      </div>

      {/* Modals */}
      <UpgradeModal
        isOpen={showPaymentModal}
        onClose={() => setShowPaymentModal(false)}
        trigger="premium_feature"
        title="Upgrade to Premium"
        description="Get unlimited thread generation and access to all premium features."
      />
      
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        mode={authMode}
        onModeChange={setAuthMode}
      />
    </div>
  );
}