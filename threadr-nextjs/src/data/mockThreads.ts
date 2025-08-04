/**
 * Mock Thread History Data for Development and Testing
 * 
 * This file provides realistic thread data for UI development while the backend
 * integration is being completed. The data structure matches the backend models
 * in backend/src/models/thread.py and the TypeScript interfaces in types/api.ts.
 */

import { SavedThread, ThreadTweet, ThreadMetadata, ContentType } from '../types/api';

// ============================================================================
// MOCK DATA CONSTANTS
// ============================================================================

const MOCK_USER_ID = 'user_12345';

const SAMPLE_URLS = [
  'https://medium.com/@example/building-better-apis-2024',
  'https://dev.to/programmer/react-hooks-explained',
  'https://substack.com/writer/startup-lessons',
  'https://blog.example.com/ai-future-predictions',
  'https://techcrunch.com/latest-funding-round',
  null, // Text-based thread
  'https://hackernoon.com/javascript-performance-tips',
  null, // Another text-based thread
  'https://css-tricks.com/modern-css-layouts',
  'https://smashingmagazine.com/design-systems-2024'
];

const SAMPLE_CONTENT_TYPES: ContentType[] = [
  ContentType.EDUCATIONAL,
  ContentType.TECHNICAL,
  ContentType.NEWS,
  ContentType.PERSONAL,
  ContentType.PROMOTIONAL
];

const SAMPLE_TAGS = [
  ['javascript', 'webdev', 'tutorial'],
  ['react', 'hooks', 'frontend'],
  ['startup', 'entrepreneurship', 'lessons'],
  ['ai', 'machine-learning', 'future'],
  ['funding', 'venture-capital', 'startups'],
  ['productivity', 'personal-development'],
  ['performance', 'optimization', 'javascript'],
  ['career', 'remote-work'],
  ['css', 'design', 'layouts'],
  ['design-systems', 'ui-ux', 'components']
];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Generate a random date within the last 90 days
 */
function getRandomDate(daysBack: number = 90): Date {
  const now = new Date();
  const randomDays = Math.floor(Math.random() * daysBack);
  const date = new Date(now);
  date.setDate(date.getDate() - randomDays);
  return date;
}

/**
 * Generate random engagement metrics
 */
function getRandomEngagement() {
  return {
    view_count: Math.floor(Math.random() * 5000) + 100,
    copy_count: Math.floor(Math.random() * 150) + 5
  };
}

/**
 * Create ThreadTweet objects from content array
 */
function createThreadTweets(content: string[]): ThreadTweet[] {
  return content.map((tweet, index) => ({
    id: `tweet_${Date.now()}_${index}`,
    content: tweet,
    order: index + 1,
    character_count: tweet.length
  }));
}

/**
 * Create ThreadMetadata object
 */
function createThreadMetadata(
  sourceUrl: string | null, 
  contentLength: number,
  tags: string[] = []
): ThreadMetadata {
  return {
    source_url: sourceUrl,
    source_type: sourceUrl ? 'URL' : 'text',
    generation_time_ms: Math.floor(Math.random() * 3000) + 1000, // 1-4 seconds
    ai_model: 'gpt-3.5-turbo',
    content_length: contentLength,
    tags
  };
}

// ============================================================================
// MOCK THREAD DATA
// ============================================================================

/**
 * Collection of realistic thread content for different topics and lengths
 */
