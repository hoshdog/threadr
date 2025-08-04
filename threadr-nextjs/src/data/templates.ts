/**
 * Templates Data
 * Extracted from the Alpine.js Threadr app and converted to TypeScript
 * 
 * This file contains all 16 thread templates with proper TypeScript typing
 * and helper functions for filtering and manipulation.
 */

// Template Category Constants
export const TEMPLATE_CATEGORIES = {
  ALL: 'all',
  BUSINESS: 'Business',
  EDUCATIONAL: 'Educational',
  PERSONAL: 'Personal'
} as const;

export type TemplateCategory = typeof TEMPLATE_CATEGORIES[keyof typeof TEMPLATE_CATEGORIES];

// Template Interface
export interface Template {
  id: string;
  name: string;
  description: string;
  category: Exclude<TemplateCategory, 'all'>; // All categories except 'all'
  isPro: boolean;
  popularity: number;
  variables: string[];
  structure: string[];
}

// Template Form Data Interface
export interface TemplateFormData {
  [key: string]: string;
}

// Filtered Templates Result Interface
export interface FilteredTemplatesResult {
  templates: Template[];
  freeCount: number;
  proCount: number;
  totalCount: number;
}

// Legacy interface for backward compatibility
export interface TemplateData extends Template {}

export const templateCategories = [
  { id: 'all', name: 'All Templates', count: 16 },
  { id: 'Business', name: 'Business', count: 6 },
  { id: 'Educational', name: 'Educational', count: 6 },
  { id: 'Personal', name: 'Personal', count: 4 },
] as const;

