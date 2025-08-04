'use client';

import React, { useState } from 'react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { cn } from '@/lib/utils';
import { 
  Search, 
  Calendar, 
  Filter, 
  X, 
  Star, 
  Archive,
  ChevronDown,
  SlidersHorizontal
} from 'lucide-react';
import type { HistoryFilters, DateFilter, StatusFilter, SortOption } from '@/app/(dashboard)/history/page';

interface ThreadHistoryFiltersProps {
  filters: HistoryFilters;
  onFiltersChange: (filters: Partial<HistoryFilters>) => void;
  resultsCount: number;
  isLoading?: boolean;
  className?: string;
}

const dateFilterOptions: { value: DateFilter; label: string; description: string }[] = [
  { value: 'all', label: 'All Time', description: 'Show all threads' },
  { value: 'today', label: 'Today', description: 'Created today' },
  { value: 'week', label: 'This Week', description: 'Last 7 days' },
  { value: 'month', label: 'This Month', description: 'Current month' },
];

const statusFilterOptions: { value: StatusFilter; label: string; icon: React.ReactNode }[] = [
  { value: 'all', label: 'All Status', icon: null },
  { value: 'draft', label: 'Drafts', icon: <Archive className="h-4 w-4" /> },
  { value: 'published', label: 'Published', icon: <Star className="h-4 w-4" /> },
  { value: 'archived', label: 'Archived', icon: <Archive className="h-4 w-4" /> },
];

const sortOptions: { value: SortOption; label: string }[] = [
  { value: 'newest', label: 'Newest First' },
  { value: 'oldest', label: 'Oldest First' },
  { value: 'title', label: 'Title A-Z' },
  { value: 'most_tweets', label: 'Most Tweets' },
];

