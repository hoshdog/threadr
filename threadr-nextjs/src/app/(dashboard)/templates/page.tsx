'use client';

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth';
import { templatesData, templateCategories, getTemplatesByCategory, searchTemplates } from '@/data/templates';
import TemplateCard from '@/components/templates/TemplateCard';
import TemplateFilters from '@/components/templates/TemplateFilters';
import TemplateGrid from '@/components/templates/TemplateGrid';
import ProTemplateModal from '@/components/templates/ProTemplateModal';
import { LoadingSpinner } from '@/components/ui';
import { Button } from '@/components/ui';

export default function TemplatesPage() {
  const router = useRouter();
  const { user } = useAuth();
  
  // State management
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showProModal, setShowProModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<typeof templatesData[0] | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Filter templates based on search and category
  const filteredTemplates = useMemo(() => {
    let templates = templatesData;
    
    // Apply category filter
    if (selectedCategory !== 'all') {
      templates = getTemplatesByCategory(selectedCategory as 'Business' | 'Educational' | 'Personal');
    }
    
    // Apply search filter
    if (searchQuery.trim()) {
      templates = searchTemplates(searchQuery);
      if (selectedCategory !== 'all') {
        templates = templates.filter(t => t.category === selectedCategory);
      }
    }
    
    // Hide pro templates for non-premium users
    if (!user?.isPremium) {
      return templates.filter(t => !t.isPro);
    }
    
    return templates;
  }, [selectedCategory, searchQuery, user?.isPremium]);

  // Handle template selection
  const handleTemplateSelect = async (template: typeof templatesData[0]) => {
    // Check if user can access this template
    if (template.isPro && !user?.isPremium) {
      setSelectedTemplate(template);
      setShowProModal(true);
      return;
    }
    
    setIsLoading(true);
    try {
      // Navigate to generate page with template
      router.push(`/generate?template=${template.id}`);
    } catch (error) {
      console.error('Failed to select template:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle pro upgrade
  const handleUpgrade = () => {
    setShowProModal(false);
    router.push('/pricing');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900 sm:text-4xl">
              Thread Templates
            </h1>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              Professional templates to create engaging Twitter threads in seconds. 
              Choose from our curated collection of high-performing formats.
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <TemplateFilters
          categories={templateCategories}
          selectedCategory={selectedCategory}
          onCategoryChange={setSelectedCategory}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          templateCount={filteredTemplates.length}
          totalCount={templatesData.length}
        />

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center items-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        )}

        {/* Templates Grid */}
        {!isLoading && (
          <>
            {filteredTemplates.length > 0 ? (
              <TemplateGrid>
                {filteredTemplates.map((template) => (
                  <TemplateCard
                    key={template.id}
                    template={template}
                    onSelect={handleTemplateSelect}
                    isPremiumUser={user?.isPremium || false}
                  />
                ))}
              </TemplateGrid>
            ) : (
              <div className="text-center py-12">
                <div className="w-16 h-16 mx-auto mb-4 text-gray-400">
                  <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      strokeWidth={1} 
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" 
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No templates found
                </h3>
                <p className="text-gray-600 mb-6">
                  Try adjusting your search or category filters.
                </p>
                <Button
                  variant="secondary"
                  onClick={() => {
                    setSearchQuery('');
                    setSelectedCategory('all');
                  }}
                >
                  Clear Filters
                </Button>
              </div>
            )}
          </>
        )}

        {/* Pro Features Info */}
        {!user?.isPremium && (
          <div className="mt-12 bg-gradient-to-r from-purple-500 to-indigo-600 rounded-2xl p-8 text-white text-center">
            <h3 className="text-2xl font-bold mb-4">
              Unlock Premium Templates
            </h3>
            <p className="text-lg opacity-90 mb-6 max-w-2xl mx-auto">
              Get access to advanced templates, unlimited generations, and exclusive features 
              to supercharge your Twitter presence.
            </p>
            <Button
              variant="secondary"
              size="lg"
              onClick={() => router.push('/pricing')}
              className="bg-white text-purple-600 hover:bg-gray-100"
            >
              Upgrade to Pro
            </Button>
          </div>
        )}
      </div>

      {/* Pro Template Modal */}
      {showProModal && selectedTemplate && (
        <ProTemplateModal
          template={selectedTemplate}
          onClose={() => setShowProModal(false)}
          onUpgrade={handleUpgrade}
        />
      )}
    </div>
  );
}