const THREAD_CONTENT_SAMPLES = [
  // 1. JavaScript Performance Tips (8 tweets)
  {
    title: "5 JavaScript Performance Tips That Actually Matter",
    originalContent: "Here are the most impactful JavaScript performance optimizations I've learned after 5 years of frontend development...",
    tweets: [
      "🚀 5 JavaScript performance tips that actually matter (thread)",
      "After 5 years of frontend development, these are the optimizations that made the biggest difference:",
      "1️⃣ Debounce expensive operations\n\nDon't let search boxes kill your app. Debounce API calls to prevent excessive requests.",
      "2️⃣ Use Web Workers for heavy computations\n\nMove CPU-intensive tasks off the main thread. Your UI will thank you.",
      "3️⃣ Lazy load images and components\n\nOnly load what's visible. Intersection Observer API is your friend here.",
      "4️⃣ Optimize bundle size with tree shaking\n\nImport only what you need. Your users on 3G will appreciate smaller bundles.",
      "5️⃣ Cache API responses intelligently\n\nImplement proper caching strategies. SWR and React Query make this easier.",
      "💡 Pro tip: Measure first, optimize second. Use Chrome DevTools to identify actual bottlenecks before optimizing.\n\nWhat performance tip would you add to this list?"
    ],
    sourceUrl: SAMPLE_URLS[6],
    tags: SAMPLE_TAGS[6],
    engagement: { view_count: 3200, copy_count: 89 }
  },

  // 2. React Hooks Tutorial (12 tweets)
  {
    title: "React Hooks Explained: useState, useEffect, and Custom Hooks",
    originalContent: "A comprehensive guide to React Hooks, covering the basics and advanced patterns...",
    tweets: [
      "🧵 React Hooks explained (for beginners and pros)",
      "Hooks changed how we write React components. Here's everything you need to know:",
      "useState - Your gateway to state management\n\n```jsx\nconst [count, setCount] = useState(0);\n```\n\nSimple, predictable, powerful.",
      "useEffect - Handle side effects like a pro\n\n```jsx\nuseEffect(() => {\n  // Side effect here\n  return () => cleanup();\n}, [dependencies]);\n```",
      "Common useEffect patterns:\n\n🔄 Data fetching\n🎧 Event listeners\n⏰ Timers and intervals\n📊 Subscriptions",
      "useContext - Share state without prop drilling\n\n```jsx\nconst theme = useContext(ThemeContext);\n```\n\nPerfect for themes, auth, and global state.",
      "useMemo - Optimize expensive calculations\n\n```jsx\nconst expensiveValue = useMemo(() => {\n  return heavyComputation(data);\n}, [data]);\n```",
      "useCallback - Prevent unnecessary re-renders\n\n```jsx\nconst memoizedCallback = useCallback(() => {\n  doSomething(a, b);\n}, [a, b]);\n```",
      "Custom Hooks - Your secret weapon 🎯\n\nExtract component logic into reusable functions:",
      "```jsx\nfunction useApi(url) {\n  const [data, setData] = useState(null);\n  const [loading, setLoading] = useState(true);\n  \n  useEffect(() => {\n    fetch(url).then(setData).finally(() => setLoading(false));\n  }, [url]);\n  \n  return { data, loading };\n}\n```",
      "Rules of Hooks:\n\n✅ Only call at top level\n✅ Only call from React functions\n❌ No conditional hooks\n❌ No hooks in loops",
      "Hooks transformed React development. They're intuitive, powerful, and unlock new patterns.\n\nWhat's your favorite hook? Share your go-to custom hooks below! 👇"
    ],
    sourceUrl: SAMPLE_URLS[1],
    tags: SAMPLE_TAGS[1],
    engagement: { view_count: 4500, copy_count: 123 }
  },

  // 3. Startup Lessons (6 tweets)
  {
    title: "3 Hard Lessons From My Failed Startup",
    originalContent: "After shutting down my startup last month, here are the brutal lessons I learned...",
    tweets: [
      "3 brutal lessons from my failed startup 💔",
      "We shut down last month after 2 years. Here's what I wish I knew:",
      "Lesson 1: Build for a market, not an idea\n\nWe built something technically impressive that nobody wanted. Market research isn't optional.",
      "Lesson 2: Runway is everything\n\nWe burned through cash too fast trying to 'move fast and break things'. Sometimes slow and steady wins.",
      "Lesson 3: Team > Technology\n\nHiring the wrong people cost us 6 months and $200K. Culture and values matter more than technical skills.",
      "Failure hurts, but it teaches. Starting my next venture with these lessons burned into my brain.\n\nWhat's the hardest lesson you've learned? 👇"
    ],
    sourceUrl: SAMPLE_URLS[2],
    tags: SAMPLE_TAGS[2],
    engagement: { view_count: 2800, copy_count: 67 }
  },

  // 4. AI Future Predictions (10 tweets)
  {
    title: "My Bold AI Predictions for 2025-2027",
    originalContent: "Here are my predictions for how AI will transform industries in the next 3 years...",
    tweets: [
      "🔮 My bold AI predictions for 2025-2027",
      "Based on current trends and breakthroughs, here's what I see coming:",
      "Prediction 1: AI coding assistants will write 60% of production code\n\nGitHub Copilot is just the beginning. Full-stack AI developers are coming.",
      "Prediction 2: Every company becomes an AI company\n\nJust like every company became a 'digital' company, AI integration will be table stakes.",
      "Prediction 3: Creative industries get AI-augmented\n\nDesigners, writers, and artists will use AI as creative partners, not replacements.",
      "Prediction 4: Education transforms completely\n\nPersonalized AI tutors for every student. One-size-fits-all education dies.",
      "Prediction 5: Healthcare diagnostics reach superhuman accuracy\n\nAI will detect diseases years before human doctors could.",
      "The wildcard: AGI breakthrough by 2027\n\n20% chance we achieve artificial general intelligence. This changes everything.",
      "What am I wrong about? What am I missing?\n\nRemindMe! 2027 to see how these predictions aged 📅",
      "The future is coming faster than we think. The question isn't IF AI transforms everything, but HOW FAST.\n\nWhat industry do you think AI will disrupt next? 👇"
    ],
    sourceUrl: SAMPLE_URLS[3],
    tags: SAMPLE_TAGS[3],
    engagement: { view_count: 5200, copy_count: 145 }
  },

  // 5. Funding News (5 tweets)
  {
    title: "Breaking: TechCorp Raises $50M Series B",
    originalContent: "TechCorp just announced their $50M Series B funding round led by Sequoia Capital...",
    tweets: [
      "🔥 BREAKING: TechCorp raises $50M Series B",
      "Led by Sequoia Capital with participation from existing investors. Here's what this means:",
      "💰 Valuation jumped from $100M to $400M\n📈 4x growth in 18 months\n🎯 Expanding to European markets\n👥 Hiring 200+ engineers",
      "This validates the B2B SaaS productivity space is still hot. VCs are betting big on enterprise tools.",
      "Key takeaway for founders: Product-market fit + strong unit economics = funding in any market.\n\nCongrats to the TechCorp team! 🎉"
    ],
    sourceUrl: SAMPLE_URLS[4],
    tags: SAMPLE_TAGS[4],
    engagement: { view_count: 1800, copy_count: 34 }
  },

  // 6. Personal Productivity (7 tweets) - Text-based
  {
    title: "My Morning Routine for Maximum Productivity",
    originalContent: "After experimenting with different morning routines for 2 years, I've found what actually works...",
    tweets: [
      "My morning routine for maximum productivity ☀️",
      "After 2 years of experimentation, here's what actually works (no BS, just results):",
      "5:30 AM - Wake up (no snooze button)\n6:00 AM - 20 minutes meditation\n6:20 AM - Review daily priorities\n6:30 AM - Exercise (30 mins)",
      "7:00 AM - Cold shower (game changer for alertness)\n7:15 AM - Healthy breakfast + coffee\n7:45 AM - Deep work block (2 hours, no distractions)",
      "The key insights:\n\n🧠 Your brain is sharpest in the first 2 hours\n⏰ Consistency beats perfection\n📱 No phone for the first hour",
      "What I tried that DIDN'T work:\n\n❌ 4 AM wake-ups (unsustainable)\n❌ Hour-long workouts (too exhausting)\n❌ Checking email first thing",
      "Your morning sets the tone for your entire day. Invest in it.\n\nWhat's one morning habit that changed your life? Share below! 👇"
    ],
    sourceUrl: null,
    tags: SAMPLE_TAGS[5],
    engagement: { view_count: 3500, copy_count: 98 }
  },

  // 7. Career Advice (9 tweets) - Text-based
  {
    title: "Why I Quit My $200k Job to Go Remote",
    originalContent: "Last month I left my $200k corporate job to work remotely. Here's why and what I learned...",
    tweets: [
      "Why I quit my $200K job to go remote 🏠",
      "Last month I left corporate life behind. Here's the real story:",
      "The breaking point: 2 hours daily commute + toxic office politics + zero work-life balance = misery with a good salary.",
      "What I was afraid of:\n\n💰 Taking a pay cut\n🏠 Working from home discipline\n🤝 Missing team collaboration\n📈 Career growth stagnation",
      "The reality after 30 days:\n\n✅ 20% pay increase (remote premium)\n✅ 3x more productive\n✅ Better team communication (async)\n✅ Learning new skills daily",
      "Unexpected benefits:\n\n⏰ 10 extra hours per week\n💪 Daily gym sessions\n🍳 Home-cooked meals\n🌍 Traveling while working",
      "The downsides (being honest):\n\n😴 Harder to 'switch off'\n🏠 Home office setup costs\n👥 Less spontaneous conversations\n🎯 Need strong self-discipline",
      "Tips for remote work success:\n\n📍 Dedicated workspace\n⏰ Strict schedule\n💬 Over-communicate\n🎯 Set clear boundaries",
      "Remote work isn't for everyone, but it changed my life. The future of work is flexibility.\n\nAre you thinking about going remote? What's holding you back? 👇"
    ],
    sourceUrl: null,
    tags: SAMPLE_TAGS[7],
    engagement: { view_count: 4200, copy_count: 112 }
  },

  // 8. CSS Layouts (11 tweets)
  {
    title: "Modern CSS Layouts: Grid vs Flexbox in 2024",
    originalContent: "A comprehensive comparison of CSS Grid and Flexbox for modern web layouts...",
    tweets: [
      "CSS Grid vs Flexbox in 2024 🎨",
      "Still confused about when to use which? Here's your definitive guide:",
      "Flexbox = One dimension (row OR column)\nGrid = Two dimensions (rows AND columns)\n\nThis is the fundamental difference.",
      "Use Flexbox for:\n\n🔄 Navigation bars\n📱 Button groups\n📊 Form layouts\n🎯 Centering content\n📋 Card layouts (single row/column)",
      "Use CSS Grid for:\n\n🖥️ Page layouts\n📱 Complex responsive designs\n🎨 Magazine-style layouts\n📊 Dashboard components\n🖼️ Image galleries",
      "Flexbox powers:\n\n```css\n.navbar {\n  display: flex;\n  justify-content: space-between;\n  align-items: center;\n}\n```\n\nPerfect for navigation!",
      "CSS Grid shines:\n\n```css\n.layout {\n  display: grid;\n  grid-template-areas:\n    'header header'\n    'sidebar main'\n    'footer footer';\n}\n```",
      "Pro tip: Use them together! 🤝\n\nGrid for overall layout, Flexbox for component internals.",
      "Example: Grid container with Flexbox cards\n\n```css\n.card-grid {\n  display: grid;\n  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));\n}\n\n.card {\n  display: flex;\n  flex-direction: column;\n}\n```",
      "Browser support in 2024:\n\n✅ Grid: 96% global support\n✅ Flexbox: 98% global support\n\nYou can use both confidently!",
      "Stop overthinking it:\n\n🤔 One dimension? → Flexbox\n🤔 Two dimensions? → Grid\n🤔 Complex layout? → Grid + Flexbox\n\nWhat layout challenge are you facing? Drop it below! 👇"
    ],
    sourceUrl: SAMPLE_URLS[8],
    tags: SAMPLE_TAGS[8],
    engagement: { view_count: 2900, copy_count: 78 }
  },

  // 9. Design Systems (15 tweets)
  {
    title: "Building Design Systems That Scale: A Complete Guide",
    originalContent: "Everything you need to know about building design systems that actually get adopted by teams...",
    tweets: [
      "🧵 Building design systems that scale (complete guide)",
      "After building design systems for 5 companies, here's what actually works:",
      "First truth: Design systems aren't about components\n\nThey're about consistency, efficiency, and enabling teams to move faster.",
      "Start with these foundations:\n\n🎨 Color palette (semantic tokens)\n📝 Typography scale\n📏 Spacing system\n🔘 Border radius values\n🌫️ Shadow levels",
      "Color tokens example:\n\n```css\n--color-primary-500: #3B82F6;\n--color-surface-primary: var(--color-primary-500);\n--color-text-on-primary: #FFFFFF;\n```\n\nSemantic names > hex values",
      "Typography that scales:\n\n```css\n--font-size-xs: 0.75rem;   /* 12px */\n--font-size-sm: 0.875rem;  /* 14px */\n--font-size-base: 1rem;    /* 16px */\n--font-size-lg: 1.125rem;  /* 18px */\n```\n\n8pt grid system works wonders.",
      "Component hierarchy:\n\n1️⃣ Tokens (colors, fonts, spacing)\n2️⃣ Primitives (buttons, inputs)\n3️⃣ Patterns (forms, cards)\n4️⃣ Templates (page layouts)",
      "Documentation is everything 📚\n\nStorybook + MDX + live examples = adoption success\n\nNo docs = dead design system",
      "Governance that works:\n\n👥 Design system team (2-3 people max)\n🔄 Regular office hours\n📝 RFC process for new components\n📊 Usage analytics",
      "Common mistakes to avoid:\n\n❌ Building everything upfront\n❌ No feedback loop with teams\n❌ Over-engineering components\n❌ Ignoring developer experience",
      "Developer experience tips:\n\n✅ TypeScript support\n✅ Tree-shaking friendly\n✅ Clear error messages\n✅ Automated testing\n✅ Easy local development",
      "Measure success with:\n\n📊 Component adoption rates\n⏱️ Time to build new features\n🎯 Design-dev handoff efficiency\n🔄 Reduced design debt",
      "Evolution strategy:\n\n🌱 Start small (5-10 components)\n📈 Grow based on real needs\n🔄 Regular audits and cleanup\n📦 Versioning strategy",
      "Tools that help:\n\n🎨 Figma (design)\n📚 Storybook (docs)\n🔧 Changesets (versioning)\n🧪 Chromatic (visual testing)\n📦 npm/yarn workspaces",
      "Design systems are marathons, not sprints. Focus on adoption over perfection.\n\nWhat's your biggest design system challenge? Let's solve it together! 👇"
    ],
    sourceUrl: SAMPLE_URLS[9],
    tags: SAMPLE_TAGS[9],
    engagement: { view_count: 3800, copy_count: 156 }
  },

  // 10. Short Success Story (4 tweets)
  {
    title: "How I Got My First 1000 Newsletter Subscribers",
    originalContent: "The simple strategy that helped me grow my newsletter from 0 to 1000 subscribers in 3 months...",
    tweets: [
      "How I got my first 1000 newsletter subscribers 📧",
      "3 months, 0 to 1000 subs. Here's the simple strategy:",
      "1️⃣ Consistent value (weekly technical deep dives)\n2️⃣ Twitter threads that convert\n3️⃣ Cross-promotion with other creators\n4️⃣ Lead magnet (free React course)",
      "The key: Solve one specific problem really well. My newsletter helps React developers level up.\n\nWhat problem could you solve for your audience? 🤔"
    ],
    sourceUrl: null,
    tags: ['newsletter', 'growth', 'content-marketing'],
    engagement: { view_count: 1600, copy_count: 45 }
  }
];

