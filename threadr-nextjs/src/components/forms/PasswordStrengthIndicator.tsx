'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface PasswordStrengthIndicatorProps {
  password: string;
  className?: string;
}

interface PasswordStrength {
  score: number;
  label: string;
  color: string;
  requirements: Array<{
    met: boolean;
    text: string;
  }>;
}

export function PasswordStrengthIndicator({ password, className }: PasswordStrengthIndicatorProps) {
  const getPasswordStrength = (password: string): PasswordStrength => {
    const requirements = [
      {
        met: password.length >= 8,
        text: 'At least 8 characters',
      },
      {
        met: /[a-z]/.test(password),
        text: 'One lowercase letter',
      },
      {
        met: /[A-Z]/.test(password),
        text: 'One uppercase letter',
      },
      {
        met: /\d/.test(password),
        text: 'One number',
      },
      {
        met: /[^a-zA-Z0-9]/.test(password),
        text: 'One special character',
      },
    ];

    const metCount = requirements.filter(req => req.met).length;
    
    let score = 0;
    let label = '';
    let color = '';

    if (metCount <= 1) {
      score = 1;
      label = 'Very Weak';
      color = 'bg-destructive';
    } else if (metCount === 2) {
      score = 2;
      label = 'Weak';
      color = 'bg-orange-500';
    } else if (metCount === 3) {
      score = 3;
      label = 'Fair';
      color = 'bg-yellow-500';
    } else if (metCount === 4) {
      score = 4;
      label = 'Good';
      color = 'bg-blue-500';
    } else {
      score = 5;
      label = 'Strong';
      color = 'bg-green-500';
    }

    return { score, label, color, requirements };
  };

  const strength = getPasswordStrength(password);

  if (!password) return null;

  return (
    <div className={cn('space-y-2', className)}>
      {/* Strength Bar */}
      <div className="space-y-1">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">Password strength</span>
          <span className={cn(
            'text-xs font-medium',
            strength.score <= 2 ? 'text-destructive' : 
            strength.score <= 3 ? 'text-yellow-600' : 
            strength.score === 4 ? 'text-blue-600' : 'text-green-600'
          )}>
            {strength.label}
          </span>
        </div>
        
        <div className="flex space-x-1">
          {[1, 2, 3, 4, 5].map((step) => (
            <div
              key={step}
              className={cn(
                'h-1.5 flex-1 rounded-full transition-colors duration-300',
                step <= strength.score ? strength.color : 'bg-muted'
              )}
            />
          ))}
        </div>
      </div>

      {/* Requirements List */}
      <div className="space-y-1">
        {strength.requirements.map((requirement, index) => (
          <div key={index} className="flex items-center space-x-2">
            <div
              className={cn(
                'h-3 w-3 rounded-full flex items-center justify-center text-[10px] font-bold',
                requirement.met
                  ? 'bg-green-100 text-green-700 border border-green-200'
                  : 'bg-muted text-muted-foreground border border-border'
              )}
            >
              {requirement.met ? '✓' : '·'}
            </div>
            <span
              className={cn(
                'text-xs transition-colors',
                requirement.met ? 'text-green-700' : 'text-muted-foreground'
              )}
            >
              {requirement.text}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}