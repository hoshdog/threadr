# Threadr Next.js

A modern, production-ready Next.js application for converting blog articles into Twitter threads using AI.

## 🚀 Features

- **Next.js 14** with App Router
- **TypeScript** with strict mode configuration
- **Tailwind CSS** with custom Threadr theme
- **React Query** for server state management
- **Zustand** for client state management
- **React Hook Form** with Zod validation
- **JWT Authentication** with secure token handling
- **Responsive Design** with mobile-first approach
- **Dark/Light Theme** support
- **Production-ready** configurations

## 📁 Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── globals.css        # Global styles with Threadr theme
│   ├── layout.tsx         # Root layout with providers
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── ui/               # Reusable UI components
│   ├── forms/            # Form components
│   ├── layout/           # Layout components
│   └── common/           # Common components
├── lib/                  # Library code
│   ├── api/              # API client and endpoints
│   ├── stores/           # Zustand stores
│   ├── utils/            # Utility functions
│   └── providers/        # React providers
├── hooks/                # Custom React hooks
└── types/                # TypeScript type definitions
```

## 🛠️ Getting Started

### Prerequisites

- Node.js 18.17 or later
- npm, yarn, or pnpm

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.local.example .env.local
   ```
   
   Update the environment variables in `.env.local`:
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8001/api
   NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your-stripe-key
   # ... other variables
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 📝 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint issues
- `npm run format` - Format code with Prettier
- `npm run format:check` - Check code formatting
- `npm run type-check` - Run TypeScript type checking
- `npm run clean` - Clean build artifacts

## 🔧 Configuration

### TypeScript

Strict TypeScript configuration with additional safety checks:
- `noUncheckedIndexedAccess`
- `noImplicitReturns`
- `noFallthroughCasesInSwitch`

### ESLint & Prettier

Production-ready linting and formatting configuration:
- Next.js recommended rules
- TypeScript strict rules
- Prettier integration
- Import sorting

### Tailwind CSS

Custom theme with Threadr's black/white aesthetic:
- Custom color palette
- Inter font integration
- Dark mode support
- Component classes for buttons, inputs, cards

## 🔐 Authentication

JWT-based authentication system with:
- Secure token storage (cookies + localStorage)
- Automatic token refresh
- Auth state management with Zustand
- Protected routes and API calls

## 🌐 API Integration

Axios-based API client with:
- Request/response interceptors
- Automatic token injection
- Error handling
- TypeScript support

## 📱 State Management

### Zustand Stores

- **Auth Store**: User authentication and profile management
- **App Store**: Global app state (theme, notifications, sidebar)

### React Query

Server state management for:
- Caching API responses
- Background refetching
- Optimistic updates
- Error handling

## 🎨 Theming

### Color Palette

- **Primary**: Black/white theme matching existing Threadr design
- **Accent**: Blue shades for interactive elements
- **Semantic**: Success, error, warning colors
- **Dark Mode**: Full dark theme support

### Components

Pre-built UI components following design system:
- Buttons (primary, secondary, outline, ghost)
- Inputs with validation states
- Cards with consistent styling
- Loading states and animations

## 📦 Dependencies

### Core Dependencies
- `next` - React framework
- `react` & `react-dom` - React library
- `typescript` - Type safety
- `tailwindcss` - Styling
- `@tanstack/react-query` - Server state
- `zustand` - Client state
- `axios` - HTTP client
- `react-hook-form` - Forms
- `zod` - Validation
- `js-cookie` - Cookie management

### Development Dependencies
- `eslint` & `prettier` - Code quality
- `@types/*` - TypeScript definitions

## 🚀 Deployment

### Vercel (Recommended)

1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Other Platforms

The app can be deployed to any platform supporting Next.js:
- Netlify
- Railway
- AWS Amplify
- Docker

## 🔒 Environment Variables

Required environment variables:

```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.com/api
NEXT_PUBLIC_FRONTEND_URL=https://your-domain.com

# Authentication
NEXT_PUBLIC_JWT_SECRET=your-jwt-secret

# Stripe (for payments)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...

# Optional
REDIS_URL=redis://...
NODE_ENV=production
```

## 📊 Performance

- **Bundle Analysis**: Use `npm run build` to see bundle sizes
- **Core Web Vitals**: Optimized for good CWV scores
- **Image Optimization**: Next.js automatic image optimization
- **Code Splitting**: Automatic route-based code splitting

## 🧪 Testing

Testing setup ready for:
- Unit tests with Jest
- Integration tests with Testing Library
- E2E tests with Playwright

## 📚 Documentation

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [React Query Documentation](https://tanstack.com/query/latest)
- [Zustand Documentation](https://zustand-demo.pmnd.rs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