// ============================================================================
// GENERATE MOCK THREADS
// ============================================================================

/**
 * Generate complete SavedThread objects from the sample data
 */
export const mockThreads: SavedThread[] = THREAD_CONTENT_SAMPLES.map((sample, index) => {
  const createdAt = getRandomDate(90);
  const updatedAt = new Date(createdAt.getTime() + Math.random() * 7 * 24 * 60 * 60 * 1000); // Up to 7 days later
  const engagement = sample.engagement || getRandomEngagement();
  
  return {
    id: `thread_${Date.now()}_${index}`,
    user_id: MOCK_USER_ID,
    title: sample.title,
    original_content: sample.originalContent,
    tweets: createThreadTweets(sample.tweets),
    metadata: createThreadMetadata(
      sample.sourceUrl || null,
      sample.originalContent.length,
      sample.tags
    ),
    created_at: createdAt.toISOString(),
    updated_at: updatedAt.toISOString(),
    view_count: engagement.view_count,
    copy_count: engagement.copy_count,
    is_favorite: Math.random() > 0.7, // 30% chance of being favorited
    is_archived: Math.random() > 0.9, // 10% chance of being archived
    // Computed properties
    tweet_count: sample.tweets.length,
    total_characters: sample.tweets.reduce((total, tweet) => total + tweet.length, 0),
    preview_text: sample.tweets[0] 
      ? (sample.tweets[0].length > 100 
          ? sample.tweets[0].substring(0, 97) + '...'
          : sample.tweets[0])
      : ''
  };
});

