// API configuration and client
const getApiBase = () => {
  // Priorité 1 : Variable d'environnement explicite
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // Priorité 2 : Détection automatique en production
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      // En production, utiliser la même origine
      return window.location.origin;
    }
  }
  
  // Priorité 3 : Développement local
  return 'http://localhost:8000';
};

const API_BASE = getApiBase();

export interface ApiError {
  error: string;
  detail?: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData: ApiError = await response.json().catch(() => ({
        error: `HTTP ${response.status}: ${response.statusText}`
      }));
      throw new Error(errorData.error || `Request failed with status ${response.status}`);
    }

    const contentType = response.headers.get('content-type');
    if (contentType?.includes('application/json')) {
      return response.json();
    } else {
      return response as unknown as T;
    }
  }

  async postExtract(input: File | string) {
    if (input instanceof File) {
      const formData = new FormData();
      formData.append('file', input);
      
      const response = await fetch(`${this.baseUrl}/api/v1/extract`, {
        method: 'POST',
        body: formData
      });
      
      return this.handleResponse<any>(response);
    } else {
      const response = await fetch(`${this.baseUrl}/api/v1/extract-text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ cv_text: input })
      });
      
      return this.handleResponse<any>(response);
    }
  }

  async generatePDF(dossierData: any) {
    const response = await fetch(`${this.baseUrl}/api/v1/generate-pdf`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(dossierData)
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json().catch(() => ({
        error: `HTTP ${response.status}: ${response.statusText}`
      }));
      throw new Error(errorData.error || `Request failed with status ${response.status}`);
    }

    // Return the response blob for PDF download
    return response.blob();
  }

  async generateGoogleDocs(dossierData: any) {
    const response = await fetch(`${this.baseUrl}/api/v1/generate-google-docs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(dossierData)
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json().catch(() => ({
        error: `HTTP ${response.status}: ${response.statusText}`
      }));
      throw new Error(errorData.error || `Request failed with status ${response.status}`);
    }

    // Return the response blob for HTML download
    return response.blob();
  }

  async generatePowerPoint(dossierData: any) {
    const response = await fetch(`${this.baseUrl}/api/v1/generate-pptx`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(dossierData)
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json().catch(() => ({
        error: `HTTP ${response.status}: ${response.statusText}`
      }));
      throw new Error(errorData.error || `Request failed with status ${response.status}`);
    }

    // Return the response blob for PPTX download
    return response.blob();
  }

  async healthCheck() {
    const response = await fetch(`${this.baseUrl}/api/v1/health`);
    return this.handleResponse<{ status: string; service: string }>(response);
  }
}

export const apiClient = new ApiClient(API_BASE);

// Convenience functions
export const postExtract = (input: File | string) => apiClient.postExtract(input);
export const generatePDF = (dossierData: any) => apiClient.generatePDF(dossierData);
export const generateGoogleDocs = (dossierData: any) => apiClient.generateGoogleDocs(dossierData);
export const generatePowerPoint = (dossierData: any) => apiClient.generatePowerPoint(dossierData);
export const healthCheck = () => apiClient.healthCheck();
