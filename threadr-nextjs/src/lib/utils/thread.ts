/**
 * Thread Generation Utilities
 * 
 * Core algorithms extracted from the Alpine.js Threadr app for modern TypeScript usage.
 * Handles tweet splitting, character counting, URL validation, and thread formatting.
 */

// Types
export interface Tweet {
  text: string;
  copied?: boolean;
}

export interface ThreadResponse {
  thread: Tweet[];
  thread_id?: string;
  usage?: {
    daily_count: number;
    monthly_count: number;
  };
}

export interface SplitOptions {
  maxLength?: number;
  preserveWords?: boolean;
  addNumbers?: boolean;
  numberFormat?: string;
}

// Constants
export const DEFAULT_TWEET_LENGTH = 280;
export const TWEET_WARNING_LENGTH = 250;
export const URL_REGEX = /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/;

/**
 * Splits content into tweet-sized chunks while preserving word boundaries
 * 
 * @param content - The content to split into tweets
 * @param options - Configuration options for splitting
 * @returns Array of tweet strings
 */
export function splitIntoTweets(
  content: string, 
  options: SplitOptions = {}
): string[] {
  const {
    maxLength = DEFAULT_TWEET_LENGTH,
    preserveWords = true,
    addNumbers = true,
    numberFormat = '{current}/{total}'
  } = options;

  if (!content || typeof content !== 'string') {
    return [];
  }

  // Clean up the content
  const cleanContent = content.trim().replace(/\r\n/g, '\n').replace(/\r/g, '\n');
  
  if (cleanContent.length === 0) {
    return [];
  }

  // If content fits in one tweet and no numbering needed
  const effectiveMaxLength = addNumbers ? maxLength - estimateNumberingLength(numberFormat) : maxLength;
  
  if (cleanContent.length <= effectiveMaxLength) {
    return [cleanContent];
  }

  const tweets: string[] = [];
  let remainingContent = cleanContent;

  while (remainingContent.length > 0) {
    let chunkSize = effectiveMaxLength;
    let chunk = remainingContent.substring(0, chunkSize);

    // If we're preserving words and didn't reach the end
    if (preserveWords && remainingContent.length > chunkSize) {
      // Find the last space within the chunk to avoid breaking words
      const lastSpaceIndex = chunk.lastIndexOf(' ');
      const lastNewlineIndex = chunk.lastIndexOf('\n');
      const lastBreakIndex = Math.max(lastSpaceIndex, lastNewlineIndex);

      if (lastBreakIndex > chunkSize * 0.5) { // Don't break too early
        chunk = chunk.substring(0, lastBreakIndex);
      }
    }

    tweets.push(chunk.trim());
    remainingContent = remainingContent.substring(chunk.length).trim();
  }

  // Add numbering if requested
  if (addNumbers && tweets.length > 1) {
    return addTweetNumbers(tweets, numberFormat);
  }

  return tweets;
}

/**
 * Adds numbering to tweets in the specified format
 * 
 * @param tweets - Array of tweet strings
 * @param format - Numbering format (e.g., '{current}/{total}', '{current}.')
 * @returns Array of numbered tweets
 */
export function addTweetNumbers(tweets: string[], format: string = '{current}/{total}'): string[] {
  if (!Array.isArray(tweets) || tweets.length <= 1) {
    return tweets;
  }

  return tweets.map((tweet, index) => {
    const current = index + 1;
    const total = tweets.length;
    
    const numberString = format
      .replace('{current}', current.toString())
      .replace('{total}', total.toString());

    // Add the number at the beginning, handling existing threading indicators
    if (tweet.startsWith('🧵') || tweet.match(/^\d+[.)]/)) {
      return `${numberString} ${tweet}`;
    }
    
    return `${numberString} ${tweet}`;
  });
}

/**
 * Counts characters in text, handling emojis and special characters properly
 * 
 * @param text - Text to count characters for
 * @returns Character count
 */
export function countCharacters(text: string): number {
  if (!text || typeof text !== 'string') {
    return 0;
  }

  // Use the spread operator to properly handle emojis and multi-byte characters
  return [...text].length;
}

/**
 * Validates if a string is a valid URL
 * 
 * @param url - URL string to validate
 * @returns Boolean indicating if URL is valid
 */
export function validateUrl(url: string): boolean {
  if (!url || typeof url !== 'string') {
    return false;
  }

  try {
    // First try the built-in URL constructor for comprehensive validation
    new URL(url);
    
    // Additional regex check for common patterns
    return URL_REGEX.test(url);
  } catch {
    return false;
  }
}

/**
 * Checks if a tweet exceeds the character limit
 * 
 * @param text - Tweet text to validate
 * @param maxLength - Maximum allowed length (default: 280)
 * @returns Object with validation result and character count
 */
