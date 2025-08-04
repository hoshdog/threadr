import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { ReactQueryProvider } from '@/lib/providers';
import { AuthProvider } from '@/contexts/auth';
import { cn } from '@/lib/utils';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: 'Threadr - Convert Articles to Twitter Threads',
  description: 'Transform your blog articles and content into engaging Twitter threads with AI-powered thread generation.',
  keywords: 'twitter, threads, content, blog, articles, social media, ai, automation',
  authors: [{ name: 'Threadr Team' }],
  creator: 'Threadr',
  publisher: 'Threadr',
  metadataBase: new URL(process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000'),
  icons: {
    icon: [
      { url: '/favicon.ico' },
      { url: '/favicon.png', type: 'image/png' },
    ],
    shortcut: '/favicon.ico',
    apple: '/threadrLogo_Black_Cropped.PNG',
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: '/',
    title: 'Threadr - Convert Articles to Twitter Threads',
    description: 'Transform your blog articles and content into engaging Twitter threads with AI-powered thread generation.',
    siteName: 'Threadr',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Threadr - Convert Articles to Twitter Threads',
    description: 'Transform your blog articles and content into engaging Twitter threads with AI-powered thread generation.',
    creator: '@threadr',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang='en' suppressHydrationWarning>
      <body
        className={cn(
          'min-h-screen bg-background font-sans antialiased',
          inter.variable
        )}
      >
        <ReactQueryProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </ReactQueryProvider>
      </body>
    </html>
  );
}
