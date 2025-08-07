'use client';

import Image from 'next/image';
import Link from 'next/link';
import { cn } from '@/lib/utils';

interface LogoProps {
  className?: string;
  variant?: 'white' | 'black' | 'auto';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  showText?: boolean;
  clickable?: boolean;
  href?: string;
}

const sizeClasses = {
  xs: 'h-5 w-auto',
  sm: 'h-6 w-auto',
  md: 'h-8 w-auto',
  lg: 'h-10 w-auto',
  xl: 'h-12 w-auto',
  '2xl': 'h-16 w-auto',
};

export default function Logo({ 
  className, 
  variant = 'auto', 
  size = 'md',
  showText = false,
  clickable = false,
  href = '/'
}: LogoProps) {
  // Auto-detect variant based on dark mode if not specified
  const logoSrc = variant === 'black' || (variant === 'auto')
    ? '/threadrLogo_Black_Cropped.PNG'
    : '/threadrLogo_White_Cropped.PNG';

  const logoElement = (
    <div className={cn(
      'flex items-center gap-3 transition-all duration-200',
      clickable && 'hover:scale-105 cursor-pointer',
      className
    )}>
      <Image
        src={logoSrc}
        alt="Threadr - Convert Articles to Twitter Threads"
        width={200}
        height={50}
        className={cn(sizeClasses[size], 'object-contain drop-shadow-sm')}
        priority
      />
      {showText && (
        <span className={cn(
          'font-bold select-none',
          {
            'text-sm': size === 'xs' || size === 'sm',
            'text-base': size === 'md',
            'text-lg': size === 'lg',
            'text-xl': size === 'xl',
            'text-2xl': size === '2xl',
          },
          variant === 'white' ? 'text-white' : 'text-gray-900 dark:text-white'
        )}>
          Threadr
        </span>
      )}
    </div>
  );

  if (clickable) {
    return (
      <Link href={href} className="inline-block">
        {logoElement}
      </Link>
    );
  }

  return logoElement;
}