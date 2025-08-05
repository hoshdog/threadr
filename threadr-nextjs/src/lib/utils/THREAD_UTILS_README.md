# Thread Generation Utilities

Modern TypeScript utilities extracted from the Alpine.js Threadr application. These utilities provide comprehensive thread generation, validation, and management functionality.

## Overview

The thread utilities are extracted from the production Threadr SaaS application and provide:

- **Tweet Splitting**: Intelligent content splitting respecting word boundaries
- **Character Counting**: Proper emoji and Unicode support
- **URL Validation**: Comprehensive URL validation with domain support
- **Thread Management**: Creation, validation, and statistics
- **TypeScript Support**: Full type safety and intellisense

## Installation

The utilities are located at: `src/lib/utils/thread.ts`

To use in your components:

```typescript
import {
  splitIntoTweets,
  validateUrl,
  countCharacters,
  getThreadStats
} from '@/lib/utils/thread';
```

## Core Functions

### `splitIntoTweets(content: string, options?: SplitOptions): string[]`

Intelligently splits long content into tweet-sized chunks while preserving word boundaries.

```typescript
const longContent = "Your long article content here...";
const tweets = splitIntoTweets(longContent, {
  maxLength: 280,
  preserveWords: true,
  addNumbers: true,
  numberFormat: '{current}/{total}'
});

// Result: ['1/3 Your long article...', '2/3 content continues...', '3/3 final part.']
```

**Options:**
- `maxLength`: Maximum characters per tweet (default: 280)
- `preserveWords`: Avoid breaking words (default: true)
- `addNumbers`: Add tweet numbering (default: true)
- `numberFormat`: Numbering format string (default: '{current}/{total}')

### `validateUrl(url: string): boolean`

Comprehensive URL validation supporting both built-in URL constructor and regex patterns.

```typescript
validateUrl('https://medium.com/@user/article'); // true
validateUrl('not-a-url'); // false
validateUrl('https://localhost:3000'); // true
```

### `countCharacters(text: string): number`

Accurately counts characters including emojis and Unicode characters.

```typescript
countCharacters('Hello 👋'); // 7 (not 8)
countCharacters('こんにちは'); // 5
countCharacters('Regular text'); // 12
```

### `validateTweetLength(text: string, maxLength?: number)`

Validates tweet length and provides detailed feedback.

```typescript
const validation = validateTweetLength('Your tweet content');
// Returns:
// {
//   isValid: boolean,
//   characterCount: number,
//   isWarning: boolean, // true if > 250 chars
//   remainingCharacters: number
// }
```

### `getThreadStats(tweets: Tweet[])`

Comprehensive thread statistics for analytics and optimization.

```typescript
const stats = getThreadStats(threadTweets);
// Returns:
// {
//   totalTweets: number,
//   totalCharacters: number,
//   averageLength: number,
//   longestTweet: number,
//   shortestTweet: number,
//   tweetsOverLimit: number,
//   tweetsNearLimit: number
// }
```

## Supporting Functions

### `addTweetNumbers(tweets: string[], format?: string): string[]`

Adds numbering to tweet arrays with customizable format.

```typescript
const numbered = addTweetNumbers(['First tweet', 'Second tweet'], '{current}.');
// Result: ['1. First tweet', '2. Second tweet']
```

### `createThreadFromTweets(tweets: string[]): Tweet[]`

Converts plain strings to Tweet objects with metadata.

```typescript
const threadObjects = createThreadFromTweets(['Tweet 1', 'Tweet 2']);
// Result: [
//   { text: 'Tweet 1', copied: false },
//   { text: 'Tweet 2', copied: false }
// ]
```

### `threadToText(tweets: Tweet[], separator?: string): string`

Converts thread back to plain text for export/copying.

```typescript
const plainText = threadToText(threadObjects, '\n\n');
// Result: "Tweet 1\n\nTweet 2"
```

### `cleanContent(content: string): string`

Normalizes content for consistent processing.

```typescript
const cleaned = cleanContent('Line 1\r\nLine 2\n\n\nLine 3');
// Result: "Line 1\nLine 2\n\nLine 3"
```

### `isSupportedDomain(url: string): boolean`

Checks if URL is from a supported content domain.

```typescript
isSupportedDomain('https://medium.com/article'); // true
isSupportedDomain('https://dev.to/post'); // true
isSupportedDomain('https://facebook.com/post'); // false
```

## Type Definitions

```typescript
interface Tweet {
  text: string;
  copied?: boolean;
}

interface ThreadResponse {
  thread: Tweet[];
  thread_id?: string;
  usage?: {
    daily_count: number;
    monthly_count: number;
  };
}

interface SplitOptions {
  maxLength?: number;
  preserveWords?: boolean;
  addNumbers?: boolean;
  numberFormat?: string;
}
```

## Constants