export const ThreadHistoryFilters: React.FC<ThreadHistoryFiltersProps> = ({
  filters,
  onFiltersChange,
  resultsCount,
  isLoading = false,
  className,
}) => {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showDateDropdown, setShowDateDropdown] = useState(false);
  const [showStatusDropdown, setShowStatusDropdown] = useState(false);
  const [showSortDropdown, setShowSortDropdown] = useState(false);

  // Handle search input
  const handleSearchChange = (value: string) => {
    onFiltersChange({ search: value });
  };

  // Handle clear all filters
  const handleClearFilters = () => {
    onFiltersChange({
      search: '',
      dateFilter: 'all',
      statusFilter: 'all',
      sortBy: 'newest',
      showFavorites: false,
    });
  };

  // Check if any filters are active
  const hasActiveFilters = 
    filters.search !== '' ||
    filters.dateFilter !== 'all' ||
    filters.statusFilter !== 'all' ||
    filters.sortBy !== 'newest' ||
    filters.showFavorites;

  // Get active filter count
  const activeFilterCount = [
    filters.search !== '',
    filters.dateFilter !== 'all',
    filters.statusFilter !== 'all',
    filters.showFavorites,
  ].filter(Boolean).length;

  return (
    <div className={cn('space-y-4', className)}>
      {/* Main Filter Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search Input */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search threads by title or content..."
                value={filters.search}
                onChange={(e) => handleSearchChange(e.target.value)}
                className="pl-10 pr-4"
              />
              {filters.search && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSearchChange('')}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>

            {/* Quick Filter Buttons */}
            <div className="flex items-center gap-2 flex-wrap">
              {/* Date Filter */}
              <div className="relative">
                <Button
                  variant={filters.dateFilter !== 'all' ? 'primary' : 'secondary'}
                  size="sm"
                  onClick={() => setShowDateDropdown(!showDateDropdown)}
                  className="flex items-center gap-2"
                >
                  <Calendar className="h-4 w-4" />
                  {dateFilterOptions.find(opt => opt.value === filters.dateFilter)?.label}
                  <ChevronDown className="h-3 w-3" />
                </Button>

                {showDateDropdown && (
                  <div className="absolute top-full left-0 mt-2 bg-background border border-border rounded-lg shadow-lg z-50 min-w-48">
                    {dateFilterOptions.map((option) => (
                      <button
                        key={option.value}
                        onClick={() => {
                          onFiltersChange({ dateFilter: option.value });
                          setShowDateDropdown(false);
                        }}
                        className={cn(
                          "w-full text-left px-4 py-3 hover:bg-accent rounded-lg transition-colors",
                          filters.dateFilter === option.value && "bg-accent font-medium"
                        )}
                      >
                        <div className="font-medium">{option.label}</div>
                        <div className="text-xs text-muted-foreground">{option.description}</div>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Status Filter */}
              <div className="relative">
                <Button
                  variant={filters.statusFilter !== 'all' ? 'primary' : 'secondary'}
                  size="sm"
                  onClick={() => setShowStatusDropdown(!showStatusDropdown)}
                  className="flex items-center gap-2"
                >
                  <Filter className="h-4 w-4" />
                  {statusFilterOptions.find(opt => opt.value === filters.statusFilter)?.label}
                  <ChevronDown className="h-3 w-3" />
                </Button>

                {showStatusDropdown && (
                  <div className="absolute top-full left-0 mt-2 bg-background border border-border rounded-lg shadow-lg z-50 min-w-40">
                    {statusFilterOptions.map((option) => (
                      <button
                        key={option.value}
                        onClick={() => {
                          onFiltersChange({ statusFilter: option.value });
                          setShowStatusDropdown(false);
                        }}
                        className={cn(
                          "w-full text-left px-4 py-2 hover:bg-accent rounded-lg transition-colors flex items-center gap-2",
                          filters.statusFilter === option.value && "bg-accent font-medium"
                        )}
                      >
                        {option.icon}
                        {option.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Favorites Toggle */}
              <Button
                variant={filters.showFavorites ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => onFiltersChange({ showFavorites: !filters.showFavorites })}
                className="flex items-center gap-2"
              >
                <Star className={cn(
                  "h-4 w-4",
                  filters.showFavorites && "fill-current"
                )} />
                Favorites
              </Button>

              {/* Advanced Filters Toggle */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center gap-2"
              >
                <SlidersHorizontal className="h-4 w-4" />
                {showAdvanced ? 'Less' : 'More'}
              </Button>

              {/* Clear Filters */}
              {hasActiveFilters && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleClearFilters}
                  className="text-muted-foreground hover:text-foreground"
                >
                  Clear All
                </Button>
              )}
            </div>
          </div>

          {/* Advanced Filters */}
          {showAdvanced && (
            <div className="mt-4 pt-4 border-t border-border">
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-foreground">Sort by:</span>
                  <div className="relative">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => setShowSortDropdown(!showSortDropdown)}
                      className="flex items-center gap-2"
                    >
                      {sortOptions.find(opt => opt.value === filters.sortBy)?.label}
                      <ChevronDown className="h-3 w-3" />
                    </Button>

                    {showSortDropdown && (
                      <div className="absolute top-full left-0 mt-2 bg-background border border-border rounded-lg shadow-lg z-50 min-w-40">
                        {sortOptions.map((option) => (
                          <button
                            key={option.value}
                            onClick={() => {
                              onFiltersChange({ sortBy: option.value });
                              setShowSortDropdown(false);
                            }}
                            className={cn(
                              "w-full text-left px-4 py-2 hover:bg-accent rounded-lg transition-colors",
                              filters.sortBy === option.value && "bg-accent font-medium"
                            )}
                          >
                            {option.label}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Results Summary */}
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <div className="flex items-center gap-4">
          <span>
            {isLoading ? 'Loading...' : `${resultsCount.toLocaleString()} thread${resultsCount !== 1 ? 's' : ''} found`}
          </span>
          
          {activeFilterCount > 0 && (
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-primary/10 text-primary rounded-full text-xs">
              <Filter className="h-3 w-3" />
              {activeFilterCount} filter{activeFilterCount !== 1 ? 's' : ''} active
            </span>
          )}
        </div>

        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClearFilters}
            className="text-xs"
          >
            Reset filters
          </Button>
        )}
      </div>

      {/* Active Filters Tags */}
      {hasActiveFilters && (
        <div className="flex flex-wrap items-center gap-2">
          {filters.search && (
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-background border border-border rounded-full text-xs">
              Search: "{filters.search}"
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleSearchChange('')}
                className="h-4 w-4 p-0 ml-1"
              >
                <X className="h-3 w-3" />
              </Button>
            </span>
          )}

          {filters.dateFilter !== 'all' && (
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-background border border-border rounded-full text-xs">
              {dateFilterOptions.find(opt => opt.value === filters.dateFilter)?.label}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onFiltersChange({ dateFilter: 'all' })}
                className="h-4 w-4 p-0 ml-1"
              >
                <X className="h-3 w-3" />
              </Button>
            </span>
          )}

          {filters.statusFilter !== 'all' && (
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-background border border-border rounded-full text-xs">
              {statusFilterOptions.find(opt => opt.value === filters.statusFilter)?.label}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onFiltersChange({ statusFilter: 'all' })}
                className="h-4 w-4 p-0 ml-1"
              >
                <X className="h-3 w-3" />
              </Button>
            </span>
          )}

          {filters.showFavorites && (
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-background border border-border rounded-full text-xs">
              <Star className="h-3 w-3 fill-current" />
              Favorites Only
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onFiltersChange({ showFavorites: false })}
                className="h-4 w-4 p-0 ml-1"
              >
                <X className="h-3 w-3" />
              </Button>
            </span>
          )}
        </div>
      )}

      {/* Click outside handlers */}
      {(showDateDropdown || showStatusDropdown || showSortDropdown) && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => {
            setShowDateDropdown(false);
            setShowStatusDropdown(false);
            setShowSortDropdown(false);
          }}
        />
      )}
    </div>
  );
};