import { useState } from 'react';
import { toast } from 'sonner';

interface CopyableFieldProps {
  label: string;
  value: string | undefined | null;
  multiline?: boolean;
  className?: string;
}

export default function CopyableField({ label, value, multiline = false, className = '' }: CopyableFieldProps) {
  const [copied, setCopied] = useState(false);
  
  const displayValue = value || 'Non renseigné';
  const isEmpty = !value;

  const handleCopy = async () => {
    if (isEmpty) return;
    
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      toast.success(`${label} copié !`);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast.error('Erreur lors de la copie');
    }
  };

  return (
    <div className={`group relative transition-all duration-200 hover:scale-[1.02] ${className}`}>
      <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center space-x-2">
        <span className="w-1 h-4 bg-[#F8485D] rounded-full opacity-60"></span>
        <span>{label}</span>
      </label>
      <div className="relative">
        {multiline ? (
          <textarea
            value={displayValue}
            readOnly
            className={`w-full p-4 pr-12 border-2 rounded-xl bg-white transition-all duration-200 resize-none focus:ring-2 focus:ring-[#F8485D] focus:border-[#F8485D] hover:border-gray-300 hover:shadow-sm ${
              isEmpty ? 'text-gray-400 italic border-gray-200' : 'text-gray-900 border-gray-200'
            }`}
            rows={Math.min(Math.max(Math.ceil(displayValue.length / 60), 2), 6)}
          />
        ) : (
          <input
            type="text"
            value={displayValue}
            readOnly
            className={`w-full p-4 pr-12 border-2 rounded-xl bg-white transition-all duration-200 focus:ring-2 focus:ring-[#F8485D] focus:border-[#F8485D] hover:border-gray-300 hover:shadow-sm ${
              isEmpty ? 'text-gray-400 italic border-gray-200' : 'text-gray-900 border-gray-200'
            }`}
          />
        )}
        
        {!isEmpty && (
          <button
            onClick={handleCopy}
            className={`absolute right-3 top-1/2 transform -translate-y-1/2 p-2 rounded-lg transition-all duration-200 ${
              copied 
                ? 'bg-[#F8485D] text-white scale-110 shadow-lg' 
                : 'bg-gray-100 text-gray-600 hover:bg-[#F8485D] hover:text-white opacity-0 group-hover:opacity-100 hover:scale-105'
            }`}
            title={copied ? 'Copié !' : 'Copier'}
          >
            {copied ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            )}
          </button>
        )}
      </div>
    </div>
  );
}