// ============================================================================
// UTILITY FUNCTIONS FOR MOCK DATA
// ============================================================================

/**
 * Get threads filtered by criteria (mirrors backend filtering)
 */
export function getFilteredMockThreads({
  searchQuery,
  sourceType,
  isFavorite,
  isArchived,
  dateFrom,
  dateTo,
  tags
}: {
  searchQuery?: string;
  sourceType?: 'URL' | 'text';
  isFavorite?: boolean;
  isArchived?: boolean;
  dateFrom?: Date;
  dateTo?: Date;
  tags?: string[];
} = {}): SavedThread[] {
  let filtered = [...mockThreads];

  // Search query filter
  if (searchQuery) {
    const query = searchQuery.toLowerCase();
    filtered = filtered.filter(thread =>
      thread.title.toLowerCase().includes(query) ||
      thread.original_content.toLowerCase().includes(query) ||
      thread.tweets.some(tweet => tweet.content.toLowerCase().includes(query))
    );
  }

  // Source type filter
  if (sourceType) {
    filtered = filtered.filter(thread => thread.metadata.source_type === sourceType);
  }

  // Favorite filter
  if (isFavorite !== undefined) {
    filtered = filtered.filter(thread => thread.is_favorite === isFavorite);
  }

  // Archived filter
  if (isArchived !== undefined) {
    filtered = filtered.filter(thread => thread.is_archived === isArchived);
  }

  // Date range filter
  if (dateFrom) {
    filtered = filtered.filter(thread => new Date(thread.created_at) >= dateFrom);
  }
  if (dateTo) {
    filtered = filtered.filter(thread => new Date(thread.created_at) <= dateTo);
  }

  // Tags filter
  if (tags && tags.length > 0) {
    filtered = filtered.filter(thread =>
      tags.some(tag => thread.metadata.tags.includes(tag))
    );
  }

  return filtered;
}

