import { useState, useRef, DragEvent } from 'react';
import FadeIn from './FadeIn';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  onFilesSelect?: (files: File[]) => void;
  disabled?: boolean;
  multiple?: boolean;
  accept?: string;
  primaryText?: string; // main title when not dragging
  browseText?: string; // clickable part
  supportedText?: string; // small helper text about formats
  maxSizeText?: string; // small helper text about max size
}

export default function FileUpload({ onFileSelect, onFilesSelect, disabled, multiple, accept, primaryText, browseText, supportedText, maxSizeText }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (disabled) return;
    
    const files = Array.from(e.dataTransfer.files || []);
    if (files.length === 0) return;

    if (disabled) return;

    const valid = files.filter(isValidFile);
    if (multiple) {
      if (onFilesSelect && valid.length > 0) {
        onFilesSelect(valid);
        return;
      }

      // Fallback: call onFileSelect for each valid file so existing single-file handlers can accept multiple
      for (const f of valid) {
        onFileSelect(f);
      }
      return;
    }

    const file = valid[0];
    if (file) onFileSelect(file);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files ? Array.from(e.target.files) : [];
    if (files.length === 0) return;

    const valid = files.filter(isValidFile);
    if (multiple) {
      if (onFilesSelect && valid.length > 0) {
        onFilesSelect(valid);
        return;
      }

      for (const f of valid) {
        onFileSelect(f);
      }
      return;
    }

    const file = valid[0];
    if (file) onFileSelect(file);
  };

  const isValidFile = (file: File) => {
    const validTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword',
      'application/vnd.ms-powerpoint',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      'text/plain'
    ];
    const validExtensions = ['.pdf', '.docx', '.doc', '.pptx', '.txt'];

    const hasValidType = validTypes.includes(file.type);
    const hasValidExtension = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));

    return hasValidType || hasValidExtension;
  };

  const openFileDialog = () => {
    if (!disabled) {
      fileInputRef.current?.click();
    }
  };

  const acceptTypes = accept ?? '.pdf,.docx,.txt';

  return (
    <div className="relative">
      <FadeIn>
      <input
        ref={fileInputRef}
        type="file"
        accept={acceptTypes}
        onChange={handleFileChange}
        className="hidden"
        disabled={disabled}
        multiple={!!multiple}
      />
      
      <div
        className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 cursor-pointer ${
          isDragging 
            ? 'border-[#F8485D] bg-red-50 scale-105' 
            : isHovered
            ? 'border-[#F8485D] bg-red-50'
            : 'border-gray-300 bg-gray-50 hover:border-gray-400'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={openFileDialog}
        onMouseEnter={() => !disabled && setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* Icône animée */}
        <div className={`w-16 h-16 mx-auto mb-4 transition-all duration-300 ${isDragging ? 'scale-110' : ''}`}>
          <div className={`w-full h-full rounded-2xl flex items-center justify-center transition-all duration-300 ${
            isDragging || isHovered ? 'bg-[#F8485D] shadow-lg' : 'bg-gray-200'
          }`}>
            <svg 
              className={`w-8 h-8 transition-all duration-300 ${
                isDragging || isHovered ? 'text-white' : 'text-gray-500'
              }`} 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" 
              />
            </svg>
          </div>
        </div>

        {/* Texte principal */}
        <div className="space-y-2">
          <h3 className={`text-lg font-semibold transition-colors duration-300 ${
            isDragging || isHovered ? 'text-[#F8485D]' : 'text-gray-700'
          }`}>
            {isDragging ? 'Déposez votre fichier ici' : (primaryText ?? 'Glissez-déposez votre CV')}
          </h3>
          
          <p className="text-gray-600">
            ou <span className={`font-medium transition-colors duration-300 ${
              isHovered ? 'text-[#F8485D]' : 'text-blue-600'
            }`}>{browseText ?? 'cliquez pour parcourir'}</span>
          </p>
          
          <div className="text-sm text-gray-500 space-y-1">
            <p>{supportedText ?? 'Formats supportés : PDF, DOCX, TXT'}</p>
            <p>{maxSizeText ?? 'Taille maximum : 10 MB'}</p>
          </div>
        </div>

        {/* Animations décoratives */}
        <div className={`absolute top-4 right-4 w-3 h-3 bg-[#F8485D] rounded-full transition-all duration-500 ${
          isDragging ? 'animate-ping' : 'opacity-30'
        }`}></div>
        
        <div className={`absolute bottom-4 left-4 w-2 h-2 bg-[#F8485D] rounded-full transition-all duration-700 ${
          isDragging ? 'animate-pulse' : 'opacity-20'
        }`}></div>
      </div>

      {/* Indicateur de statut */}
      </FadeIn>
      {isDragging && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#F8485D] bg-opacity-10 rounded-2xl">
          <div className="bg-white px-4 py-2 rounded-lg shadow-lg border-2 border-[#F8485D]">
            <span className="text-[#F8485D] font-medium">Déposez maintenant !</span>
          </div>
        </div>
      )}
    </div>
  );
}
