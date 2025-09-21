import LoadingSpinner from './LoadingSpinner';
import devoteamLogo from '../images/devoteam.png';

interface AnalysisLoadingProps {
  stage: string;
  progress?: number;
}

export default function AnalysisLoading({ stage, progress }: AnalysisLoadingProps) {
  return (
  <div className="min-h-screen flex items-center justify-center">
    <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full mx-4 force-white">
        {/* Logo */}
        <div className="flex justify-center mb-6">
          <div className="w-[75px] h-[75px] rounded-full flex items-center justify-center shadow-lg border-2 border-gray-100 force-white">
            <img 
              src={devoteamLogo} 
              alt="Devoteam" 
              className="w-12 h-12 object-contain"
            />
          </div>
        </div>

        {/* Titre */}
        <h2 className="text-2xl font-bold text-gray-900 text-center mb-2">
          Analyse en cours
        </h2>
        <p className="text-gray-600 text-center mb-8">
          Extraction et traitement de votre CV
        </p>

        {/* Animation de chargement */}
        <div className="flex justify-center mb-6">
          <LoadingSpinner size="lg" color="secondary" />
        </div>

        {/* Étape actuelle */}
        <div className="text-center mb-4">
          <p className="text-sm font-medium text-gray-700">
            {stage}
          </p>
        </div>

        {/* Barre de progression */}
        {progress !== undefined && (
          <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
            <div 
              className="bg-[#F8485D] h-2 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        )}

        {/* Animation des points */}
        <div className="flex justify-center space-x-1">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-2 h-2 bg-[#F8485D] rounded-full animate-pulse"
              style={{
                animationDelay: `${i * 0.2}s`,
                animationDuration: '1s'
              }}
            ></div>
          ))}
        </div>
      </div>
    </div>
  );
}
