'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { useAuth } from '@/hooks/useAuth';
import Logo from '@/components/ui/Logo';

export default function Home() {
  const [url, setUrl] = useState('');
  const { isAuthenticated, user, isLoading } = useAuth();
  const router = useRouter();

  // Redirect authenticated users to the dashboard
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/generate');
    }
  }, [isAuthenticated, isLoading, router]);

  const handleGenerate = () => {
    console.log('Generating thread for:', url);
    // This would connect to the thread generation API
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
    <div className='min-h-screen bg-gradient-to-br from-background to-muted'>
      <div className='container mx-auto px-4 py-16'>
        {/* Header */}
        <div className='text-center mb-16'>
          <div className="flex items-center justify-center mb-6">
            <Logo variant="black" size="xl" />
          </div>
          <p className='text-xl text-muted-foreground max-w-2xl mx-auto mb-8'>
            Transform your blog articles and content into engaging Twitter threads with AI-powered thread generation.
          </p>
          
          {/* Auth Status */}
          {isAuthenticated ? (
            <div className='text-sm text-muted-foreground mb-8'>
              Welcome back, {user?.email}! {user?.isPremium ? '✨ Premium' : '🆓 Free'}
            </div>
          ) : (
            <div className='text-sm text-muted-foreground mb-8'>
              Not signed in • <Link href='/login' className='text-accent hover:underline'>Sign In</Link>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className='max-w-4xl mx-auto'>
          <Card className='mb-8'>
            <CardHeader>
              <CardTitle>Generate Twitter Thread</CardTitle>
              <CardDescription>
                Enter a URL or paste your content to convert it into a Twitter thread
              </CardDescription>
            </CardHeader>
            <CardContent className='space-y-4'>
              <div className='flex gap-4'>
                <Input
                  placeholder='https://example.com/article or paste your content...'
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className='flex-1'
                />
                <Button onClick={handleGenerate} disabled={!url}>
                  Generate Thread
                </Button>
              </div>
              
              <div className='grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-muted-foreground'>
                <div className='text-center'>
                  <div className='font-semibold text-foreground'>15+ Domains</div>
                  <div>Medium, Dev.to, Substack & more</div>
                </div>
                <div className='text-center'>
                  <div className='font-semibold text-foreground'>AI Powered</div>
                  <div>GPT-3.5 Turbo optimization</div>
                </div>
                <div className='text-center'>
                  <div className='font-semibold text-foreground'>Inline Editing</div>
                  <div>Refine each tweet individually</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Features Grid */}
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
            <Card>
              <CardHeader>
                <CardTitle className='text-lg'>Smart Content Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <p className='text-sm text-muted-foreground'>
                  Our AI analyzes your content structure and creates engaging, coherent threads that maintain your original message.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className='text-lg'>Character Optimization</CardTitle>
              </CardHeader>
              <CardContent>
                <p className='text-sm text-muted-foreground'>
                  Automatically splits content into tweet-sized chunks while preserving context and readability.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className='text-lg'>Copy & Share</CardTitle>
              </CardHeader>
              <CardContent>
                <p className='text-sm text-muted-foreground'>
                  One-click copying for individual tweets or entire threads. Perfect for scheduling tools.
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Pricing */}
          <div className='mt-16 text-center'>
            <h2 className='text-3xl font-bold mb-8'>Simple, Transparent Pricing</h2>
            <div className='grid grid-cols-1 md:grid-cols-2 gap-8 max-w-2xl mx-auto'>
              <Card>
                <CardHeader>
                  <CardTitle>Free</CardTitle>
                  <CardDescription>Perfect for getting started</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className='text-3xl font-bold mb-4'>$0</div>
                  <ul className='text-sm space-y-2 text-left'>
                    <li>• 5 threads per day</li>
                    <li>• 20 threads per month</li>
                    <li>• All supported domains</li>
                    <li>• Basic thread editing</li>
                  </ul>
                </CardContent>
              </Card>

              <Card className='border-accent'>
                <CardHeader>
                  <CardTitle>Premium</CardTitle>
                  <CardDescription>For power users</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className='text-3xl font-bold mb-4'>$4.99</div>
                  <div className='text-sm text-muted-foreground mb-4'>per 30 days</div>
                  <ul className='text-sm space-y-2 text-left'>
                    <li>• Unlimited threads</li>
                    <li>• Priority processing</li>
                    <li>• Advanced templates</li>
                    <li>• Thread analytics</li>
                  </ul>
                  <Button className='w-full mt-4'>Upgrade Now</Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
