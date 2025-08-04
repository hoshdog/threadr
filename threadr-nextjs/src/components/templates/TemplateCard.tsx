'use client';

import { useState } from 'react';
import { TemplateData } from '@/data/templates';
import { Button } from '@/components/ui';

interface TemplateCardProps {
  template: TemplateData;
  onSelect: (template: TemplateData) => void;
  isPremiumUser: boolean;
}

export default function TemplateCard({ template, onSelect, isPremiumUser }: TemplateCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  
  const canAccess = !template.isPro || isPremiumUser;
  
  // Get category color
  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'Business':
        return 'bg-twitter-blue/10 text-twitter-blue';
      case 'Educational':
        return 'bg-green-100 text-green-800';
      case 'Personal':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-twitter-light-gray text-twitter-text-gray';
    }
  };

  // Get popularity level
  const getPopularityLevel = (popularity: number) => {
    if (popularity >= 90) return { level: 'Hot', color: 'text-red-600' };
    if (popularity >= 80) return { level: 'Popular', color: 'text-orange-600' };
    if (popularity >= 70) return { level: 'Good', color: 'text-yellow-600' };
    return { level: 'New', color: 'text-twitter-gray' };
  };

  const popularityInfo = getPopularityLevel(template.popularity);

  return (
    <div
      className={`relative bg-white rounded-xl border-2 transition-all duration-200 cursor-pointer group ${
        isHovered ? 'border-twitter-blue shadow-lg transform scale-[1.02]' : 'border-gray-200 hover:border-twitter-border/30'
      } ${!canAccess ? 'opacity-75' : ''}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => onSelect(template)}
    >
      {/* Pro Badge */}
      {template.isPro && (
        <div className="absolute -top-2 -right-2 z-10">
          <div className="bg-gradient-to-r from-twitter-blue to-twitter-hover text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">
            PRO
          </div>
        </div>
      )}

      {/* Lock Overlay for Non-Premium Users */}
      {template.isPro && !isPremiumUser && (
        <div className="absolute inset-0 bg-black bg-opacity-40 rounded-xl flex items-center justify-center z-20">
          <div className="text-center text-white">
            <div className="w-12 h-12 mx-auto mb-2">
              <svg fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
              </svg>
            </div>
            <p className="text-sm font-medium">Premium Required</p>
          </div>
        </div>
      )}

      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-twitter-blue transition-colors">
              {template.name}
            </h3>
            <p className="text-sm text-twitter-text-gray line-clamp-2">
              {template.description}
            </p>
          </div>
        </div>

        {/* Metadata */}
        <div className="flex items-center gap-3 mb-4">
          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(template.category)}`}>
            {template.category}
          </span>
          <span className={`text-xs font-medium ${popularityInfo.color}`}>
            {popularityInfo.level}
          </span>
          <span className="text-xs text-twitter-gray">
            {template.structure.length} tweets
          </span>
        </div>

        {/* Preview */}
        <div className="mb-4">
          <div className="bg-twitter-light-gray rounded-lg p-3 space-y-2">
            {template.structure.slice(0, 2).map((tweet, index) => (
              <div key={index} className="text-sm text-twitter-text-gray bg-white rounded p-2 border">
                {tweet.length > 80 ? `${tweet.substring(0, 80)}...` : tweet}
              </div>
            ))}
            {template.structure.length > 2 && (
              <div className="text-xs text-twitter-gray text-center py-1">
                +{template.structure.length - 2} more tweets
              </div>
            )}
          </div>
        </div>

        {/* Variables Preview */}
        {template.variables.length > 0 && (
          <div className="mb-4">
            <p className="text-xs text-twitter-gray mb-2">Variables:</p>
            <div className="flex flex-wrap gap-1">
              {template.variables.slice(0, 3).map((variable, index) => (
                <span
                  key={index}
                  className="inline-flex px-2 py-1 bg-twitter-blue/10 text-twitter-blue text-xs rounded-full"
                >
                  {variable.replace(/_/g, ' ')}
                </span>
              ))}
              {template.variables.length > 3 && (
                <span className="text-xs text-twitter-gray">
                  +{template.variables.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Action Button */}
        <Button
          variant={template.isPro && !isPremiumUser ? "secondary" : "primary"}
          size="sm"
          className="w-full"
          disabled={template.isPro && !isPremiumUser}
        >
          {template.isPro && !isPremiumUser ? (
            <>
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
              </svg>
              Upgrade to Use
            </>
          ) : (
            'Use Template'
          )}
        </Button>
      </div>

      {/* Popularity Bar */}
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-twitter-light-gray rounded-b-xl overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-twitter-blue to-twitter-hover transition-all duration-300"
          style={{ width: `${template.popularity}%` }}
        />
      </div>
    </div>
  );
}