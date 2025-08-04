'use client';

interface TemplateGridProps {
  children: React.ReactNode;
}

export default function TemplateGrid({ children }: TemplateGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 auto-rows-fr">
      {children}
    </div>
  );
}