/**
 * Dashboard utilisateur après connexion
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { getStats } from '../lib/api';
import { 
  User, 
  LogOut, 
  FileText, 
  Upload, 
  BarChart3, 
  Settings,
  Bell,
  TrendingUp,
  Calendar,
  Search,
  Plus,
  Moon,
  Sun
} from 'lucide-react';

export default function Dashboard() {
  const { user, logout, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [stats, setStats] = useState({
    total_analyses: 0,
    successful_analyses: 0,
    failed_analyses: 0,
    pending_analyses: 0
  });
  const [isDarkMode, setIsDarkMode] = useState(() => {
    try {
      const stored = localStorage.getItem('theme');
      if (stored) return stored === 'dark';
      return document.documentElement.classList.contains('dark');
    } catch (e) {
      return false;
    }
  });

  // Rediriger si non connecté
  useEffect(() => {
    if (!isAuthenticated && !isLoading) {
      navigate('/login', { replace: true });
    }
  }, [isAuthenticated, isLoading, navigate]);

  // Charger les statistiques
  useEffect(() => {
    const loadStats = async () => {
      if (isAuthenticated && user) {
        try {
          const statsData = await getStats();
          setStats(statsData);
        } catch (error) {
          console.error('Erreur lors du chargement des statistiques:', error);
        }
      }
    };

    loadStats();
  }, [isAuthenticated, user]);

  // Appliquer le thème dark/light
  useEffect(() => {
    try {
      if (isDarkMode) {
        document.documentElement.classList.add('dark');
        localStorage.setItem('theme', 'dark');
      } else {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('theme', 'light');
      }
    } catch (e) {
      // ignore localStorage errors
    }
  }, [isDarkMode]);

  // Mettre à jour l'heure
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000); // Mise à jour chaque minute

    return () => clearInterval(timer);
  }, []);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--bg)' }}>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#F8485D]"></div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('fr-FR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('fr-FR', { 
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--bg)' }}>
      {/* Header avec logo Devoteam - comme les autres pages */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            {/* Logo Devoteam comme dans Header.tsx */}
            <div className="flex items-center space-x-8">
              <div className="flex items-center space-x-3">
                <img 
                  src="/devoteam.png" 
                  alt="Devoteam" 
                  className="h-8 w-auto"
                  onError={(e) => {
                    // Fallback si l'image n'est pas trouvée
                    const target = e.target as HTMLImageElement;
                    target.style.display = 'none';
                  }}
                />
                <span className="text-xl font-bold text-gray-900">CV Analyzer</span>
              </div>
              
              <nav className="hidden md:flex space-x-8">
                <button className="text-[#F8485D] hover:text-[#e63946] font-medium transition-colors">
                  Dashboard
                </button>
                <button 
                  onClick={() => navigate('/new')}
                  className="text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Nouveau CV
                </button>
                <button 
                  onClick={() => navigate('/compare')}
                  className="text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Comparer
                </button>
              </nav>
            </div>

            {/* Actions utilisateur */}
            <div className="flex items-center space-x-4">
              <button className="p-2 text-gray-400 hover:text-[#F8485D] transition-colors rounded-xl">
                <Bell className="h-5 w-5" />
              </button>
              
              <button
                onClick={toggleDarkMode}
                className="p-2 text-gray-400 hover:text-[#F8485D] transition-colors rounded-xl"
                title={isDarkMode ? 'Passer au mode clair' : 'Passer au mode sombre'}
              >
                {isDarkMode ? (
                  <Sun className="h-5 w-5" />
                ) : (
                  <Moon className="h-5 w-5" />
                )}
              </button>
              
              <div className="flex items-center space-x-3">
                {user.picture && (
                  <img
                    src={user.picture}
                    alt={user.name}
                    className="h-8 w-8 rounded-full ring-2 ring-[#F8485D]/20"
                  />
                )}
                <div className="hidden md:block">
                  <p className="text-sm font-medium text-gray-900">{user.name}</p>
                  <p className="text-xs text-gray-500">{user.email}</p>
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="p-2 text-gray-400 hover:text-[#F8485D] transition-colors rounded-xl"
                title="Se déconnecter"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section - Style cohérent avec votre design */}
        <div className="mb-8">
          <div className="bg-gradient-to-r from-[#F8485D] to-[#e63946] rounded-xl shadow-xl p-8 text-white transform transition-all duration-200 hover:scale-[1.02] hover:shadow-2xl">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold mb-3">
                  Salut, {user.given_name || user.name} ! 👋
                </h1>
                <p className="text-red-100 text-lg">
                  {formatDate(currentTime)} • {formatTime(currentTime)}
                </p>
              </div>
              <div className="hidden md:block">
                <div className="text-right bg-white/10 rounded-xl p-4 backdrop-blur-sm">
                  <p className="text-sm text-red-100 mb-1">Dernière connexion</p>
                  <p className="font-semibold text-white">
                    {new Date(user.last_login).toLocaleString('fr-FR')}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions - Style cohérent avec vos boutons */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <button 
            onClick={() => navigate('/new')}
            className="bg-white p-6 rounded-xl shadow-sm hover:shadow-xl transition-all duration-200 transform hover:scale-105 border border-gray-200 group"
          >
            <div className="flex items-center space-x-4">
              <div className="bg-[#F8485D]/10 p-3 rounded-xl group-hover:bg-[#F8485D] transition-colors duration-200">
                <Upload className="h-6 w-6 text-[#F8485D] group-hover:text-white transition-colors duration-200" />
              </div>
              <div className="text-left">
                <h3 className="font-semibold text-gray-900 group-hover:text-[#F8485D] transition-colors">Analyser un CV</h3>
                <p className="text-sm text-gray-600">Uploader et analyser</p>
              </div>
            </div>
          </button>

          <button 
            onClick={() => navigate('/compare')}
            className="bg-white p-6 rounded-xl shadow-sm hover:shadow-xl transition-all duration-200 transform hover:scale-105 border border-gray-200 group"
          >
            <div className="flex items-center space-x-4">
              <div className="bg-[#F8485D]/10 p-3 rounded-xl group-hover:bg-[#F8485D] transition-colors duration-200">
                <BarChart3 className="h-6 w-6 text-[#F8485D] group-hover:text-white transition-colors duration-200" />
              </div>
              <div className="text-left">
                <h3 className="font-semibold text-gray-900 group-hover:text-[#F8485D] transition-colors">Comparer</h3>
                <p className="text-sm text-gray-600">Profils vs mission</p>
              </div>
            </div>
          </button>

          <button 
            onClick={() => navigate('/history')}
            className="bg-white p-6 rounded-xl shadow-sm hover:shadow-xl transition-all duration-200 transform hover:scale-105 border border-gray-200 group"
          >
            <div className="flex items-center space-x-4">
              <div className="bg-[#F8485D]/10 p-3 rounded-xl group-hover:bg-[#F8485D] transition-colors duration-200">
                <FileText className="h-6 w-6 text-[#F8485D] group-hover:text-white transition-colors duration-200" />
              </div>
              <div className="text-left">
                <h3 className="font-semibold text-gray-900 group-hover:text-[#F8485D] transition-colors">Mes dossiers</h3>
                <p className="text-sm text-gray-600">Historique des CVs</p>
              </div>
            </div>
          </button>

          <button className="bg-white p-6 rounded-xl shadow-sm hover:shadow-xl transition-all duration-200 transform hover:scale-105 border border-gray-200 group">
            <div className="flex items-center space-x-4">
              <div className="bg-[#F8485D]/10 p-3 rounded-xl group-hover:bg-[#F8485D] transition-colors duration-200">
                <Settings className="h-6 w-6 text-[#F8485D] group-hover:text-white transition-colors duration-200" />
              </div>
              <div className="text-left">
                <h3 className="font-semibold text-gray-900 group-hover:text-[#F8485D] transition-colors">Paramètres</h3>
                <p className="text-sm text-gray-600">Configuration</p>
              </div>
            </div>
          </button>
        </div>

        {/* Recent Activity & Stats - Style cohérent */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Stats */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-xl border border-gray-200 p-8 transform transition-all duration-200 hover:scale-[1.01]">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <TrendingUp className="h-6 w-6 text-[#F8485D] mr-3" />
                Statistiques
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-6 bg-gradient-to-br from-[#F8485D]/10 to-[#F8485D]/5 rounded-xl border border-[#F8485D]/20 transform transition-all duration-200 hover:scale-105">
                  <div className="text-3xl font-bold text-[#F8485D] mb-2">{stats.successful_analyses}</div>
                  <div className="text-sm font-medium text-gray-700">CVs analysés</div>
                </div>
                <div className="text-center p-6 bg-gradient-to-br from-[#F8485D]/10 to-[#F8485D]/5 rounded-xl border border-[#F8485D]/20 transform transition-all duration-200 hover:scale-105">
                  <div className="text-3xl font-bold text-[#F8485D] mb-2">{stats.failed_analyses}</div>
                  <div className="text-sm font-medium text-gray-700">Échecs</div>
                </div>
                <div className="text-center p-6 bg-gradient-to-br from-[#F8485D]/10 to-[#F8485D]/5 rounded-xl border border-[#F8485D]/20 transform transition-all duration-200 hover:scale-105">
                  <div className="text-3xl font-bold text-[#F8485D] mb-2">{stats.total_analyses}</div>
                  <div className="text-sm font-medium text-gray-700">Total analyses</div>
                </div>
              </div>

              {stats.total_analyses === 0 ? (
                <div className="mt-8 text-center text-gray-500 bg-gray-50 rounded-xl p-6">
                  <div className="bg-[#F8485D]/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                    <FileText className="h-8 w-8 text-[#F8485D]" />
                  </div>
                  <p className="font-semibold text-gray-700 mb-2">Aucune activité récente</p>
                  <p className="text-sm text-gray-600">Commencez par analyser votre premier CV !</p>
                  <button 
                    onClick={() => navigate('/new')}
                    className="mt-4 px-6 py-2 bg-[#F8485D] text-white rounded-xl font-medium transition-all duration-200 transform hover:scale-105 hover:shadow-lg active:scale-95 hover:bg-[#e63946]"
                  >
                    Analyser un CV
                  </button>
                </div>
              ) : (
                <div className="mt-8 text-center bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6">
                  <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                    <FileText className="h-8 w-8 text-green-600" />
                  </div>
                  <p className="font-semibold text-gray-700 mb-2">Bravo ! Vous avez analysé {stats.successful_analyses} CV{stats.successful_analyses > 1 ? 's' : ''}</p>
                  <p className="text-sm text-gray-600">Continuez à analyser ou consultez votre historique</p>
                  <div className="mt-4 flex justify-center space-x-3">
                    <button 
                      onClick={() => navigate('/new')}
                      className="px-6 py-2 bg-[#F8485D] text-white rounded-xl font-medium transition-all duration-200 transform hover:scale-105 hover:shadow-lg active:scale-95 hover:bg-[#e63946]"
                    >
                      Analyser un CV
                    </button>
                    <button 
                      onClick={() => navigate('/history')}
                      className="px-6 py-2 bg-white border border-[#F8485D] text-[#F8485D] rounded-xl font-medium transition-all duration-200 transform hover:scale-105 hover:shadow-lg active:scale-95 hover:bg-[#F8485D] hover:text-white"
                    >
                      Voir l'historique
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Profile Info - Style cohérent */}
          <div className="bg-white rounded-xl shadow-xl border border-gray-200 p-8 transform transition-all duration-200 hover:scale-[1.01]">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <User className="h-6 w-6 text-[#F8485D] mr-3" />
              Mon profil
            </h2>
            
            <div className="space-y-6">
              <div className="flex items-center space-x-4 p-4 bg-gradient-to-r from-[#F8485D]/5 to-[#F8485D]/10 rounded-xl">
                {user.picture ? (
                  <img
                    src={user.picture}
                    alt={user.name}
                    className="h-16 w-16 rounded-full ring-4 ring-[#F8485D]/20 shadow-lg"
                  />
                ) : (
                  <div className="h-16 w-16 bg-[#F8485D]/10 rounded-full flex items-center justify-center ring-4 ring-[#F8485D]/20">
                    <User className="h-8 w-8 text-[#F8485D]" />
                  </div>
                )}
                <div>
                  <p className="font-bold text-gray-900 text-lg">{user.name}</p>
                  <p className="text-sm text-gray-600">{user.email}</p>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200 space-y-4">
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-xl">
                  <span className="text-gray-600 font-medium flex items-center">
                    <Calendar className="h-4 w-4 mr-2 text-[#F8485D]" />
                    Membre depuis
                  </span>
                  <span className="text-gray-900 font-semibold">
                    {new Date(user.created_at).toLocaleDateString('fr-FR')}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-xl">
                  <span className="text-gray-600 font-medium flex items-center">
                    <Calendar className="h-4 w-4 mr-2 text-[#F8485D]" />
                    Dernière connexion
                  </span>
                  <span className="text-gray-900 font-semibold">
                    {new Date(user.last_login).toLocaleDateString('fr-FR')}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}