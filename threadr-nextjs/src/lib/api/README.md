# Threadr API Client

A comprehensive, production-ready API client for Threadr with TypeScript support, automatic retry logic, error handling, and React Query integration.

## Features

- ✅ **TypeScript Safety**: Fully typed API responses and requests
- ✅ **Automatic Retry Logic**: Exponential backoff for failed requests
- ✅ **Authentication Handling**: Automatic token injection and refresh
- ✅ **React Query Integration**: Optimized caching and state management
- ✅ **Error Handling**: Comprehensive error types and handling
- ✅ **Production Ready**: Configurable timeouts, retries, and error boundaries

## Quick Start

### 1. Setup ReactQuery Provider

```tsx
// app/layout.tsx
import { ReactQueryProvider } from '@/lib/providers';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ReactQueryProvider>
          {children}
        </ReactQueryProvider>
      </body>
    </html>
  );
}
```

### 2. Environment Configuration

```env
# .env.local
NEXT_PUBLIC_API_BASE_URL=https://threadr-production.up.railway.app/api
```

## API Usage Examples

### Authentication

```tsx
import { useLogin, useProfile, useLogout } from '@/lib/api';

function LoginForm() {
  const login = useLogin();
  const profile = useProfile();
  const logout = useLogout();

  const handleLogin = async (email: string, password: string) => {
    try {
      await login.mutateAsync({ email, password });
      // User is automatically logged in and profile is cached
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  if (profile.data) {
    return (
      <div>
        <h1>Welcome, {profile.data.email}</h1>
        <button onClick={() => logout.mutate()}>
          Logout
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      const formData = new FormData(e.currentTarget);
      handleLogin(
        formData.get('email') as string,
        formData.get('password') as string
      );
    }}>
      <input name="email" type="email" placeholder="Email" required />
      <input name="password" type="password" placeholder="Password" required />
      <button type="submit" disabled={login.isPending}>
        {login.isPending ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
```

### Thread Generation

```tsx
import { useGenerateThread, useUsageStats } from '@/lib/api';

function ThreadGenerator() {
  const generateThread = useGenerateThread();
  const usageStats = useUsageStats();

  const handleGenerate = async (content: string) => {
    try {
      const result = await generateThread.mutateAsync({ content });
      console.log('Generated thread:', result.tweets);
    } catch (error) {
      console.error('Generation failed:', error);
    }
  };

  return (
    <div>
      <div className="usage-stats">
        <p>Daily Usage: {usageStats.data?.dailyUsage}/{usageStats.data?.dailyLimit}</p>
        <p>Monthly Usage: {usageStats.data?.monthlyUsage}/{usageStats.data?.monthlyLimit}</p>
        {!usageStats.data?.canGenerate && (
          <p className="error">Usage limit reached. Please upgrade to premium.</p>
        )}
      </div>
      
      <textarea 
        placeholder="Enter your content here..."
        onBlur={(e) => handleGenerate(e.target.value)}
        disabled={generateThread.isPending || !usageStats.data?.canGenerate}
      />
      
      {generateThread.isPending && <p>Generating thread...</p>}
      {generateThread.error && (
        <p className="error">Error: {generateThread.error.message}</p>
      )}
    </div>
  );
}
```

### Thread Management

```tsx
import { useThreads, useInfiniteThreads, useDeleteThread } from '@/lib/api';

function ThreadsList() {
  const { data: threads, isLoading, error } = useThreads(1, 10);
  const deleteThread = useDeleteThread();

  const handleDelete = async (threadId: string) => {
    if (confirm('Are you sure you want to delete this thread?')) {
      await deleteThread.mutateAsync(threadId);
    }
  };

  if (isLoading) return <div>Loading threads...</div>;
  if (error) return <div>Error loading threads: {error.message}</div>;

  return (
    <div>
      <h2>My Threads ({threads?.total})</h2>
      {threads?.data.map((thread) => (
        <div key={thread.id} className="thread-card">
          <h3>{thread.title}</h3>
          <p>{thread.tweets.length} tweets</p>
          <p>Created: {new Date(thread.createdAt).toLocaleDateString()}</p>
          <button 
            onClick={() => handleDelete(thread.id)}
            disabled={deleteThread.isPending}
          >
            Delete
          </button>
        </div>
      ))}
    </div>
  );
}

// Infinite scroll version
function InfiniteThreadsList() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useInfiniteThreads(12);

  const threads = data?.pages.flatMap(page => page.data) ?? [];

  return (
    <div>
      {threads.map((thread) => (
        <div key={thread.id}>{thread.title}</div>
      ))}
      
      {hasNextPage && (
        <button
          onClick={() => fetchNextPage()}
          disabled={isFetchingNextPage}
        >
          {isFetchingNextPage ? 'Loading more...' : 'Load More'}
        </button>
      )}
    </div>
  );
}
```

### Templates

