/**
 * Service d'authentification pour le frontend
 */

// Configuration de l'API dynamique
const getApiBase = () => {
  // Priorité 1 : Variable d'environnement explicite
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL + '/api';
  }
  
  // Priorité 2 : Détection automatique en production
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      // En production, utiliser la même origine
      return window.location.origin + '/api';
    }
  }
  
  // Priorité 3 : Développement local
  return 'http://localhost:8000/api';
};

const API_BASE = getApiBase();

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
  given_name?: string;
  family_name?: string;
  created_at: string;
  last_login: string;
}

export interface AuthStatus {
  authenticated: boolean;
  user: User | null;
}

class AuthService {
  private baseUrl = API_BASE;

  /**
   * Vérifier le statut d'authentification actuel
   */
  async getAuthStatus(): Promise<AuthStatus> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/status`, {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        return data;
      }
      
      return { authenticated: false, user: null };
    } catch (error) {
      console.error('Erreur lors de la vérification du statut auth:', error);
      return { authenticated: false, user: null };
    }
  }

  /**
   * Obtenir les informations de l'utilisateur connecté
   */
  async getCurrentUser(): Promise<User | null> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/me`, {
        credentials: 'include',
      });
      
      if (response.ok) {
        return await response.json();
      }
      
      return null;
    } catch (error) {
      console.error('Erreur lors de la récupération du profil:', error);
      return null;
    }
  }

  /**
   * Initier la connexion Google OAuth
   */
  async initiateLogin(): Promise<string | null> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/login`);
      
      if (response.ok) {
        const data = await response.json();
        return data.auth_url;
      }
      
      throw new Error('Impossible d\'initier la connexion');
    } catch (error) {
      console.error('Erreur lors de l\'initiation de la connexion:', error);
      return null;
    }
  }

  /**
   * Se connecter avec Google (redirection)
   */
  async loginWithGoogle(): Promise<void> {
    const authUrl = await this.initiateLogin();
    if (authUrl) {
      // Marquer qu'on va faire une redirection OAuth
      sessionStorage.setItem('oauth_redirect', 'true');
      window.location.href = authUrl;
    } else {
      throw new Error('Impossible de se connecter avec Google');
    }
  }

  /**
   * Se déconnecter
   */
  async logout(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });
      
      return response.ok;
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error);
      return false;
    }
  }

  /**
   * Vérifier si l'utilisateur est connecté
   */
  async isAuthenticated(): Promise<boolean> {
    const status = await this.getAuthStatus();
    return status.authenticated;
  }

  /**
   * Appel API authentifié
   */
  async authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const response = await fetch(url, {
      ...options,
      credentials: 'include',
    });

    // Si non autorisé, rediriger vers login
    if (response.status === 401) {
      window.location.href = '/login';
    }

    return response;
  }
}

export const authService = new AuthService();