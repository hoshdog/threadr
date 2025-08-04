'use client';

import Image from 'next/image';
import { cn } from '@/lib/utils';

interface LogoProps {
  className?: string;
  variant?: 'white' | 'black';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showText?: boolean;
}

const sizeClasses = {
  sm: 'h-6 w-auto',
  md: 'h-8 w-auto',
  lg: 'h-10 w-auto',
  xl: 'h-12 w-auto',
};

export default function Logo({ 
  className, 
  variant = 'white', 
  size = 'md',
  showText = false 
}: LogoProps) {
  const logoSrc = variant === 'white' 
    ? '/threadrLogo_White_Cropped.PNG' 
    : '/threadrLogo_Black_Cropped.PNG';

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <Image
        src={logoSrc}
        alt="Threadr Logo"
        width={200}
        height={50}
        className={cn(sizeClasses[size], 'object-contain')}
        priority
      />
      {showText && (
        <span className={cn(
          'font-bold text-lg',
          variant === 'white' ? 'text-white' : 'text-gray-900'
        )}>
          Threadr
        </span>
      )}
    </div>
  );
}