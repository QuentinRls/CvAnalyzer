import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Storage helpers
export const storage = {
  get: <T>(key: string, defaultValue: T): T => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch {
      return defaultValue;
    }
  },
  
  set: <T>(key: string, value: T): void => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.warn('Failed to save to localStorage:', error);
    }
  },
  
  remove: (key: string): void => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.warn('Failed to remove from localStorage:', error);
    }
  }
};

// Constants
export const STORAGE_KEYS = {
  LAST_DRAFT: 'cv2dossier:lastDraft',
  LAST_EXTRACTION: 'cv2dossier:lastExtraction',
  SETTINGS: 'cv2dossier:settings'
} as const;

// File helpers
export const fileHelpers = {
  getFileExtension: (filename: string): string => {
    return filename.split('.').pop()?.toLowerCase() || '';
  },
  
  isValidCVFile: (file: File): boolean => {
    const validTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain'
    ];
    const validExtensions = ['pdf', 'docx', 'txt'];
    
    return validTypes.includes(file.type) || 
           validExtensions.includes(fileHelpers.getFileExtension(file.name));
  },
  
  formatFileSize: (bytes: number): string => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  }
};

// Date helpers
export const dateHelpers = {
  formatDateRange: (startDate: string, endDate?: string): string => {
    if (!startDate) return '';
    
    const start = new Date(startDate);
    const end = endDate ? new Date(endDate) : new Date();
    
    const formatDate = (date: Date) => {
      return date.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
    };
    
    if (endDate) {
      return `De ${formatDate(start)} à ${formatDate(end)}`;
    } else {
      return `Depuis ${formatDate(start)}`;
    }
  }
};

// Error helpers
export const errorHelpers = {
  getErrorMessage: (error: unknown): string => {
    if (error instanceof Error) {
      return error.message;
    }
    if (typeof error === 'string') {
      return error;
    }
    return 'Une erreur inattendue s\'est produite';
  },
  
  isNetworkError: (error: unknown): boolean => {
    const message = errorHelpers.getErrorMessage(error);
    return message.toLowerCase().includes('network') || 
           message.toLowerCase().includes('fetch') ||
           message.toLowerCase().includes('connection');
  }
};
