import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Define routes that require authentication
const protectedRoutes = [
  '/generate',
  '/templates',
  '/history',
  '/analytics',
  '/account',
  '/profile',
  '/settings',
  '/threads',
  '/team',
  '/billing',
];

// Define routes that require premium access
const premiumRoutes = [
  '/analytics',
  '/team',
  '/templates/premium',
];

// Define public routes (accessible without authentication)
const publicRoutes = [
  '/',
  '/login',
  '/register',
  '/forgot-password',
  '/reset-password',
  '/pricing',
  '/about',
  '/terms',
  '/privacy',
  '/api/health',
];

// Helper function to check if token is expired
function isTokenExpired(token: string): boolean {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return true;
    
    const payload = JSON.parse(atob(parts[1] || ''));
    const currentTime = Date.now() / 1000;
    return payload.exp < currentTime;
  } catch {
    return true;
  }
}

// Helper function to extract user info from token
function getUserFromToken(token: string): { isPremium: boolean } | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    
    const payload = JSON.parse(atob(parts[1] || ''));
    return {
      isPremium: payload.is_premium || false,
    };
  } catch {
    return null;
  }
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Skip middleware for static files and API routes (except auth-related ones)
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api/') ||
    pathname.includes('.') // Static files (images, css, js, etc.)
  ) {
    return NextResponse.next();
  }
  
  // Get token from cookies or localStorage (we'll check both)
  const tokenFromCookie = request.cookies.get('threadr_token')?.value;
  
  // Check if the current route is public
  const isPublicRoute = publicRoutes.some(route => {
    if (route === '/') return pathname === '/';
    return pathname.startsWith(route);
  });
  
  // Check if the current route requires authentication
  const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route));
  
  // Check if the current route requires premium
  const isPremiumRoute = premiumRoutes.some(route => pathname.startsWith(route));
  
  // If it's a public route, allow access
  if (isPublicRoute && !isProtectedRoute) {
    return NextResponse.next();
  }
  
  // If no token is found for protected routes
  if (!tokenFromCookie && isProtectedRoute) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }
  
  // If token exists, validate it
  if (tokenFromCookie) {
    // Check if token is expired
    if (isTokenExpired(tokenFromCookie)) {
      // Token is expired, redirect to login
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('redirect', pathname);
      
      // Clear the expired token
      const response = NextResponse.redirect(loginUrl);
      response.cookies.delete('threadr_token');
      return response;
    }
    
    // For premium routes, check if user has premium access
    if (isPremiumRoute) {
      const userInfo = getUserFromToken(tokenFromCookie);
      if (!userInfo?.isPremium) {
        const upgradeUrl = new URL('/upgrade', request.url);
        upgradeUrl.searchParams.set('redirect', pathname);
        return NextResponse.redirect(upgradeUrl);
      }
    }
    
    // If user is authenticated and trying to access login/register, redirect to dashboard
    if (pathname === '/login' || pathname === '/register') {
      return NextResponse.redirect(new URL('/', request.url));
    }
  }
  
  // Add security headers
  const response = NextResponse.next();
  
  // Security headers
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('X-XSS-Protection', '1; mode=block');
  
  // CSP header for enhanced security
  const cspHeader = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com https://cdn.jsdelivr.net",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data: https: blob:",
    "connect-src 'self' https://api.stripe.com https://api.openai.com",
    "frame-src https://js.stripe.com",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
  ].join('; ');
  
  response.headers.set('Content-Security-Policy', cspHeader);
  
  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};