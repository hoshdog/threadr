import { z } from 'zod';

// Authentication schemas
export const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

export const registerSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  confirmPassword: z.string(),
  username: z.string().min(2, 'Username must be at least 2 characters').optional(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

export const forgotPasswordSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
});

export const resetPasswordSchema = z.object({
  password: z.string().min(6, 'Password must be at least 6 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

export const changePasswordSchema = z.object({
  currentPassword: z.string().min(1, 'Current password is required'),
  newPassword: z.string().min(6, 'New password must be at least 6 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

// Thread generation schemas
export const generateThreadSchema = z.object({
  content: z.string().optional(),
  url: z.string().url('Please enter a valid URL').optional(),
  customPrompt: z.string().max(500, 'Custom prompt must be less than 500 characters').optional(),
}).refine((data) => data.content || data.url, {
  message: 'Either content or URL is required',
  path: ['content'],
});

export const saveThreadSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title must be less than 200 characters'),
  tweets: z.array(z.object({
    id: z.string(),
    content: z.string().min(1, 'Tweet content is required').max(280, 'Tweet must be 280 characters or less'),
    order: z.number().int().positive(),
    characterCount: z.number().int().min(0).max(280),
  })).min(1, 'At least one tweet is required'),
  isPublic: z.boolean().default(false),
  tags: z.array(z.string()).optional(),
  sourceUrl: z.string().url().optional(),
  sourceContent: z.string().optional(),
});

// Profile update schema
export const updateProfileSchema = z.object({
  username: z.string().min(2, 'Username must be at least 2 characters').max(50, 'Username must be less than 50 characters').optional(),
  email: z.string().email('Please enter a valid email address').optional(),
});

// Team schemas
export const createTeamSchema = z.object({
  name: z.string().min(2, 'Team name must be at least 2 characters').max(100, 'Team name must be less than 100 characters'),
  description: z.string().max(500, 'Description must be less than 500 characters').optional(),
});

export const addTeamMemberSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  role: z.enum(['admin', 'member']).default('member'),
});

// Utility validation functions
export const isValidEmail = (email: string): boolean => {
  return z.string().email().safeParse(email).success;
};

export const isValidUrl = (url: string): boolean => {
  return z.string().url().safeParse(url).success;
};

export const isValidPassword = (password: string): boolean => {
  return password.length >= 6;
};

export const validateTweetLength = (content: string): { isValid: boolean; length: number } => {
  const length = content.length;
  return {
    isValid: length > 0 && length <= 280,
    length,
  };
};

export const sanitizeInput = (input: string): string => {
  return input.trim().replace(/\s+/g, ' ');
};

export const extractDomain = (url: string): string | null => {
  try {
    const domain = new URL(url).hostname;
    return domain.replace('www.', '');
  } catch {
    return null;
  }
};

export const validateThreadTitle = (title: string): string | null => {
  const sanitized = sanitizeInput(title);
  if (!sanitized) return 'Title is required';
  if (sanitized.length > 200) return 'Title must be less than 200 characters';
  return null;
};