```tsx
import { 
  useTemplates, 
  useFeaturedTemplates, 
  useGenerateFromTemplate,
  useTemplateCategories 
} from '@/lib/api';

function TemplateBrowser() {
  const { data: categories } = useTemplateCategories();
  const { data: featured } = useFeaturedTemplates();
  const { data: templates } = useTemplates({ isPremium: false });
  const generateFromTemplate = useGenerateFromTemplate();

  const handleUseTemplate = async (templateId: string, content: string) => {
    try {
      const result = await generateFromTemplate.mutateAsync({
        templateId,
        content,
      });
      console.log('Generated from template:', result.tweets);
    } catch (error) {
      console.error('Template generation failed:', error);
    }
  };

  return (
    <div>
      <h2>Featured Templates</h2>
      <div className="featured-templates">
        {featured?.map((template) => (
          <div key={template.id} className="template-card">
            <h3>{template.name}</h3>
            <p>{template.description}</p>
            <div className="tags">
              {template.tags.map(tag => (
                <span key={tag} className="tag">{tag}</span>
              ))}
            </div>
            <button 
              onClick={() => handleUseTemplate(template.id, '')}
              disabled={generateFromTemplate.isPending}
            >
              Use Template
            </button>
          </div>
        ))}
      </div>

      <h2>Categories</h2>
      <div className="categories">
        {categories?.map((category) => (
          <div key={category.id} className="category">
            <h3>{category.name}</h3>
            <p>{category.templateCount} templates</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Analytics Dashboard

```tsx
import { useDashboardAnalytics } from '@/lib/api';

function AnalyticsDashboard() {
  const {
    dashboard,
    usage,
    topThreads,
    content,
    engagement,
    isLoading,
    isError,
    error
  } = useDashboardAnalytics('month');

  if (isLoading) return <div>Loading analytics...</div>;
  if (isError) return <div>Error: {error?.message}</div>;

  return (
    <div className="analytics-dashboard">
      <h1>Analytics Dashboard</h1>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Threads</h3>
          <p>{dashboard.data?.totalThreads}</p>
        </div>
        
        <div className="stat-card">
          <h3>Total Tweets</h3>
          <p>{dashboard.data?.totalTweets}</p>
        </div>
        
        <div className="stat-card">
          <h3>Average Thread Length</h3>
          <p>{dashboard.data?.averageThreadLength} tweets</p>
        </div>

        <div className="stat-card">
          <h3>Monthly Usage</h3>
          <p>{usage.data?.total} threads</p>
        </div>
      </div>

      <div className="charts">
        <div className="chart">
          <h3>Top Performing Threads</h3>
          {topThreads.data?.map((thread) => (
            <div key={thread.threadId}>
              <span>{thread.title}</span>
              <span>Score: {thread.score}</span>
            </div>
          ))}
        </div>

        <div className="chart">
          <h3>Popular Domains</h3>
          {dashboard.data?.popularDomains.map((domain) => (
            <div key={domain.domain}>
              <span>{domain.domain}</span>
              <span>{domain.count} threads</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

## Direct API Usage (without React Query)

If you need to use the API directly without React Query hooks:

```tsx
import { authApi, threadsApi, templatesApi, analyticsApi } from '@/lib/api';

// Direct API calls
async function directApiUsage() {
  try {
    // Authentication
    const authResponse = await authApi.login({ email: 'user@example.com', password: 'password' });
    console.log('Logged in:', authResponse.user);

    // Generate thread
    const threadResponse = await threadsApi.generateThread({ 
      content: 'Your blog content here...' 
    });
    console.log('Generated tweets:', threadResponse.tweets);

    // Get templates
    const templates = await templatesApi.getTemplates({ isPremium: false });
    console.log('Available templates:', templates.templates);

    // Get analytics
    const analytics = await analyticsApi.getDashboard();
    console.log('Analytics:', analytics);

  } catch (error) {
    console.error('API Error:', error);
  }
}
```

## Error Handling

The API client provides comprehensive error handling:

```tsx
import { ApiError } from '@/types';

function handleApiError(error: unknown) {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 401:
        // Redirect to login (handled automatically by client)
        break;
      case 403:
        console.error('Access forbidden:', error.message);
        break;
      case 429:
        console.error('Rate limit exceeded:', error.message);
        break;
      case 500:
        console.error('Server error:', error.message);
        break;
      default:
        console.error('API error:', error.message);
    }
  } else {
    console.error('Unknown error:', error);
  }
}
```

## Configuration

### Retry Configuration

```tsx
import { apiClient } from '@/lib/api';

// Update retry configuration
apiClient.updateRetryConfig({
  retries: 5,
  retryDelay: 2000,
  retryCondition: (error) => {
    // Custom retry logic
    return error.response?.status >= 500;
  },
});
```

### Custom Base URL

```tsx
// The client automatically uses the production URL
// Override with environment variable:
// NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.com/api
```

## Health Check

```tsx
import { apiClient } from '@/lib/api';

async function checkApiHealth() {
  try {
    const health = await apiClient.healthCheck();
    console.log('API Status:', health.status);
  } catch (error) {
    console.error('API is down:', error);
  }
}
```

## Best Practices

1. **Always use React Query hooks** when possible for automatic caching and error handling
2. **Handle loading states** in your UI components
3. **Implement proper error boundaries** for API errors
4. **Use optimistic updates** for better UX where appropriate
5. **Prefetch data** for better performance when navigating
6. **Invalidate queries** appropriately after mutations

## TypeScript Support

All API methods are fully typed with TypeScript. The client will provide:

- ✅ Autocomplete for API methods and parameters
- ✅ Type checking for request/response data
- ✅ IntelliSense for all available options
- ✅ Compile-time error checking for invalid usage

## Production Deployment

The API client is configured to work with the production backend at:
`https://threadr-production.up.railway.app/api`

Ensure your environment variables are set correctly:

```env
NEXT_PUBLIC_API_BASE_URL=https://threadr-production.up.railway.app/api
```