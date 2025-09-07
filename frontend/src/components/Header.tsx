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
        <div className="flex items-center justify-between">
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

          {/* Bouton nouvelle analyse */}
          {onNewAnalysis && (
            <button
              onClick={onNewAnalysis}
              className="px-4 py-2 bg-[#F8485D] text-white rounded-lg hover:bg-[#e63946] transition-colors duration-200 font-medium flex items-center space-x-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span>Nouvelle Analyse</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
