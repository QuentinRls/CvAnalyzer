import { useState } from 'react';
import { toast } from 'sonner';

interface CopyableListProps {
  label: string;
  items: string[] | undefined | null;
  className?: string;
}

export default function CopyableList({ label, items, className = '' }: CopyableListProps) {
  const [copied, setCopied] = useState(false);
  
  const displayItems = items && items.length > 0 ? items : ['Aucun élément'];
  const isEmpty = !items || items.length === 0;

  const handleCopy = async () => {
    if (isEmpty) return;
    
    try {
      const textToCopy = items!.join(',\n');
      await navigator.clipboard.writeText(textToCopy);
      setCopied(true);
      toast.success(`${label} copiée !`);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast.error('Erreur lors de la copie');
    }
  };

  const handleCopyItem = async (item: string) => {
    if (isEmpty) return;
    
    try {
      await navigator.clipboard.writeText(item);
      toast.success('Élément copié !');
    } catch (error) {
      toast.error('Erreur lors de la copie');
    }
  };

  return (
    <div className={`group relative ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <label className="block text-sm font-medium text-gray-700">
          {label}
        </label>
        {!isEmpty && (
          <button
            onClick={handleCopy}
            className={`px-3 py-1 text-xs rounded-md transition-all duration-200 ${
              copied 
                ? 'bg-green-100 text-green-600' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200 opacity-0 group-hover:opacity-100'
            }`}
            title={copied ? 'Liste copiée !' : 'Copier toute la liste'}
          >
            {copied ? 'Copiée !' : 'Copier tout'}
          </button>
        )}
      </div>
      
      <div className="border rounded-lg bg-gray-50 p-3">
        <div className="space-y-2">
          {displayItems.map((item, index) => (
            <div
              key={index}
              className={`flex items-center justify-between p-2 rounded border-l-4 ${
                isEmpty ? 'border-gray-300 bg-gray-100' : 'border-blue-300 bg-white hover:bg-blue-50'
              } group/item`}
            >
              <span className={`flex-1 ${isEmpty ? 'text-gray-400 italic' : 'text-gray-900'}`}>
                {item}
              </span>
              {!isEmpty && (
                <button
                  onClick={() => handleCopyItem(item)}
                  className="ml-2 p-1 rounded text-gray-400 hover:text-gray-600 opacity-0 group-hover/item:opacity-100 transition-opacity"
                  title="Copier cet élément"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