```typescript
export const DEFAULT_TWEET_LENGTH = 280;
export const TWEET_WARNING_LENGTH = 250;
export const SUPPORTED_DOMAINS = [
  'medium.com',
  'dev.to',
  'substack.com',
  // ... more domains
];
```

## Usage Examples

### Basic Thread Generation

```typescript
import { splitIntoTweets, createThreadFromTweets } from '@/lib/utils/thread';

function generateThread(content: string) {
  // Split content into tweets
  const tweetStrings = splitIntoTweets(content, {
    maxLength: 280,
    preserveWords: true,
    addNumbers: true
  });
  
  // Create thread objects
  const tweets = createThreadFromTweets(tweetStrings);
  
  return tweets;
}
```

### Content Validation Pipeline

```typescript
import { validateUrl, cleanContent, isSupportedDomain } from '@/lib/utils/thread';

function validateContentInput(input: string, isUrl: boolean) {
  if (isUrl) {
    if (!validateUrl(input)) {
      throw new Error('Invalid URL format');
    }
    
    if (!isSupportedDomain(input)) {
      console.warn('URL domain may not be fully supported');
    }
  }
  
  return cleanContent(input);
}
```

### Thread Analytics

```typescript
import { getThreadStats, validateTweetLength } from '@/lib/utils/thread';

function analyzeThread(tweets: Tweet[]) {
  const stats = getThreadStats(tweets);
  
  // Check for issues
  if (stats.tweetsOverLimit > 0) {
    console.warn(`${stats.tweetsOverLimit} tweets exceed character limit`);
  }
  
  // Validate each tweet
  const validations = tweets.map(tweet => 
    validateTweetLength(tweet.text)
  );
  
  return { stats, validations };
}
```

### Integration with React Components

```typescript
'use client';

import { useState } from 'react';
import { 
  splitIntoTweets, 
  validateUrl, 
  createThreadFromTweets,
  type Tweet 
} from '@/lib/utils/thread';

export function ThreadGenerator() {
  const [content, setContent] = useState('');
  const [tweets, setTweets] = useState<Tweet[]>([]);
  
  const handleGenerate = () => {
    if (!content.trim()) return;
    
    const tweetStrings = splitIntoTweets(content);
    const threadObjects = createThreadFromTweets(tweetStrings);
    setTweets(threadObjects);
  };
  
  return (
    <div>
      <textarea 
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Enter your content..."
      />
      <button onClick={handleGenerate}>Generate Thread</button>
      
      {tweets.map((tweet, index) => (
        <div key={index}>
          <span>{index + 1}/{tweets.length}</span>
          <p>{tweet.text}</p>
        </div>
      ))}
    </div>
  );
}
```

## Testing

Comprehensive test suite available at `thread.test.ts`:

```bash
npm test thread.test.ts
```

Tests cover:
- Tweet splitting with various content lengths
- Character counting with emojis and Unicode
- URL validation edge cases
- Thread statistics calculation
- Integration workflows

## Migration from Alpine.js

The utilities maintain compatibility with the original Alpine.js implementation:

### Original Alpine.js Pattern:
```javascript
// Alpine.js component method
generateThread() {
  // API call to backend
  const response = await fetch('/api/generate', { ... });
  const data = await response.json();
  this.tweets = data.thread.map(tweet => ({
    text: tweet.content || tweet.text,
    copied: false
  }));
}
```

### New TypeScript Pattern:
```typescript
// React component with utilities
const handleGenerate = async () => {
  try {
    const response = await fetch('/api/generate', { ... });
    const data: ThreadResponse = await response.json();
    
    // Use utility for consistent object creation
    const tweets = createThreadFromTweets(
      data.thread.map(t => t.content || t.text || '')
    );
    
    setTweets(tweets);
  } catch (error) {
    console.error('Thread generation failed:', error);
  }
};
```

## Performance Characteristics

- **splitIntoTweets**: O(n) where n is content length
- **countCharacters**: O(n) with Unicode support
- **validateUrl**: O(1) with regex and URL constructor
- **Thread operations**: O(n) where n is number of tweets

Optimized for handling:
- Content up to 50,000 characters
- Threads up to 50 tweets
- Real-time character counting
- Batch validation operations

## Browser Compatibility

- **Modern browsers**: Full support with all features
- **Legacy browsers**: Graceful degradation for URL validation
- **Node.js**: Full server-side support
- **TypeScript**: Complete type safety and intellisense

## Future Enhancements

Planned improvements based on the original Threadr roadmap:

1. **Advanced splitting algorithms**: ML-based content segmentation
2. **Custom formatting**: User-defined tweet templates
3. **Social platform variants**: LinkedIn, Facebook post formatting
4. **Content optimization**: AI-powered engagement optimization
5. **Batch processing**: Handling multiple articles simultaneously

These utilities provide a solid foundation for any thread generation application while maintaining the proven functionality of the production Threadr SaaS.