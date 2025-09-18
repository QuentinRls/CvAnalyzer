import { Link } from 'react-router-dom';
import devoteamLogo from '../images/devoteam.png';

interface HeaderProps {
  title: string;
  subtitle?: string;
  onNewAnalysis?: () => void;
}

export default function Header({ title, subtitle, onNewAnalysis }: HeaderProps) {
  return (
    <div className="bg-white border-b border-gray-200 shadow-sm">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center">
          {/* Logo et titre */}
          <div className="flex items-center space-x-4">
            {/* Logo Devoteam */}
            <div className="flex-shrink-0">
              <div className="w-[75px] h-[75px] bg-white rounded-full flex items-center justify-center shadow-md border-2 border-gray-100">
                <img 
                  src={devoteamLogo} 
                  alt="Devoteam" 
                  className="w-12 h-12 object-contain"
                />
              </div>
            </div>
            
            {/* Titre */}
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {title}
              </h1>
              {subtitle && (
                <p className="text-sm text-gray-600 mt-1">
                  {subtitle}
                </p>
              )}
            </div>
          </div>

          {/* Zone centrale : boutons centrés */}
          <div className="flex-1 flex items-center justify-center">
            <div className="flex items-center space-x-3">
            {/* Accueil */}
            <Link
              to="/"
              className="inline-flex items-center justify-center gap-2 px-3 py-2 bg-gray-100 text-gray-800 rounded-xl hover:bg-gray-200 transition-colors duration-150 text-sm"
            >
              Accueil
            </Link>

            {/* Nouveau dossier / page */}
            <Link
              to="/new"
              className="inline-flex items-center justify-center gap-2 px-3 py-2 bg-[#F8485D] text-white rounded-xl hover:bg-[#e63946] transition-colors duration-150 text-sm"
            >
              <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span>Nouveau</span>
            </Link>

            {/* Fonctionnalité future (placeholder) */}
            <button
              onClick={() => {
                // Placeholder pour une fonctionnalité future
              }}
              disabled
              title="Fonctionnalité à venir"
                className="inline-flex items-center justify-center px-3 py-2 bg-gray-50 text-gray-400 rounded-xl border border-dashed border-gray-200 text-sm cursor-not-allowed"
            >
              À venir
            </button>

            {/* Le bouton 'Nouvelle Analyse' a été retiré (conservé uniquement la prop pour compatibilité) */}
            </div>
          </div>

          {/* Espace droit réservé pour actions futures (actuellement vide) */}
          <div className="w-24" />
        </div>
      </div>
    </div>
  );
}
