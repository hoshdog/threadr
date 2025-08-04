'use client';

import React from 'react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { cn } from '@/lib/utils';
import { 
  MessageSquare, 
  Plus, 
  Search, 
  Filter,
  Sparkles,
  FileText,
  RefreshCw
} from 'lucide-react';

interface ThreadHistoryEmptyProps {
  hasFilters: boolean;
  onClearFilters: () => void;
  onCreateThread: () => void;
  className?: string;
}

export const ThreadHistoryEmpty: React.FC<ThreadHistoryEmptyProps> = ({
  hasFilters,
  onClearFilters,
  onCreateThread,
  className,
}) => {
  if (hasFilters) {
    // Empty state with active filters
    return (
      <Card className={cn('', className)}>
        <CardContent className="flex flex-col items-center justify-center text-center py-16 px-6">
          <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mb-6">
            <Search className="h-8 w-8 text-muted-foreground" />
          </div>
          
          <h3 className="text-xl font-semibold text-foreground mb-2">
            No threads found
          </h3>
          
          <p className="text-muted-foreground mb-6 max-w-md">
            No threads match your current filters. Try adjusting your search criteria or clearing filters 
            to see more results.
          </p>

          <div className="flex flex-col sm:flex-row items-center gap-3">
            <Button 
              onClick={onClearFilters}
              variant="secondary"
              className="flex items-center gap-2"
            >
              <RefreshCw className="h-4 w-4" />
              Clear All Filters
            </Button>
            
            <Button 
              onClick={onCreateThread}
              className="flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              Create New Thread
            </Button>
          </div>

          {/* Filter suggestions */}
          <div className="mt-8 p-4 bg-muted/50 rounded-lg max-w-md">
            <h4 className="font-medium text-sm text-foreground mb-2">Try these suggestions:</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Check your spelling in the search box</li>
              <li>• Try broader date ranges</li>
              <li>• Remove status filters</li>
              <li>• Clear the favorites filter</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Empty state with no threads at all
  return (
    <Card className={cn('', className)}>
      <CardContent className="flex flex-col items-center justify-center text-center py-20 px-6">
        <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mb-8">
          <MessageSquare className="h-10 w-10 text-primary" />
        </div>
        
        <h2 className="text-2xl font-bold text-foreground mb-3">
          Welcome to Your Thread History
        </h2>
        
        <p className="text-muted-foreground mb-8 max-w-lg">
          This is where you'll see all your saved threads. Create your first thread to get started 
          building your Twitter content library.
        </p>

        <Button 
          onClick={onCreateThread}
          size="lg"
          className="flex items-center gap-2 mb-8"
        >
          <Sparkles className="h-5 w-5" />
          Create Your First Thread
        </Button>

        {/* Feature highlights */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-4xl w-full">
          <div className="text-center p-4">
            <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center mx-auto mb-3">
              <Plus className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="font-semibold text-foreground mb-2">Create Threads</h3>
            <p className="text-sm text-muted-foreground">
              Turn articles, blog posts, or your own ideas into engaging Twitter threads
            </p>
          </div>

          <div className="text-center p-4">
            <div className="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center mx-auto mb-3">
              <FileText className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="font-semibold text-foreground mb-2">Save & Organize</h3>
            <p className="text-sm text-muted-foreground">
              Keep all your threads organized with search, filters, and favorites
            </p>
          </div>

          <div className="text-center p-4">
            <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center mx-auto mb-3">
              <Search className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="font-semibold text-foreground mb-2">Find & Reuse</h3>
            <p className="text-sm text-muted-foreground">
              Quickly find past threads and reuse content for consistent messaging
            </p>
          </div>
        </div>

        {/* Quick start tips */}
        <div className="mt-12 p-6 bg-muted/50 rounded-lg max-w-2xl w-full">
          <h4 className="font-semibold text-foreground mb-4 flex items-center gap-2">
            <Sparkles className="h-4 w-4" />
            Quick Start Tips
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm text-muted-foreground">
            <div>
              <strong className="text-foreground">From URLs:</strong>
              <br />
              Paste any article URL to automatically generate a thread
            </div>
            <div>
              <strong className="text-foreground">From Text:</strong>
              <br />
              Write or paste your content directly for custom threads
            </div>
            <div>
              <strong className="text-foreground">Templates:</strong>
              <br />
              Use pre-built templates for common thread formats
            </div>
            <div>
              <strong className="text-foreground">AI-Powered:</strong>
              <br />
              Our AI optimizes length and engagement for Twitter
            </div>
          </div>
        </div>

        {/* Secondary action */}
        <div className="mt-8 flex items-center gap-4">
          <Button 
            variant="secondary" 
            size="sm"
            onClick={() => window.location.href = '/dashboard/templates'}
            className="flex items-center gap-2"
          >
            Browse Templates
          </Button>
          <span className="text-sm text-muted-foreground">or</span>
          <Button 
            variant="ghost" 
            size="sm"
            onClick={() => window.location.href = '/dashboard/analytics'}
          >
            View Analytics
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};