export const templates: Template[] = [
  {
    id: 'product-launch',
    name: 'Product Launch Announcement',
    description: 'Announce your new product with excitement and key features',
    category: 'Business',
    isPro: false,
    popularity: 95,
    variables: ['product_name', 'key_feature_1', 'key_feature_2', 'key_feature_3', 'launch_date', 'website_url'],
    structure: [
      "🚀 Big news! We're launching {product_name}!",
      "After months of hard work, we're excited to share what we've built:",
      "✨ {key_feature_1}",
      "⚡ {key_feature_2}", 
      "🔥 {key_feature_3}",
      "Mark your calendars - {launch_date} is the day!",
      "Ready to try it? Check it out: {website_url}",
      "Retweet if you're as excited as we are! 🎉"
    ]
  },
  {
    id: 'tutorial-guide',
    name: 'Tutorial/How-to Guide',
    description: 'Step-by-step guide to teach your audience something valuable',
    category: 'Educational',
    isPro: false,
    popularity: 88,
    variables: ['topic', 'step_1', 'step_2', 'step_3', 'step_4', 'pro_tip', 'resource_link'],
    structure: [
      "🧵 How to {topic} (a step-by-step guide)",
      "I've helped 100+ people master this. Here's exactly how to do it:",
      "Step 1: {step_1}",
      "Step 2: {step_2}",
      "Step 3: {step_3}",
      "Step 4: {step_4}",
      "💡 Pro tip: {pro_tip}",
      "Want more resources? Check out: {resource_link}",
      "Found this helpful? Share it with others! ↗️"
    ]
  },
  {
    id: 'personal-story',
    name: 'Personal Story/Journey',
    description: 'Share your personal experience or transformation story',
    category: 'Personal',
    isPro: false,
    popularity: 92,
    variables: ['time_period', 'starting_point', 'challenge', 'turning_point', 'outcome', 'lesson_learned'],
    structure: [
      "{time_period} ago, I was {starting_point}",
      "I was struggling with {challenge} and felt stuck.",
      "Then something changed: {turning_point}",
      "Fast forward to today: {outcome}",
      "The biggest lesson I learned: {lesson_learned}",
      "Your current situation is not your final destination.",
      "What's one small step you can take today? 💪"
    ]
  },
  {
    id: 'news-breakdown',
    name: 'Industry News Breakdown',
    description: 'Analyze and explain breaking news or industry updates',
    category: 'Business',
    isPro: true,
    popularity: 76,
    variables: ['news_topic', 'key_fact_1', 'key_fact_2', 'impact', 'prediction', 'action_item'],
    structure: [
      "🔥 Breaking: {news_topic}",
      "Here's what you need to know (and why it matters):",
      "Key facts:",
      "• {key_fact_1}",
      "• {key_fact_2}",
      "Why this matters: {impact}",
      "My prediction: {prediction}",
      "What should you do? {action_item}",
      "What are your thoughts on this? 👇"
    ]
  },
  {
    id: 'tips-tricks',
    name: 'Tips and Tricks List',
    description: 'Share actionable tips and tricks about your expertise',
    category: 'Educational',
    isPro: false,
    popularity: 90,
    variables: ['topic', 'tip_1', 'tip_2', 'tip_3', 'tip_4', 'tip_5', 'bonus_tip'],
    structure: [
      "5 {topic} tips that changed my game:",
      "1. {tip_1}",
      "2. {tip_2}",
      "3. {tip_3}",
      "4. {tip_4}",
      "5. {tip_5}",
      "Bonus tip: {bonus_tip}",
      "Which tip resonates most with you? Let me know! 👇"
    ]
  },
  {
    id: 'case-study',
    name: 'Case Study Analysis',
    description: 'Deep dive into a successful project or campaign',
    category: 'Business',
    isPro: true,
    popularity: 71,
    variables: ['company_name', 'challenge', 'strategy', 'execution', 'results', 'takeaway'],
    structure: [
      "Case Study: How {company_name} solved {challenge}",
      "The Problem: {challenge} was costing them thousands monthly.",
      "The Strategy: {strategy}",
      "The Execution: {execution}",
      "The Results: {results}",
      "Key Takeaway: {takeaway}",
      "Apply this to your business and watch what happens 📈"
    ]
  },
  {
    id: 'book-summary',
    name: 'Book/Article Summary',
    description: 'Summarize key insights from books or articles',
    category: 'Educational',
    isPro: false,
    popularity: 84,
    variables: ['title', 'author', 'main_insight', 'insight_1', 'insight_2', 'insight_3', 'actionable_takeaway'],
    structure: [
      "Just finished \"{title}\" by {author}",
      "The main insight that blew my mind: {main_insight}",
      "3 key takeaways:",
      "📖 {insight_1}",
      "💡 {insight_2}",
      "🔥 {insight_3}",
      "Most actionable takeaway: {actionable_takeaway}",
      "10/10 recommend if you want to level up! 📚"
    ]
  },
  {
    id: 'controversial-opinion',
    name: 'Controversial Opinion/Hot Take',
    description: 'Share a bold opinion that sparks discussion',
    category: 'Personal',
    isPro: true,
    popularity: 68,
    variables: ['opinion', 'reason_1', 'reason_2', 'counterargument', 'final_thought'],
    structure: [
      "Unpopular opinion: {opinion}",
      "Here's why I believe this:",
      "Reason 1: {reason_1}",
      "Reason 2: {reason_2}",
      "I know some will say: {counterargument}",
      "But here's the thing: {final_thought}",
      "Change my mind (or agree) in the comments 👇",
      "RT if you think I'm onto something 🔥"
    ]
  },
  {
    id: 'behind-scenes',
    name: 'Behind the Scenes',
    description: 'Give followers a peek behind the curtain',
    category: 'Personal', 
    isPro: false,
    popularity: 82,
    variables: ['project', 'challenge', 'solution', 'unexpected_learning', 'current_status'],
    structure: [
      "Behind the scenes of {project}:",
      "What you see: The polished final result",
      "What you don't see: {challenge}",
      "How we solved it: {solution}",
      "Plot twist: {unexpected_learning}",
      "Current status: {current_status}",
      "The messy middle is where the magic happens ✨"
    ]
  },
  {
    id: 'resource-compilation',
    name: 'Resource Compilation',
    description: 'Curated list of valuable resources and tools',
    category: 'Educational',
    isPro: true,
    popularity: 79,
    variables: ['topic', 'resource_1', 'resource_2', 'resource_3', 'resource_4', 'bonus_resource'],
    structure: [
      "Ultimate {topic} resource list (bookmark this 🔖)",
      "After 5+ years, these are my go-to resources:",
      "🔗 {resource_1}",
      "⚡ {resource_2}",
      "💎 {resource_3}",
      "🚀 {resource_4}",
      "Bonus: {bonus_resource} (my secret weapon)",
      "Save this tweet - you'll thank me later!",
      "What would you add to this list? 👇"
    ]
  },
  {
    id: 'qa-format',
    name: 'Q&A Format',
    description: 'Answer common questions in your field',
    category: 'Educational',
    isPro: false,
    popularity: 75,
    variables: ['topic', 'question_1', 'answer_1', 'question_2', 'answer_2', 'question_3', 'answer_3'],
    structure: [
      "Common {topic} questions (answered):",
      "Q: {question_1}",
      "A: {answer_1}",
      "Q: {question_2}",
      "A: {answer_2}",
      "Q: {question_3}",
      "A: {answer_3}",
      "Got more questions? Drop them below! 👇"
    ]
  },
  {
    id: 'problem-solution',
    name: 'Problem/Solution',
    description: 'Present a common problem and your solution',
    category: 'Business',
    isPro: false,
    popularity: 86,
    variables: ['problem', 'why_common', 'solution', 'benefit_1', 'benefit_2', 'how_to_start'],
    structure: [
      "Problem: {problem}",
      "This affects 80% of people because {why_common}",
      "The solution: {solution}",
      "Benefits:",
      "✅ {benefit_1}",
      "✅ {benefit_2}",
      "How to start: {how_to_start}",
      "Don't let this problem hold you back any longer 💪"
    ]
  },
  {
    id: 'transformation',
    name: 'Before/After Transformation',
    description: 'Showcase a dramatic before and after transformation',
    category: 'Personal',
    isPro: true,
    popularity: 89,
    variables: ['timeframe', 'before_state', 'catalyst', 'changes_made', 'after_state', 'key_lesson'],
    structure: [
      "{timeframe} transformation thread 🧵",
      "BEFORE: {before_state}",
      "The catalyst: {catalyst}",
      "What changed: {changes_made}",
      "AFTER: {after_state}",
      "Key lesson: {key_lesson}",
      "Your future self is counting on the decisions you make today.",
      "What transformation are you working on? 👇"
    ]
  },
  {
    id: 'myth-busting',
    name: 'Myth Busting',
    description: 'Debunk common myths in your industry',  
    category: 'Educational',
    isPro: true,
    popularity: 73,
    variables: ['topic', 'myth_1', 'reality_1', 'myth_2', 'reality_2', 'why_myths_persist'],
    structure: [
      "🚫 {topic} myths that need to die:",
      "Myth #1: {myth_1}",
      "Reality: {reality_1}",
      "Myth #2: {myth_2}",
      "Reality: {reality_2}",
      "Why these myths persist: {why_myths_persist}",
      "Stop believing the hype. Focus on what actually works.",
      "What myths would you add to this list? 👇"
    ]
  },
  {
    id: 'future-predictions',
    name: 'Future Predictions',
    description: 'Share your predictions about industry trends',
    category: 'Business',
    isPro: true,
    popularity: 67,
    variables: ['industry', 'prediction_1', 'evidence_1', 'prediction_2', 'evidence_2', 'timeline', 'preparation_tip'],
    structure: [
      "My {industry} predictions for the next 2 years:",
      "Prediction 1: {prediction_1}",
      "Evidence: {evidence_1}",
      "Prediction 2: {prediction_2}",
      "Evidence: {evidence_2}",
      "Timeline: {timeline}",
      "How to prepare: {preparation_tip}",
      "RemindMe! 2 years to see how accurate these were 📅"
    ]
  }
];