/**
 * Get paginated mock threads (mirrors backend pagination)
 */
export function getPaginatedMockThreads({
  page = 1,
  pageSize = 10,
  sortBy = 'created_at',
  sortOrder = 'desc',
  ...filters
}: {
  page?: number;
  pageSize?: number;
  sortBy?: 'created_at' | 'updated_at' | 'title' | 'tweet_count';
  sortOrder?: 'asc' | 'desc';
  searchQuery?: string;
  sourceType?: 'URL' | 'text';
  isFavorite?: boolean;
  isArchived?: boolean;
  dateFrom?: Date;
  dateTo?: Date;
  tags?: string[];
} = {}) {
  let filtered = getFilteredMockThreads(filters);

  // Sort threads
  filtered.sort((a, b) => {
    let aValue: any, bValue: any;
    
    switch (sortBy) {
      case 'created_at':
        aValue = new Date(a.created_at);
        bValue = new Date(b.created_at);
        break;
      case 'updated_at':
        aValue = new Date(a.updated_at);
        bValue = new Date(b.updated_at);
        break;
      case 'title':
        aValue = a.title.toLowerCase();
        bValue = b.title.toLowerCase();
        break;
      case 'tweet_count':
        aValue = a.tweet_count;
        bValue = b.tweet_count;
        break;
      default:
        aValue = new Date(a.created_at);
        bValue = new Date(b.created_at);
    }

    if (sortOrder === 'desc') {
      return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
    } else {
      return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
    }
  });

  // Paginate
  const totalCount = filtered.length;
  const startIndex = (page - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedThreads = filtered.slice(startIndex, endIndex);

  return {
    threads: paginatedThreads.map(thread => thread), // Convert to dict format like backend
    total_count: totalCount,
    page,
    page_size: pageSize,
    has_next: endIndex < totalCount,
    has_previous: page > 1
  };
}

/**
 * Get a single mock thread by ID
 */
export function getMockThreadById(id: string): SavedThread | undefined {
  return mockThreads.find(thread => thread.id === id);
}

/**
 * Get mock thread statistics
 */
export function getMockThreadStats() {
  const totalThreads = mockThreads.length;
  const favoriteThreads = mockThreads.filter(t => t.is_favorite).length;
  const archivedThreads = mockThreads.filter(t => t.is_archived).length;
  const urlBasedThreads = mockThreads.filter(t => t.metadata.source_type === 'URL').length;
  const textBasedThreads = mockThreads.filter(t => t.metadata.source_type === 'text').length;
  
  const totalViews = mockThreads.reduce((sum, t) => sum + t.view_count, 0);
  const totalCopies = mockThreads.reduce((sum, t) => sum + t.copy_count, 0);
  const averageTweetCount = Math.round(
    mockThreads.reduce((sum, t) => sum + t.tweet_count, 0) / totalThreads
  );

  // Get all unique tags
  const allTags = mockThreads.flatMap(t => t.metadata.tags);
  const uniqueTags = Array.from(new Set(allTags));
  
  // Tag frequency
  const tagCounts = allTags.reduce((acc, tag) => {
    acc[tag] = (acc[tag] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return {
    totalThreads,
    favoriteThreads,
    archivedThreads,
    urlBasedThreads,
    textBasedThreads,
    totalViews,
    totalCopies,
    averageTweetCount,
    uniqueTags,
    tagCounts,
    topTags: Object.entries(tagCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10)
      .map(([tag, count]) => ({ tag, count }))
  };
}

/**
 * Search mock threads by content
 */
export function searchMockThreads(query: string): SavedThread[] {
  if (!query.trim()) return mockThreads;
  
  return getFilteredMockThreads({ searchQuery: query });
}

/**
 * Get recent mock threads (last N days)
 */
export function getRecentMockThreads(days: number = 30): SavedThread[] {
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - days);
  
  return mockThreads.filter(thread => 
    new Date(thread.created_at) >= cutoffDate
  ).sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
}

// ============================================================================
// EXPORTS
// ============================================================================

export default mockThreads;

// Export types for convenience
export type { SavedThread, ThreadTweet, ThreadMetadata } from '../types/api';

// Export individual samples for specific testing
export { THREAD_CONTENT_SAMPLES };

/**
 * Example usage:
 * 
 * // Get all mock threads
 * import mockThreads from './mockThreads';
 * 
 * // Get paginated threads
 * import { getPaginatedMockThreads } from './mockThreads';
 * const result = getPaginatedMockThreads({ page: 1, pageSize: 5 });
 * 
 * // Search threads
 * import { searchMockThreads } from './mockThreads';
 * const results = searchMockThreads('React');
 * 
 * // Get thread stats
 * import { getMockThreadStats } from './mockThreads';
 * const stats = getMockThreadStats();
 */