export function validateTweetLength(text: string, maxLength: number = DEFAULT_TWEET_LENGTH) {
  const characterCount = countCharacters(text);
  
  return {
    isValid: characterCount <= maxLength,
    characterCount,
    isWarning: characterCount > TWEET_WARNING_LENGTH,
    remainingCharacters: maxLength - characterCount
  };
}

/**
 * Creates a thread object from an array of tweet strings
 * 
 * @param tweets - Array of tweet strings
 * @returns Array of Tweet objects
 */
export function createThreadFromTweets(tweets: string[]): Tweet[] {
  if (!Array.isArray(tweets)) {
    return [];
  }

  return tweets.map(text => ({
    text: text.trim(),
    copied: false
  }));
}

/**
 * Converts a thread back to plain text
 * 
 * @param tweets - Array of Tweet objects
 * @param separator - String to join tweets (default: double newline)
 * @returns Combined text string
 */
export function threadToText(tweets: Tweet[], separator: string = '\n\n'): string {
  if (!Array.isArray(tweets)) {
    return '';
  }

  return tweets
    .map(tweet => tweet.text)
    .filter(text => text.trim().length > 0)
    .join(separator);
}

/**
 * Estimates the length needed for tweet numbering
 * 
 * @param format - Numbering format string
 * @param maxTweets - Maximum expected number of tweets (default: 50)
 * @returns Estimated character length needed for numbering
 */
function estimateNumberingLength(format: string, maxTweets: number = 50): number {
  // Estimate with maximum expected values
  const sampleNumbering = format
    .replace('{current}', maxTweets.toString())
    .replace('{total}', maxTweets.toString());
  
  return countCharacters(sampleNumbering) + 1; // +1 for space after numbering
}

/**
 * Cleans and normalizes content for thread generation
 * 
 * @param content - Raw content to clean
 * @returns Cleaned content string
 */
export function cleanContent(content: string): string {
  if (!content || typeof content !== 'string') {
    return '';
  }

  return content
    .trim()
    .replace(/\r\n/g, '\n')  // Normalize line endings
    .replace(/\r/g, '\n')    // Handle old Mac line endings
    .replace(/\n{3,}/g, '\n\n')  // Collapse multiple newlines
    .replace(/[ \t]+/g, ' ')     // Collapse multiple spaces/tabs
    .replace(/^\s+|\s+$/gm, ''); // Trim each line
}

/**
 * Extracts supported domains for URL validation
 * Based on the original Threadr supported domains
 */
export const SUPPORTED_DOMAINS = [
  'medium.com',
  'dev.to',
  'substack.com',
  'hashnode.dev',
  'hackernoon.com',
  'towards-data-science.medium.com',
  'javascript.plainenglish.io',
  'blog.logrocket.com',
  'css-tricks.com',
  'smashingmagazine.com',
  'a16z.com',
  'techcrunch.com',
  'arstechnica.com',
  'theverge.com',
  'wired.com'
];

/**
 * Checks if a URL is from a supported domain
 * 
 * @param url - URL to check
 * @returns Boolean indicating if domain is supported
 */
export function isSupportedDomain(url: string): boolean {
  if (!validateUrl(url)) {
    return false;
  }

  try {
    const urlObj = new URL(url);
    const hostname = urlObj.hostname.toLowerCase();
    
    return SUPPORTED_DOMAINS.some(domain => 
      hostname === domain || hostname.endsWith(`.${domain}`)
    );
  } catch {
    return false;
  }
}

/**
 * Utility to copy text to clipboard (browser environment)
 * 
 * @param text - Text to copy
 * @returns Promise that resolves when copy is complete
 */
export async function copyToClipboard(text: string): Promise<void> {
  if (typeof navigator !== 'undefined' && navigator.clipboard) {
    await navigator.clipboard.writeText(text);
  } else {
    // Fallback for environments without clipboard API
    throw new Error('Clipboard API not available');
  }
}

/**
 * Thread statistics utility
 * 
 * @param tweets - Array of Tweet objects
 * @returns Statistics about the thread
 */
export function getThreadStats(tweets: Tweet[]) {
  if (!Array.isArray(tweets)) {
    return {
      totalTweets: 0,
      totalCharacters: 0,
      averageLength: 0,
      longestTweet: 0,
      shortestTweet: 0,
      tweetsOverLimit: 0,
      tweetsNearLimit: 0
    };
  }

  const lengths = tweets.map(tweet => countCharacters(tweet.text));
  const totalCharacters = lengths.reduce((sum, len) => sum + len, 0);
  
  return {
    totalTweets: tweets.length,
    totalCharacters,
    averageLength: tweets.length > 0 ? Math.round(totalCharacters / tweets.length) : 0,
    longestTweet: Math.max(...lengths, 0),
    shortestTweet: Math.min(...lengths, 0),
    tweetsOverLimit: lengths.filter(len => len > DEFAULT_TWEET_LENGTH).length,
    tweetsNearLimit: lengths.filter(len => len > TWEET_WARNING_LENGTH && len <= DEFAULT_TWEET_LENGTH).length
  };
}