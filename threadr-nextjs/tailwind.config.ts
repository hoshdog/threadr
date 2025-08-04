import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Twitter/X exact color palette - matching Alpine.js x- prefixed colors
        'x-black': '#000000',
        'x-dark': '#15202b', 
        'x-darker': '#192734', 
        'x-darkest': '#22303c',
        'x-gray': '#8899ac',
        'x-light-gray': '#e1e8ed',
        'x-blue': '#1d9bf0',
        'x-blue-hover': '#1a8cd8',
        'x-border': '#38444d',
        'x-hover': '#1d2d3a',
        
        // Legacy twitter- prefix (keep for backward compatibility)
        'twitter-blue': '#1d9bf0',
        'twitter-dark': '#15202b',
        'twitter-black': '#000000',
        'twitter-gray': '#8899ac',
        'twitter-border': '#38444d',
        'twitter-hover': '#1a8cd8',
        'twitter-light-gray': '#f7f9fa',
        'twitter-text-gray': '#536471',
        
        // Primary colors using Twitter blue
        primary: {
          DEFAULT: '#1d9bf0',
          50: '#e8f4fd',
          100: '#d1e9fb', 
          200: '#a3d3f7',
          300: '#75bdf3',
          400: '#47a7ef',
          500: '#1d9bf0',
          600: '#1a8cd8',
          700: '#177dc0',
          800: '#146ea8',
          900: '#115f90',
          950: '#0d4a78',
        },
        
        // Success/Error states
        success: {
          50: '#f0fdf4',
          500: '#22c55e',
          600: '#16a34a',
        },
        error: {
          50: '#fef2f2',
          500: '#f4212e',
          600: '#dc1f2e',
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          600: '#d97706',
        },
        
        // Semantic colors mapped to CSS variables
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        muted: 'var(--muted)',
        'muted-foreground': 'var(--muted-foreground)',
        border: 'var(--border)',
        input: 'var(--input)',
        ring: 'var(--ring)',
        accent: 'var(--accent)',
        'accent-foreground': 'var(--accent-foreground)',
        secondary: 'var(--secondary)',
        'secondary-foreground': 'var(--secondary-foreground)',
        destructive: 'var(--destructive)',
        'destructive-foreground': 'var(--destructive-foreground)',
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Helvetica',
          'Arial',
          'sans-serif',
        ],
        mono: [
          'Monaco',
          'Cascadia Code',
          'Segoe UI Mono',
          'Roboto Mono',
          'monospace',
        ],
      },
      fontSize: {
        /* Twitter/X exact font sizes */
        'xs': '13px',   // Twitter small text
        'sm': '14px',   // Twitter secondary text
        'base': '15px', // Twitter body text
        'lg': '17px',   // Twitter large text
        'xl': '20px',   // Twitter heading 3
        '2xl': '23px',  // Twitter heading 2
        '3xl': '28px',  // Twitter heading 1.5
        '4xl': '34px',  // Twitter large heading
      },
      spacing: {
        /* Twitter/X tight spacing scale */
        '1': '4px',     // Twitter micro spacing
        '2': '8px',     // Twitter small spacing
        '3': '12px',    // Twitter medium spacing
        '4': '16px',    // Twitter standard spacing
        '5': '20px',    // Twitter large spacing
        '6': '24px',    // Twitter extra large spacing
        '8': '32px',    // Twitter section spacing
        '18': '4.5rem',
        '88': '22rem',
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
  darkMode: 'class',
};

export default config;
