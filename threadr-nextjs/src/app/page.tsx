'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { useAuth } from '@/hooks/useAuth';
import { useThreadGeneration } from '@/lib/api/hooks/useThreadGeneration';
import Logo from '@/components/ui/Logo';
import { PricingSection } from '@/components/pricing';

export default function Home() {
  const [url, setUrl] = useState('');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const { isAuthenticated, user, isLoading } = useAuth();
  const { generateThread, loading: threadLoading, error: threadError, tweets, clearError, copyTweet, copyAllTweets, updateTweet } = useThreadGeneration();
  const router = useRouter();

  // Redirect authenticated users to the dashboard
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/generate');
    }
  }, [isAuthenticated, isLoading, router]);

  // Handle dark mode toggle
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const handleGenerate = async () => {
    if (!url.trim()) return;
    
    clearError();
    
    try {
      await generateThread({
        content: url.trim(),
        // You can add more options here like:
        // tone: 'professional',
        // length: 'medium',
        // include_cta: true
      });
    } catch (error) {
      console.error('Thread generation failed:', error);
    }
  };

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-muted">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render if authenticated (will redirect)
  if (isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-slate-900">
      {/* Navigation Header */}
      <nav className="w-full py-6 px-4 border-b border-gray-100 dark:border-gray-800">
        <div className="container mx-auto flex items-center justify-between">
          <Logo variant={isDarkMode ? "white" : "black"} size="lg" showText clickable />
          <div className="flex items-center space-x-4">
            {/* Dark Mode Toggle */}
            <Button 
              onClick={() => setIsDarkMode(!isDarkMode)} 
              variant="ghost" 
              size="md"
              className="p-2"
            >
              {isDarkMode ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              )}
            </Button>
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">
                  {user?.email} {user?.isPremium ? '✨' : ''}
                </span>
                <Button 
                  onClick={() => router.push('/generate')} 
                  size="md"
                  variant="primary"
                >
                  Dashboard
                </Button>
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <Link href="/login">
                  <Button variant="ghost" size="md">Sign In</Button>
                </Link>
                <Link href="/register">
                  <Button variant="primary" size="md">Get Started Free</Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 pt-16 pb-24">
        {/* Hero Section */}
        <div className="text-center mb-20">
          <div className="max-w-4xl mx-auto mb-8">
            <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              Transform Articles into 
              <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent block mt-2">
                Viral Twitter Threads
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto mb-12 leading-relaxed">
              Convert blog posts, articles, and long-form content into engaging Twitter threads in seconds. 
              AI-powered, professionally formatted, ready to post.
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
            {!isAuthenticated && (
              <>
                <Button 
                  size="xl" 
                  variant="primary"
                  onClick={() => router.push('/register')}
                  className="w-full sm:w-auto"
                >
                  Start Creating Threads Free
                </Button>
                <Button 
                  size="xl" 
                  variant="outline"
                  onClick={() => router.push('/login')}
                  className="w-full sm:w-auto"
                >
                  See How It Works
                </Button>
              </>
            )}
          </div>

          {/* Social Proof */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-8 text-sm text-gray-500 mb-16">
            <div className="flex items-center space-x-2">
              <div className="flex -space-x-1">
                <div className="w-8 h-8 bg-blue-500 rounded-full border-2 border-white"></div>
                <div className="w-8 h-8 bg-green-500 rounded-full border-2 border-white"></div>
                <div className="w-8 h-8 bg-purple-500 rounded-full border-2 border-white"></div>
              </div>
              <span>10,000+ threads created</span>
            </div>
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-yellow-400 fill-current" viewBox="0 0 20 20">
                <path d="M10 1l2.928 6.072L19 8.122l-4.5 4.386L15.656 19 10 15.888 4.344 19 5.5 12.508 1 8.122l6.072-1.05z"/>
              </svg>
              <span>4.9/5 user rating</span>
            </div>
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>Average 300% engagement boost</span>
            </div>
          </div>
        </div>

        {/* Demo Section */}
        {!isAuthenticated && (
          <div className="max-w-5xl mx-auto mb-20">
            <Card className="p-8 shadow-xl border-0 bg-white/80 backdrop-blur-sm">
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-3">Try It Now - No Sign Up Required</h3>
                <p className="text-gray-600">Paste any article URL and see the magic happen</p>
              </div>
              <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <Input
                  placeholder='https://medium.com/@author/article or paste your content...'
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="flex-1 h-14 text-lg"
                />
                <Button 
                  onClick={handleGenerate} 
                  disabled={!url.trim() || threadLoading}
                  size="lg"
                  className="w-full sm:w-auto whitespace-nowrap"
                >
                  {threadLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Generating...
                    </>
                  ) : (
                    'Generate Thread Free'
                  )}
                </Button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
                <div className="p-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0 9c0-9 0-9 0-9m9 0a9 9 0 00-9-9" />
                    </svg>
                  </div>
                  <div className="font-semibold text-gray-900 mb-2">15+ Domains Supported</div>
                  <div className="text-gray-600 text-sm">Medium, Dev.to, Substack, personal blogs & more</div>
                </div>
                <div className="p-4">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <div className="font-semibold text-gray-900 mb-2">AI-Powered Processing</div>
                  <div className="text-gray-600 text-sm">GPT-4 optimization for maximum engagement</div>
                </div>
                <div className="p-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </div>
                  <div className="font-semibold text-gray-900 mb-2">Instant Editing</div>
                  <div className="text-gray-600 text-sm">Refine each tweet with inline WYSIWYG editor</div>
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Generated Thread Results */}
        {threadError && (
          <div className="max-w-5xl mx-auto mb-12">
            <Card className="p-6 border-red-200 bg-red-50 dark:bg-red-900/20 dark:border-red-700">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-red-800 dark:text-red-200 font-semibold mb-2">Thread Generation Failed</h3>
                  <p className="text-red-600 dark:text-red-300">{threadError}</p>
                </div>
                <Button onClick={clearError} variant="ghost" size="sm">
                  ✕
                </Button>
              </div>
            </Card>
          </div>
        )}

        {tweets.length > 0 && (
          <div className="max-w-5xl mx-auto mb-20">
            <div className="text-center mb-8">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">Your Generated Thread</h3>
              <p className="text-gray-600 dark:text-gray-300">Edit, copy, and share your Twitter thread</p>
            </div>
            
            <div className="space-y-4">
              {tweets.map((tweet, index) => (
                <Card key={tweet.id} className="p-6 shadow-lg">
                  <div className="flex items-start justify-between mb-4">
                    <span className="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-3 py-1 rounded-full text-sm font-medium">
                      Tweet {index + 1}/{tweets.length}
                    </span>
                    <span className={`text-sm ${tweet.characterCount > 280 ? 'text-red-500' : 'text-gray-500'}`}>
                      {tweet.characterCount}/280
                    </span>
                  </div>
                  
                  <div className="mb-4">
                    <textarea 
                      value={tweet.content}
                      onChange={(e) => updateTweet(index, e.target.value)}
                      className="w-full p-3 border rounded-lg resize-none dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                      rows={Math.ceil(tweet.content.length / 60) || 3}
                    />
                  </div>
                  
                  <Button 
                    onClick={() => copyTweet(index)}
                    variant="outline" 
                    size="sm"
                    className="w-full sm:w-auto"
                  >
                    Copy Tweet
                  </Button>
                </Card>
              ))}
              
              <div className="text-center pt-4">
                <Button 
                  onClick={copyAllTweets}
                  variant="primary"
                  size="lg"
                  className="w-full sm:w-auto"
                >
                  Copy Entire Thread
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Features Grid */}
        <div className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Everything You Need to Go Viral</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">Professional features that help content creators, marketers, and businesses amplify their reach</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="p-6 h-full border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Smart Content Analysis</h3>
              <p className="text-gray-600 leading-relaxed">
                Advanced AI analyzes your content structure, key points, and narrative flow to create compelling threads that maintain your original voice and message.
              </p>
            </Card>

            <Card className="p-6 h-full border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Engagement Optimization</h3>
              <p className="text-gray-600 leading-relaxed">
                Automatically optimizes for maximum engagement with hooks, call-to-actions, and strategic formatting that drives retweets and replies.
              </p>
            </Card>

            <Card className="p-6 h-full border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">One-Click Publishing</h3>
              <p className="text-gray-600 leading-relaxed">
                Copy individual tweets or entire threads with one click. Perfect for scheduling tools like Buffer, Hootsuite, or direct posting to Twitter.
              </p>
            </Card>

            <Card className="p-6 h-full border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <div className="w-12 h-12 bg-gradient-to-r from-amber-500 to-orange-600 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Performance Analytics</h3>
              <p className="text-gray-600 leading-relaxed">
                Track your thread performance, engagement rates, and optimize your content strategy with detailed analytics and insights.
              </p>
            </Card>

            <Card className="p-6 h-full border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <div className="w-12 h-12 bg-gradient-to-r from-red-500 to-pink-600 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Template Library</h3>
              <p className="text-gray-600 leading-relaxed">
                Choose from dozens of professionally crafted thread templates for different industries, topics, and engagement styles.
              </p>
            </Card>

            <Card className="p-6 h-full border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <div className="w-12 h-12 bg-gradient-to-r from-indigo-500 to-blue-600 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Team Collaboration</h3>
              <p className="text-gray-600 leading-relaxed">
                Work together with your team on thread creation, review workflows, and brand consistency with advanced collaboration tools.
              </p>
            </Card>
          </div>
        </div>

        {/* Pricing */}
        <div className="mt-16">
          <PricingSection showHeader={true} showBillingToggle={true} />
        </div>
      </div>
    </div>
  );
}
