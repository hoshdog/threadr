/**
 * Thread Utilities Demo
 * 
 * Demonstrates the core functionality extracted from the Alpine.js Threadr app
 */

import {
  splitIntoTweets,
  addTweetNumbers,
  countCharacters,
  validateUrl,
  validateTweetLength,
  createThreadFromTweets,
  threadToText,
  cleanContent,
  isSupportedDomain,
  getThreadStats,
  type Tweet,
  type SplitOptions
} from './thread';

// Demo: Basic thread generation workflow
export function demoBasicThreadGeneration() {
  console.log('=== Basic Thread Generation Demo ===\n');
  
  const longContent = `
    Here's an interesting article about the future of web development that I wanted to share with everyone.
    
    The landscape is changing rapidly with new frameworks and tools emerging constantly. Developers need to stay up-to-date with the latest trends while maintaining focus on fundamentals like performance, accessibility, and user experience.
    
    One key trend is the move towards full-stack frameworks that handle both frontend and backend concerns. This simplifies development workflows but requires developers to understand more concepts across the entire stack.
    
    Another important consideration is performance optimization. Modern users expect fast, responsive applications that work seamlessly across all devices and network conditions.
  `;

  // Step 1: Clean the content
  const cleaned = cleanContent(longContent);
  console.log('Original content length:', longContent.length);
  console.log('Cleaned content length:', cleaned.length);
  console.log('---');

  // Step 2: Split into tweets
  const tweets = splitIntoTweets(cleaned, {
    maxLength: 280,
    preserveWords: true,
    addNumbers: true,
    numberFormat: '{current}/{total}'
  });

  console.log(`Generated ${tweets.length} tweets:`);
  tweets.forEach((tweet, index) => {
    const validation = validateTweetLength(tweet);
    console.log(`\nTweet ${index + 1} (${validation.characterCount} chars):`);
    console.log(`"${tweet}"`);
    console.log(`Valid: ${validation.isValid}, Warning: ${validation.isWarning}`);
  });

  // Step 3: Create thread objects
  const threadObjects = createThreadFromTweets(tweets);
  
  // Step 4: Get statistics
  const stats = getThreadStats(threadObjects);
  console.log('\n=== Thread Statistics ===');
  console.log(`Total tweets: ${stats.totalTweets}`);
  console.log(`Total characters: ${stats.totalCharacters}`);
  console.log(`Average length: ${stats.averageLength}`);
  console.log(`Longest tweet: ${stats.longestTweet} chars`);
  console.log(`Shortest tweet: ${stats.shortestTweet} chars`);
  console.log(`Tweets over limit: ${stats.tweetsOverLimit}`);
  console.log(`Tweets near limit: ${stats.tweetsNearLimit}`);

  return threadObjects;
}

// Demo: URL validation
export function demoUrlValidation() {
  console.log('\n=== URL Validation Demo ===\n');
  
  const testUrls = [
    'https://medium.com/@user/great-article',
    'https://dev.to/developer/awesome-post',
    'https://user.substack.com/p/newsletter',
    'https://facebook.com/post/123',
    'not-a-url',
    'https://localhost:3000',
    'http://example.com',
    'ftp://files.example.com'
  ];

  testUrls.forEach(url => {
    const isValid = validateUrl(url);
    const isSupported = isSupportedDomain(url);
    
    console.log(`URL: ${url}`);
    console.log(`  Valid: ${isValid}`);
    console.log(`  Supported domain: ${isSupported}`);
    console.log('---');
  });
}

// Demo: Character counting with emojis
export function demoCharacterCounting() {
  console.log('\n=== Character Counting Demo ===\n');
  
  const testTexts = [
    'Hello world!',
    'Hello 👋 world 🌍',
    '🚀 Launch time! 🎉✨🔥',
    'こんにちは世界',
    'Héllo Wörld with àccénts',
    'Mixed: Hello 👋 こんにちは 🌍 Wörld!'
  ];

  testTexts.forEach(text => {
    const count = countCharacters(text);
    const jsLength = text.length; // JavaScript's default length
    
    console.log(`Text: "${text}"`);
    console.log(`  Proper count: ${count} chars`);
    console.log(`  JS .length: ${jsLength} chars`);
    console.log(`  Difference: ${jsLength - count}`);
    console.log('---');
  });
}

// Demo: Custom splitting options
export function demoCustomSplitting() {
  console.log('\n=== Custom Splitting Demo ===\n');
  
  const content = 'This is a demonstration of different splitting options for thread generation. ' +
                 'We can customize the maximum length, numbering format, and word preservation settings. ' +
                 'Each option affects how the content is divided into individual tweets.';

  // Different splitting configurations
  const configs: Array<{ name: string; options: SplitOptions }> = [
    {
      name: 'Default settings',
      options: {}
    },
    {
      name: 'No numbering',
      options: { addNumbers: false }
    },
    {
      name: 'Custom numbering',
      options: { numberFormat: 'Tweet {current}:' }
    },
    {
      name: 'Shorter tweets',
      options: { maxLength: 150, numberFormat: '{current}.' }
    },
    {
      name: 'No word preservation',
      options: { preserveWords: false, maxLength: 100 }
    }
  ];

  configs.forEach(config => {
    console.log(`\n--- ${config.name} ---`);
    const tweets = splitIntoTweets(content, config.options);
    
    tweets.forEach((tweet, index) => {
      console.log(`${index + 1}: "${tweet}" (${countCharacters(tweet)} chars)`);
    });
  });
}

