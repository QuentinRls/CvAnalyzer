import { useState, useCallback } from 'react';
import { toast } from 'sonner';

interface UseCopyToClipboardReturn {
  copied: boolean;
  copyToClipboard: (text: string, successMessage?: string) => Promise<void>;
}

export function useCopyToClipboard(): UseCopyToClipboardReturn {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = useCallback(async (text: string, successMessage = 'Copié !') => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      toast.success(successMessage);
      
      // Animation de feedback
      setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch (error) {
      toast.error('Erreur lors de la copie');
      console.error('Erreur de copie:', error);
    }
  }, []);

  return { copied, copyToClipboard };
}
