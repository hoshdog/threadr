# JWT Authentication System Implementation

## Overview

This implementation provides a complete, production-ready JWT authentication system for the Threadr Next.js application with the following features:

- **JWT Token Management**: Access tokens (30 min) + Refresh tokens (7 days)
- **Automatic Token Refresh**: Proactive refresh before expiration
- **Persistent Authentication**: Cookies + localStorage fallback
- **Protected Routes**: Middleware and component-level protection
- **Security Best Practices**: CSP headers, secure cookies, token validation

## Files Created/Modified

### Core Authentication Context
- `src/contexts/auth.tsx` - Main authentication context provider
- `src/components/auth/ProtectedRoute.tsx` - Component-level route protection
- `src/components/auth/AuthLayout.tsx` - Layout component with auth checks
- `src/components/auth/index.ts` - Easy imports

### Route Protection
- `src/middleware.ts` - Next.js middleware for route protection
- `src/hooks/useAuthGuard.ts` - Hook for programmatic auth guards

### API Integration
- Updated `src/lib/api/auth.ts` - Auth API endpoints
- Enhanced `src/lib/api/client.ts` - Automatic token refresh

### Example Pages
- `src/app/login/page.tsx` - Login page
- `src/app/register/page.tsx` - Registration page
- `src/app/dashboard/page.tsx` - Protected dashboard
- Updated `src/app/layout.tsx` - Added AuthProvider

## Key Features

### 1. Automatic Token Refresh
```typescript
// Tokens are automatically refreshed 5 minutes before expiry
// Handles concurrent requests during refresh
// Falls back to login redirect if refresh fails
```

### 2. Multiple Storage Methods
```typescript
// Primary: HTTP-only cookies (secure)
// Fallback: localStorage (client access)
// Automatic cleanup on logout
```

### 3. Route Protection Levels
```typescript
// Public routes: /, /login, /register, /pricing
// Protected routes: /dashboard, /profile, /settings
// Premium routes: /analytics, /team, /templates/premium
```

### 4. Security Headers
```typescript
// CSP, X-Frame-Options, X-Content-Type-Options
// Referrer-Policy, X-XSS-Protection
// HTTPS-only cookies in production
```

## Usage Examples

### Basic Auth Context Usage
```tsx
import { useAuth } from '@/contexts/auth';

function MyComponent() {
  const { user, isAuthenticated, login, logout, isLoading } = useAuth();
  
  if (isLoading) return <div>Loading...</div>;
  
  return (
    <div>
      {isAuthenticated ? (
        <div>
          <p>Welcome, {user?.email}!</p>
          <button onClick={logout}>Logout</button>
        </div>
      ) : (
        <button onClick={() => login({ email, password })}>Login</button>
      )}
    </div>
  );
}
```

### Protected Route Component
```tsx
import { ProtectedRoute } from '@/components/auth';

function MyProtectedPage() {
  return (
    <ProtectedRoute requireAuth={true} requirePremium={false}>
      <div>This content requires authentication</div>
    </ProtectedRoute>
  );
}
```

### Auth Layout Wrapper
```tsx
import { AuthLayout } from '@/components/auth';

export default function DashboardPage() {
  return (
    <AuthLayout requireAuth={true}>
      <div>Protected dashboard content</div>
    </AuthLayout>
  );
}
```

### Auth Guard Hook
```tsx
import { useAuthGuard } from '@/hooks/useAuthGuard';

function MyComponent() {
  const { isAuthorized, hasPremium, isLoading } = useAuthGuard({
    requireAuth: true,
    requirePremium: true,
  });
  
  if (!isAuthorized) return null;
  
  return <div>Premium content</div>;
}
```

## Token Management

### Token Structure
```typescript
interface TokenResponse {
  access_token: string;    // JWT with 30min expiry
  token_type: "bearer";
  expires_in: number;      // seconds until expiry
  refresh_token: string;   // 7 day expiry
  user: UserResponse;      // user data
}
```

### Automatic Refresh Logic
1. **Proactive Refresh**: Tokens refresh 5 minutes before expiry
2. **Concurrent Request Handling**: Queue requests during refresh
3. **Retry on 401**: Automatic retry with new token
4. **Fallback to Login**: Redirect if refresh fails

### Storage Strategy
1. **Cookies**: Primary storage (HTTP-only in production)
2. **LocalStorage**: Fallback for client-side access
3. **Memory**: Runtime caching for performance
4. **Cleanup**: All storage cleared on logout

## Security Considerations

### Token Security
- Access tokens expire in 30 minutes
- Refresh tokens expire in 7 days
- Automatic cleanup on logout
- Secure, HTTP-only cookies in production

### Route Protection
- Middleware validates tokens server-side
- Component guards for client-side protection
- Premium feature gating
- Redirect with return path preservation

### Error Handling
- Graceful degradation on auth failures
- User-friendly error messages
- Automatic retry with exponential backoff
- Secure error logging (no token exposure)

## Environment Variables

```env
NEXT_PUBLIC_API_URL=https://api.threadr.app
NEXT_PUBLIC_FRONTEND_URL=https://threadr.app
```

## Backend Integration

The system expects these endpoints:

```typescript
POST /api/auth/login          // Login user
POST /api/auth/register       // Register user
POST /api/auth/refresh        // Refresh tokens
POST /api/auth/logout         // Logout user
GET  /api/auth/me            // Get user profile
PUT  /api/auth/profile       // Update profile
```

## Testing

### Test Authentication Flow
1. Visit `/register` to create account
2. Login redirects to `/dashboard`
3. Try accessing protected routes
4. Test token refresh (wait 25+ minutes)
5. Test logout functionality

### Test Route Protection
1. Access `/dashboard` without login → redirects to `/login`
2. Access premium route without premium → redirects to `/upgrade`
3. Login and access same routes → works correctly

## Production Checklist

- [ ] Set secure environment variables
- [ ] Configure HTTPS for cookies
- [ ] Set up CSP headers
- [ ] Test token refresh flow
- [ ] Verify middleware protection
- [ ] Test error scenarios
- [ ] Monitor auth metrics

## Security Best Practices

1. **Never store tokens in localStorage in production** (use cookies)
2. **Always use HTTPS** for token transmission
3. **Implement rate limiting** on auth endpoints
4. **Log security events** (failed logins, etc.)
5. **Rotate refresh tokens** on each use
6. **Validate tokens on every request**
7. **Clear all auth data on logout**

## Troubleshooting

### Common Issues

1. **Infinite redirect loops**: Check middleware route patterns
2. **Token not persisting**: Verify cookie settings
3. **Auth context not available**: Ensure AuthProvider wraps app
4. **API 401 errors**: Check token format and expiry

### Debug Mode
```typescript
// Enable request/response logging
NEXT_PUBLIC_ENABLE_AUTH_LOGGING=true
```

This will log all auth-related API calls and token operations to the console.

## Future Enhancements

1. **Multi-factor Authentication** (MFA)
2. **Social Login** (Google, GitHub, etc.)
3. **Session Management** (view/revoke active sessions)
4. **Password Strength Requirements**
5. **Account Lockout** (after failed attempts)
6. **Email Verification** workflow
7. **Password Reset** functionality

---

This implementation provides enterprise-grade authentication with security best practices and developer-friendly APIs. The modular design allows for easy customization and extension as requirements evolve.