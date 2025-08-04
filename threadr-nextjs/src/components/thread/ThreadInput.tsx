'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

interface ThreadInputProps {
  onGenerate: (input: string, type: 'url' | 'text') => void;
  loading?: boolean;
  disabled?: boolean;
}

export const ThreadInput: React.FC<ThreadInputProps> = ({
  onGenerate,
  loading = false,
  disabled = false
}) => {
  const [inputType, setInputType] = useState<'url' | 'text'>('url');
  const [urlInput, setUrlInput] = useState('');
  const [textInput, setTextInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const input = inputType === 'url' ? urlInput : textInput;
    if (input.trim()) {
      onGenerate(input.trim(), inputType);
    }
  };

  const isFormValid = inputType === 'url' ? urlInput.trim() : textInput.trim();

  return (
    <div className="bg-[#15202b] rounded-2xl p-6 mb-6 border border-[#38444d]">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Tab Selector */}
        <div className="flex justify-center">
          <div className="inline-flex rounded-full bg-[#15202b] border border-[#38444d] p-2">
            <button
              type="button"
              onClick={() => setInputType('url')}
              className={cn(
                'px-6 py-2 rounded-full text-sm font-medium transition-all duration-200',
                inputType === 'url'
                  ? 'bg-[#1d9bf0] text-white shadow-sm'
                  : 'text-[#8899ac] hover:text-white hover:bg-[#1d2d3a]'
              )}
            >
              Article URL
            </button>
            <button
              type="button"
              onClick={() => setInputType('text')}
              className={cn(
                'px-6 py-2 rounded-full text-sm font-medium transition-all duration-200',
                inputType === 'text'
                  ? 'bg-[#1d9bf0] text-white shadow-sm'
                  : 'text-[#8899ac] hover:text-white hover:bg-[#1d2d3a]'
              )}
            >
              Raw Text
            </button>
          </div>
        </div>

        {/* URL Input */}
        {inputType === 'url' && (
          <div>
            <input
              type="url"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              placeholder="Paste article URL here (Medium, Dev.to, Substack, etc.)"
              disabled={disabled || loading}
              className={cn(
                'w-full px-4 py-4 rounded-xl text-lg bg-[#000000] border border-[#38444d]',
                'text-white placeholder:text-[#8899ac]',
                'focus:outline-none focus:ring-2 focus:ring-[#1d9bf0] focus:border-transparent',
                'transition-all duration-200',
                'disabled:opacity-50 disabled:cursor-not-allowed'
              )}
            />
          </div>
        )}

        {/* Text Input */}
        {inputType === 'text' && (
          <div>
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Paste your content here... (articles, blog posts, long-form content)"
              disabled={disabled || loading}
              rows={6}
              className={cn(
                'w-full px-4 py-4 rounded-xl text-lg bg-[#000000] border border-[#38444d]',
                'text-white placeholder:text-[#8899ac] resize-none',
                'focus:outline-none focus:ring-2 focus:ring-[#1d9bf0] focus:border-transparent',
                'transition-all duration-200',
                'disabled:opacity-50 disabled:cursor-not-allowed'
              )}
            />
          </div>
        )}

        {/* Generate Button */}
        <Button
          type="submit"
          disabled={!isFormValid || disabled || loading}
          loading={loading}
          className={cn(
            'w-full mt-8 py-4 px-8 rounded-full text-lg font-bold',
            'bg-[#1d9bf0] hover:bg-[#1a8cd8] text-white',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            'transition-all duration-200 transform active:scale-[0.98]'
          )}
        >
          {loading ? 'Generating Thread...' : 'Generate Thread'}
        </Button>
      </form>
    </div>
  );
};