import { useState, ReactNode, useRef, useEffect } from 'react';

interface CollapsableSectionProps {
  title: string;
  children: ReactNode;
  defaultExpanded?: boolean;
  className?: string;
}

export default function CollapsableSection({ 
  title, 
  children, 
  defaultExpanded = true, 
  className = '' 
}: CollapsableSectionProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [height, setHeight] = useState<number | undefined>(defaultExpanded ? undefined : 0);
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = contentRef.current;
    if (!el) return;

    const updateHeight = () => {
      const newHeight = isExpanded ? el.scrollHeight : 0;
      setHeight(prev => (prev === newHeight ? prev : newHeight));
    };

    // Update immediately
    updateHeight();

    // Observe size changes inside the content to adjust height when children change
    let ro: ResizeObserver | null = null;
    try {
      ro = new ResizeObserver(() => {
        // Recompute height if expanded
        if (isExpanded) updateHeight();
      });
      ro.observe(el);
    } catch (e) {
      // ResizeObserver unsupported -> no-op
    }

    return () => {
      if (ro) ro.disconnect();
    };
  }, [isExpanded]);

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden transition-all duration-200 ${className}`}>
      <div 
        className="px-6 py-4 cursor-pointer border-b border-gray-100"
        onClick={toggleExpanded}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
            <span className="w-1 h-6 bg-[#F8485D] rounded-full"></span>
            <span>{title}</span>
          </h2>
          <button 
            className="p-2 rounded-lg transition-all duration-200 transform"
            aria-label={isExpanded ? 'Réduire' : 'Développer'}
          >
            <svg 
              className={`w-5 h-5 transition-transform duration-300 ease-in-out ${isExpanded ? 'rotate-180' : ''}`}
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </div>
      
      <div 
        ref={contentRef}
        className="overflow-hidden transition-all duration-300 ease-in-out"
        style={{ height: height }}
      >
        <div className="p-6">
          {children}
        </div>
      </div>
    </div>
  );
}
