import React, { useState } from 'react';
import { toast } from 'sonner';

interface CopyableImageProps {
  src: string;
  alt: string;
  className?: string;
  style?: React.CSSProperties;
  title?: string;
  fallbackText?: string;
}

export default function CopyableImage({ 
  src, 
  alt, 
  className = '', 
  style = {},
  title,
  fallbackText 
}: CopyableImageProps) {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [isCopying, setIsCopying] = useState(false);

  const handleCopy = async () => {
    if (isCopying) return;
    
    setIsCopying(true);
    try {
      // Méthode 1: Copier l'URL de l'image
      if (src.startsWith('data:')) {
        // Pour les images base64, copier directement les données
        await navigator.clipboard.writeText(src);
        toast.success('Image copiée (données base64)');
      } else {
        // Pour les URLs, essayer de copier l'image elle-même
        try {
          const response = await fetch(src);
          const blob = await response.blob();
          
          if (navigator.clipboard && window.ClipboardItem) {
            await navigator.clipboard.write([
              new ClipboardItem({
                [blob.type]: blob
              })
            ]);
            toast.success('Image copiée');
          } else {
            // Fallback: copier l'URL
            await navigator.clipboard.writeText(src);
            toast.success('URL de l\'image copiée');
          }
        } catch {
          // Si la copie d'image échoue, copier l'URL
          await navigator.clipboard.writeText(src);
          toast.success('URL de l\'image copiée');
        }
      }
    } catch (error) {
      console.error('Erreur lors de la copie:', error);
      toast.error('Impossible de copier l\'image');
    } finally {
      setIsCopying(false);
    }
  };

  const handleImageLoad = () => {
    setImageLoaded(true);
    setImageError(false);
  };

  const handleImageError = () => {
    setImageError(true);
    setImageLoaded(false);
  };

  if (imageError && fallbackText) {
    return (
      <div 
        className={`
          flex items-center justify-center bg-gray-100 border border-gray-300 rounded
          cursor-pointer hover:bg-gray-200 transition-colors duration-200
          ${className}
        `}
        style={style}
        onClick={handleCopy}
        title={title || `Cliquer pour copier "${fallbackText}"`}
      >
        <span className="text-gray-600 text-sm font-medium px-2 py-1">
          {fallbackText}
        </span>
        {isCopying && (
          <div className="ml-2">
            <svg className="animate-spin h-4 w-4 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="relative group">
      <img
        src={src}
        alt={alt}
        className={`
          cursor-pointer transition-all duration-200 
          hover:shadow-lg hover:scale-105
          ${!imageLoaded ? 'opacity-0' : 'opacity-100'}
          ${className}
        `}
        style={style}
        onLoad={handleImageLoad}
        onError={handleImageError}
        onClick={handleCopy}
        title={title || 'Cliquer pour copier l\'image'}
      />
      
      {/* Loading placeholder */}
      {!imageLoaded && !imageError && (
        <div 
          className={`
            absolute inset-0 bg-gray-100 animate-pulse rounded
            flex items-center justify-center
          `}
        >
          <svg className="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
      )}
      
      {/* Copy indicator */}
      <div className={`
        absolute inset-0 bg-black bg-opacity-50 rounded
        flex items-center justify-center
        transition-opacity duration-200
        ${isCopying ? 'opacity-100' : 'opacity-0 group-hover:opacity-0'}
        pointer-events-none
      `}>
        {isCopying ? (
          <svg className="animate-spin h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        ) : (
          <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        )}
      </div>
      
      {/* Hover tooltip */}
      <div className={`
        absolute -top-8 left-1/2 transform -translate-x-1/2
        bg-gray-800 text-white text-xs px-2 py-1 rounded
        opacity-0 group-hover:opacity-100 transition-opacity duration-200
        pointer-events-none whitespace-nowrap
      `}>
        Cliquer pour copier
      </div>
    </div>
  );
}
