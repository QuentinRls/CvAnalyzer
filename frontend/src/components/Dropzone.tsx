import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import { fileHelpers } from '../lib/utils.ts';

interface DropzoneProps {
  onFile: (file: File) => void | Promise<void>;
  loading?: boolean;
  accept?: Record<string, string[]>;
  maxSize?: number;
  className?: string;
}

export default function Dropzone({
  onFile,
  loading = false,
  accept = {
    'application/pdf': ['.pdf'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    'text/plain': ['.txt']
  },
  maxSize = 10 * 1024 * 1024, // 10MB
  className = ''
}: DropzoneProps) {
  const [error, setError] = useState<string>('');

  const onDrop = useCallback(async (acceptedFiles: File[], rejectedFiles: any[]) => {
    setError('');

    // Handle rejected files
    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0];
      if (rejection.errors.some((e: any) => e.code === 'file-too-large')) {
        setError(`Fichier trop volumineux. Taille maximale: ${fileHelpers.formatFileSize(maxSize)}`);
      } else if (rejection.errors.some((e: any) => e.code === 'file-invalid-type')) {
        setError('Type de fichier non supporté. Utilisez PDF, DOCX ou TXT.');
      } else {
        setError('Fichier invalide.');
      }
      return;
    }

    // Handle accepted files
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      
      // Additional validation
      if (!fileHelpers.isValidCVFile(file)) {
        setError('Type de fichier non supporté. Utilisez PDF, DOCX ou TXT.');
        return;
      }

      try {
        await onFile(file);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erreur lors du traitement du fichier');
      }
    }
  }, [onFile, maxSize]);

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragReject
  } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple: false,
    disabled: loading
  });

  const dropzoneClass = `
    dropzone
    ${isDragActive ? 'dragover' : ''}
    ${isDragReject ? 'border-red-500 bg-red-50' : ''}
    ${loading ? 'loading' : ''}
    ${className}
  `.trim();

  return (
    <div className="space-y-4">
      <div {...getRootProps({ className: dropzoneClass })}>
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-4">
          {loading ? (
            <div className="spinner w-8 h-8"></div>
          ) : (
            <Upload className="w-12 h-12 text-gray-400" />
          )}
          
          <div className="space-y-2">
            <p className="text-lg font-medium">
              {loading ? 'Traitement en cours...' : 
               isDragActive ? 'Déposez votre CV ici' : 
               'Glissez-déposez votre CV ou cliquez pour parcourir'}
            </p>
            
            <p className="text-sm text-gray-500">
              Formats supportés: PDF, DOCX, TXT (max {fileHelpers.formatFileSize(maxSize)})
            </p>
          </div>
          
          {!loading && (
            <div className="flex items-center space-x-2 text-xs text-gray-400">
              <FileText className="w-4 h-4" />
              <span>Ou collez le texte directement</span>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-md text-red-700">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span className="text-sm">{error}</span>
        </div>
      )}
    </div>
  );
}
