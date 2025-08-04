'use client';

import { useState } from 'react';
import { Input } from '@/components/ui';

interface Category {
  id: string;
  name: string;
  count: number;
}

interface TemplateFiltersProps {
  categories: readonly Category[];
  selectedCategory: string;
  onCategoryChange: (category: string) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  templateCount: number;
  totalCount: number;
}

export default function TemplateFilters({
  categories,
  selectedCategory,
  onCategoryChange,
  searchQuery,
  onSearchChange,
  templateCount,
  totalCount,
}: TemplateFiltersProps) {
  const [showAllCategories, setShowAllCategories] = useState(false);
  
  const visibleCategories = showAllCategories 
    ? categories 
    : categories.slice(0, 4);

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
      {/* Search */}
      <div className="mb-6">
        <div className="relative max-w-md">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <Input
            type="text"
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Category Filters */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-900 mb-3">Categories</h3>
        <div className="flex flex-wrap gap-2">
          {visibleCategories.map((category) => (
            <button
              key={category.id}
              onClick={() => onCategoryChange(category.id)}
              className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                selectedCategory === category.id
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {category.name}
              <span className={`ml-2 px-2 py-0.5 rounded-full text-xs ${
                selectedCategory === category.id
                  ? 'bg-indigo-500 text-indigo-100'
                  : 'bg-gray-200 text-gray-600'
              }`}>
                {category.count}
              </span>
            </button>
          ))}
          
          {categories.length > 4 && (
            <button
              onClick={() => setShowAllCategories(!showAllCategories)}
              className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium text-indigo-600 hover:bg-indigo-50 transition-colors"
            >
              {showAllCategories ? (
                <>
                  <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                  </svg>
                  Show Less
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                  Show More
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Results Info */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
        <div className="text-sm text-gray-600">
          {searchQuery ? (
            <>
              Showing <span className="font-medium">{templateCount}</span> results for "{searchQuery}"
              {selectedCategory !== 'all' && (
                <> in <span className="font-medium">{categories.find(c => c.id === selectedCategory)?.name}</span></>
              )}
            </>
          ) : (
            <>
              Showing <span className="font-medium">{templateCount}</span> of <span className="font-medium">{totalCount}</span> templates
            </>
          )}
        </div>

        {(searchQuery || selectedCategory !== 'all') && (
          <button
            onClick={() => {
              onSearchChange('');
              onCategoryChange('all');
            }}
            className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
          >
            Clear all filters
          </button>
        )}
      </div>
    </div>
  );
}