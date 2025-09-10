import React from 'react';

interface CopyableImageProps {
  src?: string;
  alt?: string;
  className?: string;
}

const CopyableImage: React.FC<CopyableImageProps> = ({ src, alt, className }) => {
  if (!src) {
    return null;
  }

  return (
    <img 
      src={src} 
      alt={alt || ''} 
      className={className}
    />
  );
};

export default CopyableImage;