// Demo: Thread conversion utilities
export function demoThreadConversion() {
  console.log('\n=== Thread Conversion Demo ===\n');
  
  // Create a sample thread
  const tweets = [
    'Here\'s a thread about web development best practices 🧵',
    'First, always prioritize user experience and accessibility in your designs.',
    'Second, write clean, maintainable code that your future self will thank you for.',
    'Finally, stay curious and keep learning - the web never stops evolving! 🚀'
  ];

  // Convert to thread objects
  const threadObjects = createThreadFromTweets(tweets);
  console.log('Thread objects created:');
  threadObjects.forEach((tweet, index) => {
    console.log(`${index + 1}: ${JSON.stringify(tweet)}`);
  });

  // Convert back to text with different separators
  console.log('\nThread as text (double newline):');
  console.log(threadToText(threadObjects));

  console.log('\nThread as text (numbered list):');
  console.log(threadToText(threadObjects, '\n'));

  console.log('\nThread as text (pipe separated):');
  console.log(threadToText(threadObjects, ' | '));
}

// Demo: Real-world workflow simulation
export function demoRealWorldWorkflow() {
  console.log('\n=== Real-World Workflow Demo ===\n');
  
  // Simulate user input from the Alpine.js app
  const userInput = {
    inputType: 'url',
    urlInput: 'https://medium.com/@developer/understanding-react-hooks',
    textInput: '',
    isUrl: true
  };

  console.log('Step 1: Validate input');
  
  if (userInput.isUrl) {
    const isValidUrl = validateUrl(userInput.urlInput);
    const isSupported = isSupportedDomain(userInput.urlInput);
    
    console.log(`URL validation: ${isValidUrl}`);
    console.log(`Supported domain: ${isSupported}`);
    
    if (!isValidUrl) {
      console.log('❌ Invalid URL - would show error to user');
      return;
    }
    
    if (!isSupported) {
      console.log('⚠️ Unsupported domain - would warn user');
    }
  }

  console.log('\nStep 2: Simulate content extraction (normally done by backend)');
  const extractedContent = `
    Understanding React Hooks: A Comprehensive Guide
    
    React Hooks revolutionized how we write functional components by providing state and lifecycle methods without classes.
    
    The useState Hook allows functional components to have state. It returns an array with the current state value and a setter function.
    
    The useEffect Hook handles side effects like API calls, subscriptions, and DOM manipulation. It combines componentDidMount, componentDidUpdate, and componentWillUnmount.
    
    Custom Hooks let you extract component logic into reusable functions. They're just JavaScript functions that use other Hooks.
    
    Rules of Hooks: Only call Hooks at the top level and only from React functions. This ensures they're called in the same order every time.
  `;

  console.log('Content extracted, length:', extractedContent.length);

  console.log('\nStep 3: Process content into thread');
  const cleanedContent = cleanContent(extractedContent);
  const tweets = splitIntoTweets(cleanedContent, {
    maxLength: 280,
    preserveWords: true,
    addNumbers: true
  });

  console.log(`Generated ${tweets.length} tweets`);

  console.log('\nStep 4: Validate all tweets');
  let hasErrors = false;
  tweets.forEach((tweet, index) => {
    const validation = validateTweetLength(tweet);
    if (!validation.isValid) {
      console.log(`❌ Tweet ${index + 1} exceeds limit: ${validation.characterCount} chars`);
      hasErrors = true;
    } else if (validation.isWarning) {
      console.log(`⚠️ Tweet ${index + 1} near limit: ${validation.characterCount} chars`);
    }
  });

  if (!hasErrors) {
    console.log('✅ All tweets are valid');
  }

  console.log('\nStep 5: Create final thread structure');
  const finalThread = createThreadFromTweets(tweets);
  const stats = getThreadStats(finalThread);

  console.log('Final thread statistics:');
  console.log(`- ${stats.totalTweets} tweets`);
  console.log(`- ${stats.totalCharacters} total characters`);
  console.log(`- ${stats.averageLength} average characters per tweet`);
  console.log(`- ${stats.tweetsOverLimit} tweets over limit`);
  console.log(`- ${stats.tweetsNearLimit} tweets near limit`);

  return finalThread;
}

// Run all demos
export function runAllDemos() {
  console.clear();
  console.log('🧵 THREADR UTILITIES DEMO 🧵');
  console.log('============================');
  
  demoBasicThreadGeneration();
  demoUrlValidation();
  demoCharacterCounting();
  demoCustomSplitting();
  demoThreadConversion();
  demoRealWorldWorkflow();
  
  console.log('\n🎉 All demos completed! 🎉');
  console.log('\nTo use these utilities in your components:');
  console.log('import { splitIntoTweets, validateUrl } from "@/lib/utils/thread";');
}

// Export for easy testing
export const demoFunctions = {
  demoBasicThreadGeneration,
  demoUrlValidation,
  demoCharacterCounting,
  demoCustomSplitting,
  demoThreadConversion,
  demoRealWorldWorkflow,
  runAllDemos
};

// Auto-run demos if this file is executed directly
if (typeof require !== 'undefined' && require.main === module) {
  runAllDemos();
}