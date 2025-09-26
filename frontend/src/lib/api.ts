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
  public baseUrl: string;

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

  async get<T>(url: string, options?: RequestInit): Promise<{ data: T }> {
    const response = await fetch(`${this.baseUrl}${url}`, {
      method: 'GET',
      credentials: 'include',
      ...options
    });
    const data = await this.handleResponse<T>(response);
    return { data };
  }

  async post<T>(url: string, body?: any, options?: RequestInit): Promise<{ data: T }> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(options?.headers || {})
    };

    const response = await fetch(`${this.baseUrl}${url}`, {
      method: 'POST',
      credentials: 'include',
      headers,
      body: body ? JSON.stringify(body) : undefined,
      ...options
    });

    const data = await this.handleResponse<T>(response);
    return { data };
  }

  async postExtract(input: File | string) {
    if (input instanceof File) {
      const formData = new FormData();
      formData.append('file', input);
      
      const response = await fetch(`${this.baseUrl}/api/v1/extract`, {
        method: 'POST',
        credentials: 'include',
        body: formData
      });
      
      return this.handleResponse<any>(response);
    } else {
      const response = await fetch(`${this.baseUrl}/api/v1/extract-text`, {
        method: 'POST',
        credentials: 'include',
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
      credentials: 'include',
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

  async generatePowerPoint(dossierData: any) {
    const response = await fetch(`${this.baseUrl}/api/v1/generate-pptx`, {
      method: 'POST',
      credentials: 'include',
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

  async getStats() {
    const response = await fetch(`${this.baseUrl}/api/v1/stats`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    return this.handleResponse<{
      total_analyses: number;
      successful_analyses: number;
      failed_analyses: number;
      pending_analyses: number;
    }>(response);
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
export const generatePowerPoint = (dossierData: any) => apiClient.generatePowerPoint(dossierData);
export const getStats = () => apiClient.getStats();
export const healthCheck = () => apiClient.healthCheck();
export const getCompanyLogo = (companyName: string) => {
  // Fonction placeholder pour récupérer le logo d'une entreprise
  // Retourne null pour l'instant
  return Promise.resolve(null);
};
