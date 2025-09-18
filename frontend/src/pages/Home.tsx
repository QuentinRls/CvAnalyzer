import { Link } from 'react-router-dom';
import { useState } from 'react';
import devoteamLogo from '../images/devoteam.png';
import Header from '../components/Header';

export default function Home() {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-red-50">
      {/* Header avec logo Devoteam (composant partagé) */}
      <Header
        title=""
      />

      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="container mx-auto px-4 py-16 sm:py-24 lg:py-32">
          <div className="text-center">
            <div 
              className="inline-block"
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
            >
              <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
                Dossier de Compétences<br></br> spécial
                <span className={`text-[#F8485D] transition-all duration-300 ${isHovered ? 'scale-105' : ''}`}>
                  {' '}Devoteam
                </span>
                {' '}?
              </h1>
            </div>
            <p className="mt-6 text-lg leading-8 text-gray-600 max-w-2xl mx-auto">
              Upload le CV la team ! 
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link 
                to="/new" 
                className="px-8 py-4 bg-[#F8485D] text-white rounded-xl font-semibold text-lg transition-all duration-200 transform hover:scale-105 hover:shadow-xl active:scale-95 hover:bg-[#e63946]"
              >
                Allez clique !
              </Link>
            </div>
          </div>
          
          {/* Animation decorative */}
          <div className="absolute top-10 left-10 w-20 h-20 bg-[#F8485D] rounded-full opacity-20 animate-bounce"></div>
          <div className="absolute bottom-10 right-10 w-16 h-16 bg-[#F8485D] rounded-full opacity-30 animate-pulse"></div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-[#F8485D] to-[#e63946]">
        <div className="container mx-auto px-4 py-16 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Prêt à analyser votre CV ?
          </h2>
          <p className="text-red-100 text-lg mb-8 max-w-2xl mx-auto">
            Rejoignez les professionnels qui optimisent leurs candidatures 
            avec une analyse détaillée de leurs compétences.
          </p>
          <Link 
            to="/new" 
            className="px-8 py-4 bg-white text-[#F8485D] rounded-xl font-semibold text-lg transition-all duration-200 transform hover:scale-105 hover:shadow-xl"
          >
            Commencer Maintenant !
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900">
        <div className="container mx-auto px-4 py-12">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-4 mb-4">
              <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-md border border-gray-200">
                <img 
                  src={devoteamLogo} 
                  alt="Devoteam" 
                  className="w-5 h-5 object-contain"
                />
              </div>
              <h3 className="text-white text-lg font-semibold">
                CV Intelligence by Devoteam
              </h3>
            </div>
            <p className="text-gray-400 mb-4">
              Transformez votre CV en dossier professionnel avec l'IA
            </p>
            <div className="flex justify-center space-x-6 text-gray-400 text-sm">
              <span>Alimenté par GPT-5</span>
              <span>•</span>
              <span>Sécurisé et privé</span>
              <span>•</span>
              <span>Gratuit</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
