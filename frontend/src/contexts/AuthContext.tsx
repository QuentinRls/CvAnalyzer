/**
 * Context d'authentification React
 */

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService, User, AuthStatus } from '../services/auth';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const refreshAuth = async () => {
    setIsLoading(true);
    try {
      const status: AuthStatus = await authService.getAuthStatus();
      console.log('Auth status updated:', status.authenticated ? 'authenticated' : 'not authenticated');
      setUser(status.user);
      setIsAuthenticated(status.authenticated);
    } catch (error) {
      console.error('Erreur lors du refresh auth:', error);
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async () => {
    try {
      await authService.loginWithGoogle();
    } catch (error) {
      console.error('Erreur lors de la connexion:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
      setUser(null);
      setIsAuthenticated(false);
      // Rediriger vers la page de login
      window.location.href = '/login';
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error);
      throw error;
    }
  };

  // Vérifier l'état d'authentification au montage
  useEffect(() => {
    refreshAuth();
  }, []);

  // Vérifier si on revient d'un callback OAuth (une seule fois)
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const error = urlParams.get('error');
    
    if (error === 'auth_failed') {
      console.error('Authentification échouée');
    }
    
    // Détecter si on arrive depuis un callback OAuth
    const wasRedirected = sessionStorage.getItem('oauth_redirect');
    if (wasRedirected) {
      console.log('Détection de retour OAuth, rafraîchissement unique...');
      sessionStorage.removeItem('oauth_redirect');
      
      // Un seul rafraîchissement après callback
      setTimeout(() => {
        refreshAuth();
      }, 500);
    }
  }, []); // Dépendances vides pour ne s'exécuter qu'une seule fois

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    refreshAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth doit être utilisé dans un AuthProvider');
  }
  return context;
}

export default AuthContext;