// Helper Functions

/**
 * Get template by ID
 */
export function getTemplateById(id: string): Template | undefined {
  return templates.find(template => template.id === id);
}

/**
 * Filter templates by category and search term
 */
export function filterTemplates(
  category: TemplateCategory = TEMPLATE_CATEGORIES.ALL,
  searchTerm: string = '',
  isPremiumUser: boolean = false
): FilteredTemplatesResult {
  let filtered = templates;

  // Filter by category
  if (category !== TEMPLATE_CATEGORIES.ALL) {
    filtered = filtered.filter(template => template.category === category);
  }

  // Filter by search term
  if (searchTerm.trim()) {
    const search = searchTerm.toLowerCase().trim();
    filtered = filtered.filter(template =>
      template.name.toLowerCase().includes(search) ||
      template.description.toLowerCase().includes(search) ||
      template.category.toLowerCase().includes(search)
    );
  }

  // Filter by premium access
  if (!isPremiumUser) {
    filtered = filtered.filter(template => !template.isPro);
  }

  // Count templates
  const freeCount = filtered.filter(template => !template.isPro).length;
  const proCount = filtered.filter(template => template.isPro).length;

  return {
    templates: filtered,
    freeCount,
    proCount,
    totalCount: filtered.length
  };
}

/**
 * Get templates by category
 */
