'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { cn } from '@/lib/utils';
import { 
  Calendar, 
  MessageSquare, 
  Globe, 
  FileText, 
  Star, 
  Archive,
  Edit3,
  Copy,
  Trash2,
  ExternalLink,
  Eye,
  Heart,
  Share2,
  MoreHorizontal,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { SavedThread } from '@/types/api';

interface ThreadHistoryCardProps {
  thread: SavedThread;
  isSelected?: boolean;
  onSelect?: (selected: boolean) => void;
  onDelete: () => Promise<void>;
  isDeleting?: boolean;
  showCheckbox?: boolean;
  className?: string;
}

export const ThreadHistoryCard: React.FC<ThreadHistoryCardProps> = ({
  thread,
  isSelected = false,
  onSelect,
  onDelete,
  isDeleting = false,
  showCheckbox = false,
  className,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showActions, setShowActions] = useState(false);
  const [copied, setCopied] = useState(false);

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return 'Today';
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else if (diffDays < 30) {
      const weeks = Math.floor(diffDays / 7);
      return `${weeks} week${weeks !== 1 ? 's' : ''} ago`;
    } else {
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
      });
    }
  };

  // Handle copy thread
  const handleCopy = async () => {
    try {
      const threadText = thread.tweets
        .map((tweet, index) => `${index + 1}/${thread.tweets.length}\n${tweet.content}`)
        .join('\n\n');
      
      await navigator.clipboard.writeText(threadText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy thread:', error);
    }
  };

  // Handle expand/collapse
  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  // Get source icon and text
  const getSourceInfo = () => {
    if (thread.metadata?.source_url) {
      const url = new URL(thread.metadata.source_url);
      return {
        icon: <Globe className="h-4 w-4" />,
        text: url.hostname.replace('www.', ''),
        isUrl: true,
      };
    } else {
      return {
        icon: <FileText className="h-4 w-4" />,
        text: 'Manual Input',
        isUrl: false,
      };
    }
  };

  const sourceInfo = getSourceInfo();

  // Get status badge info
  const getStatusBadge = () => {
    if (thread.is_archived) {
      return {
        variant: 'secondary' as const,
        icon: <Archive className="h-3 w-3" />,
        text: 'Archived',
      };
    }
    
    // This would come from the thread status when implemented
    return {
      variant: 'secondary' as const,
      icon: <FileText className="h-3 w-3" />,
      text: 'Draft',
    };
  };

  const statusBadge = getStatusBadge();

  return (
    <Card className={cn(
      'group hover:shadow-md transition-all duration-200',
      isSelected && 'ring-2 ring-primary ring-offset-2',
      className
    )}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 flex-1 min-w-0">
            {/* Checkbox */}
            {showCheckbox && (
              <label className="flex items-center mt-1 cursor-pointer">
                <input
                  type="checkbox"
                  className="rounded border-border"
                  checked={isSelected}
                  onChange={(e) => onSelect?.(e.target.checked)}
                />
              </label>
            )}

            {/* Thread Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                <h3 className="font-semibold text-foreground truncate flex-1">
                  {thread.title}
                </h3>
                
                {/* Favorite indicator */}
                {thread.is_favorite && (
                  <Star className="h-4 w-4 text-yellow-500 fill-current flex-shrink-0" />
                )}
              </div>

              <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground mb-3">
                {/* Date */}
                <div className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  <span>{formatDate(thread.created_at)}</span>
                </div>

                {/* Tweet count */}
                <div className="flex items-center gap-1">
                  <MessageSquare className="h-3 w-3" />
                  <span>{thread.tweet_count} tweet{thread.tweet_count !== 1 ? 's' : ''}</span>
                </div>

                {/* Source */}
                <div className="flex items-center gap-1">
                  {sourceInfo.icon}
                  <span className="truncate max-w-32">{sourceInfo.text}</span>
                </div>

                {/* Status Badge */}
                <span className={cn(
                  "inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium",
                  statusBadge.variant === 'secondary' ? 'bg-secondary text-secondary-foreground' :
                  'border border-border bg-background'
                )}>
                  {statusBadge.icon}
                  {statusBadge.text}
                </span>
              </div>

              {/* Preview Text */}
              <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                {thread.preview_text || thread.original_content.slice(0, 150) + '...'}
              </p>

              {/* Stats */}
              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Eye className="h-3 w-3" />
                  <span>{thread.view_count || 0} views</span>
                </div>
                <div className="flex items-center gap-1">
                  <Copy className="h-3 w-3" />
                  <span>{thread.copy_count || 0} copies</span>
                </div>
                <div className="flex items-center gap-1">
                  <span>{thread.total_characters} chars</span>
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleExpanded}
              className="h-8 w-8 p-0"
              title={isExpanded ? 'Collapse' : 'Expand preview'}
            >
              {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopy}
              className={cn(
                "h-8 w-8 p-0",
                copied && "text-green-600"
              )}
              title="Copy thread"
            >
              {copied ? <Copy className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowActions(!showActions)}
              className="h-8 w-8 p-0"
              title="More actions"
            >
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Action Buttons */}
        {showActions && (
          <div className="flex flex-wrap items-center gap-2 pt-3 border-t border-border">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => window.location.href = `/generate?edit=${thread.id}`}
              className="flex items-center gap-1"
            >
              <Edit3 className="h-3 w-3" />
              Edit
            </Button>

            <Button
              variant="secondary"
              size="sm"
              onClick={() => window.location.href = `/generate?duplicate=${thread.id}`}
              className="flex items-center gap-1"
            >
              <Copy className="h-3 w-3" />
              Duplicate
            </Button>

            {sourceInfo.isUrl && (
              <Button
                variant="secondary"
                size="sm"
                onClick={() => thread.metadata?.source_url && window.open(thread.metadata.source_url, '_blank')}
                className="flex items-center gap-1"
              >
                <ExternalLink className="h-3 w-3" />
                Source
              </Button>
            )}

            <Button
              variant="secondary"
              size="sm"
              onClick={onDelete}
              disabled={isDeleting}
              className="flex items-center gap-1 ml-auto text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              {isDeleting ? (
                <LoadingSpinner size="sm" />
              ) : (
                <Trash2 className="h-3 w-3" />
              )}
              Delete
            </Button>
          </div>
        )}
      </CardHeader>

      {/* Expanded Content */}
      {isExpanded && (
        <CardContent className="pt-0">
          <div className="space-y-3 border-t border-border pt-4">
            <h4 className="font-medium text-sm text-foreground">Thread Preview</h4>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {thread.tweets.slice(0, 3).map((tweet, index) => (
                <div
                  key={tweet.id || index}
                  className="bg-muted/50 rounded-lg p-3 text-sm"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-muted-foreground font-medium">
                      Tweet {index + 1}/{thread.tweet_count}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {tweet.character_count} chars
                    </span>
                  </div>
                  <p className="text-foreground leading-relaxed">
                    {tweet.content}
                  </p>
                </div>
              ))}
              
              {thread.tweets.length > 3 && (
                <div className="text-center py-2">
                  <span className="text-xs text-muted-foreground">
                    +{thread.tweets.length - 3} more tweets
                  </span>
                </div>
              )}
            </div>

            {/* Full Thread Button */}
            <Button
              variant="secondary"
              size="sm"
              onClick={() => window.location.href = `/thread/${thread.id}`}
              className="w-full flex items-center gap-2"
            >
              <Eye className="h-4 w-4" />
              View Full Thread
            </Button>
          </div>
        </CardContent>
      )}
    </Card>
  );
};