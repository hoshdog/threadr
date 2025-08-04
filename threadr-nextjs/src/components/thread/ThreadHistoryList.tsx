'use client';

import React, { useState } from 'react';
import { ThreadHistoryCard } from './ThreadHistoryCard';
import { Button } from '@/components/ui/Button';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { SavedThread } from '@/types/api';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
  onPageChange: (page: number) => void;
}

interface ThreadHistoryListProps {
  threads: SavedThread[];
  onDeleteThread: (threadId: string) => Promise<void>;
  isDeleting: boolean;
  pagination: PaginationProps;
  className?: string;
}

export const ThreadHistoryList: React.FC<ThreadHistoryListProps> = ({
  threads,
  onDeleteThread,
  isDeleting,
  pagination,
  className,
}) => {
  const [selectedThreads, setSelectedThreads] = useState<Set<string>>(new Set());
  const [deletingThreadId, setDeletingThreadId] = useState<string | null>(null);

  // Handle thread selection for batch operations
  const handleThreadSelect = (threadId: string, selected: boolean) => {
    const newSelected = new Set(selectedThreads);
    if (selected) {
      newSelected.add(threadId);
    } else {
      newSelected.delete(threadId);
    }
    setSelectedThreads(newSelected);
  };

  // Handle select all
  const handleSelectAll = (selected: boolean) => {
    if (selected) {
      setSelectedThreads(new Set(threads.map(t => t.id)));
    } else {
      setSelectedThreads(new Set());
    }
  };

  // Handle delete with loading state
  const handleDelete = async (threadId: string) => {
    try {
      setDeletingThreadId(threadId);
      await onDeleteThread(threadId);
      
      // Remove from selected threads if it was selected
      const newSelected = new Set(selectedThreads);
      newSelected.delete(threadId);
      setSelectedThreads(newSelected);
    } catch (error) {
      console.error('Failed to delete thread:', error);
    } finally {
      setDeletingThreadId(null);
    }
  };

  // Generate page numbers for pagination
  const getPageNumbers = () => {
    const { currentPage, totalPages } = pagination;
    const pages: (number | string)[] = [];
    
    if (totalPages <= 7) {
      // Show all pages if total is small
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Show first page, ellipsis, current range, ellipsis, last page
      pages.push(1);
      
      if (currentPage > 3) {
        pages.push('...');
      }
      
      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);
      
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      
      if (currentPage < totalPages - 2) {
        pages.push('...');
      }
      
      if (totalPages > 1) {
        pages.push(totalPages);
      }
    }
    
    return pages;
  };

  return (
    <div className={cn('space-y-6', className)}>
      {/* Batch Actions Bar */}
      {selectedThreads.size > 0 && (
        <div className="bg-background border border-border rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              {selectedThreads.size} thread{selectedThreads.size !== 1 ? 's' : ''} selected
            </span>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setSelectedThreads(new Set())}
            >
              Clear Selection
            </Button>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              disabled={isDeleting}
              onClick={() => {
                if (confirm(`Are you sure you want to delete ${selectedThreads.size} thread${selectedThreads.size !== 1 ? 's' : ''}?`)) {
                  // TODO: Implement batch delete
                  console.log('Batch delete:', Array.from(selectedThreads));
                }
              }}
              className="text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              Delete Selected
            </Button>
          </div>
        </div>
      )}

      {/* Select All Checkbox */}
      {threads.length > 1 && (
        <div className="flex items-center gap-3 pb-4 border-b border-border">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              className="rounded border-border"
              checked={selectedThreads.size === threads.length}
              onChange={(e) => handleSelectAll(e.target.checked)}
            />
            <span className="text-sm text-muted-foreground">
              Select all {threads.length} threads
            </span>
          </label>
        </div>
      )}

      {/* Thread Grid */}
      <div className="grid gap-4 sm:gap-6">
        {threads.map((thread) => (
          <ThreadHistoryCard
            key={thread.id}
            thread={thread}
            isSelected={selectedThreads.has(thread.id)}
            onSelect={(selected) => handleThreadSelect(thread.id, selected)}
            onDelete={() => handleDelete(thread.id)}
            isDeleting={deletingThreadId === thread.id}
            showCheckbox={threads.length > 1}
          />
        ))}
      </div>

      {/* Pagination */}
      {pagination.totalPages > 1 && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-6 border-t border-border">
          <div className="text-sm text-muted-foreground">
            Page {pagination.currentPage} of {pagination.totalPages}
          </div>
          
          <div className="flex items-center gap-2">
            {/* First Page */}
            <Button
              variant="secondary"
              size="sm"
              onClick={() => pagination.onPageChange(1)}
              disabled={!pagination.hasPrevious}
              className="hidden sm:flex"
            >
              <ChevronsLeft className="h-4 w-4" />
            </Button>
            
            {/* Previous Page */}
            <Button
              variant="secondary"
              size="sm"
              onClick={() => pagination.onPageChange(pagination.currentPage - 1)}
              disabled={!pagination.hasPrevious}
            >
              <ChevronLeft className="h-4 w-4" />
              <span className="hidden sm:inline ml-1">Previous</span>
            </Button>
            
            {/* Page Numbers */}
            <div className="hidden sm:flex items-center gap-1">
              {getPageNumbers().map((page, index) => (
                <React.Fragment key={index}>
                  {page === '...' ? (
                    <span className="px-3 py-2 text-muted-foreground">...</span>
                  ) : (
                    <Button
                      variant={page === pagination.currentPage ? 'primary' : 'secondary'}
                      size="sm"
                      onClick={() => pagination.onPageChange(page as number)}
                      className="w-10 h-10 p-0"
                    >
                      {page}
                    </Button>
                  )}
                </React.Fragment>
              ))}
            </div>
            
            {/* Next Page */}
            <Button
              variant="secondary"
              size="sm"
              onClick={() => pagination.onPageChange(pagination.currentPage + 1)}
              disabled={!pagination.hasNext}
            >
              <span className="hidden sm:inline mr-1">Next</span>
              <ChevronRight className="h-4 w-4" />
            </Button>
            
            {/* Last Page */}
            <Button
              variant="secondary"
              size="sm"
              onClick={() => pagination.onPageChange(pagination.totalPages)}
              disabled={!pagination.hasNext}
              className="hidden sm:flex"
            >
              <ChevronsRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Mobile Page Indicator */}
      <div className="sm:hidden flex justify-center">
        <div className="text-xs text-muted-foreground">
          Showing {threads.length} of {pagination.totalPages * 20} threads
        </div>
      </div>
    </div>
  );
};