export function getTemplatesByCategory(category: Exclude<TemplateCategory, 'all'>): Template[] {
  return templates.filter(template => template.category === category);
}

/**
 * Get free templates only
 */
export function getFreeTemplates(): Template[] {
  return templates.filter(template => !template.isPro);
}

/**
 * Get pro templates only
 */
export function getProTemplates(): Template[] {
  return templates.filter(template => template.isPro);
}

/**
 * Get templates sorted by popularity
 */
export function getTemplatesByPopularity(descending: boolean = true): Template[] {
  return [...templates].sort((a, b) => 
    descending ? b.popularity - a.popularity : a.popularity - b.popularity
  );
}

/**
 * Get all unique categories
 */
export function getUniqueCategories(): Exclude<TemplateCategory, 'all'>[] {
  const categories = templates.map(template => template.category);
  return Array.from(new Set(categories));
}

/**
 * Generate thread from template with form data
 */
export function generateThreadFromTemplate(
  template: Template, 
  formData: TemplateFormData
): string[] {
  return template.structure.map(tweet => {
    let processedTweet = tweet;
    
    // Replace all variables in the tweet
    template.variables.forEach(variable => {
      const value = formData[variable] || `{${variable}}`;
      const regex = new RegExp(`\\{${variable}\\}`, 'g');
      processedTweet = processedTweet.replace(regex, value);
    });
    
    return processedTweet;
  });
}

/**
 * Validate template form data
 */
export function validateTemplateFormData(
  template: Template, 
  formData: TemplateFormData
): { isValid: boolean; missingFields: string[] } {
  const missingFields = template.variables.filter(variable => 
    !formData[variable] || formData[variable].trim() === ''
  );
  
  return {
    isValid: missingFields.length === 0,
    missingFields
  };
}

/**
 * Get template statistics
 */
export function getTemplateStats() {
  const totalTemplates = templates.length;
  const freeTemplates = getFreeTemplates().length;
  const proTemplates = getProTemplates().length;
  const averagePopularity = Math.round(
    templates.reduce((sum, template) => sum + template.popularity, 0) / totalTemplates
  );
  
  const categoryCounts = getUniqueCategories().reduce((acc, category) => {
    acc[category] = getTemplatesByCategory(category).length;
    return acc;
  }, {} as Record<string, number>);

  return {
    total: totalTemplates,
    free: freeTemplates,
    pro: proTemplates,
    averagePopularity,
    categoryCounts
  };
}

// Legacy helper functions for backward compatibility
export const getTemplatesByCategory_Legacy = (category: string) => {
  if (category === 'all') return templates;
  return templates.filter(template => template.category === category);
};

export const getPremiumTemplates = () => {
  return templates.filter(template => template.isPro);
};

export const searchTemplates = (query: string) => {
  const searchTerm = query.toLowerCase();
  return templates.filter(template => 
    template.name.toLowerCase().includes(searchTerm) ||
    template.description.toLowerCase().includes(searchTerm) ||
    template.category.toLowerCase().includes(searchTerm)
  );
};

export const getPopularTemplates = (limit?: number) => {
  const sorted = [...templates].sort((a, b) => b.popularity - a.popularity);
  return limit ? sorted.slice(0, limit) : sorted;
};

// Legacy export for backward compatibility
export const templatesData = templates;

// Export default templates array
export default templates;