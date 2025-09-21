import { Link } from 'react-router-dom';
import { useState } from 'react';
import devoteamLogo from '../images/devoteam.png';
import Header from '../components/Header';
import SplitText from '../components/SplitText';
import BlurText from '../components/BlurText';
import FadeIn from '../components/FadeIn';

export default function Home() {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--bg)' }}>
      {/* Header avec logo Devoteam (composant partagé) */}
      <Header
        title=""
      />

      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="container mx-auto px-4 py-16">
          <div className="text-center">
            <div className="inline-block">
              <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
                <SplitText text={"Dossier de Compétences spécial "} className="inline-block" />
                <span className={`text-[#F8485D] transition-transform duration-300 inline-block ${isHovered ? 'scale-105' : ''}`} onMouseEnter={() => setIsHovered(true)} onMouseLeave={() => setIsHovered(false)}>
                  <SplitText text={"Devoteam?"} className="inline-block" delay={0.85} />
                </span>
              </h1>
            </div>
            <p className="mt-6 text-lg leading-8 text-gray-600 max-w-2xl mx-auto">
              <SplitText text={"Upload le CV la team !"} className="inline-block" delay={1.4} />
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <FadeIn delay={1.9} duration={2}>
                <Link
                  to="/new"
                  className="px-8 py-4 bg-[#F8485D] text-white rounded-xl font-semibold text-lg transition-all duration-200 transform hover:scale-105 hover:shadow-xl active:scale-95 hover:bg-[#e63946]"
                >
                  Allez clique !
                </Link>
              </FadeIn>
            </div>
          </div>

          {/* Animation decorative */}
          <FadeIn delay={7.4} duration={1.5}>
            <div className="absolute bottom-20 left-10 w-20 h-20 bg-[#F8485D] rounded-full opacity-20 animate-bounce"></div>
            <div className="absolute bottom-1 right-10 w-16 h-16 bg-[#F8485D] rounded-full opacity-30 animate-bounce"></div>
          </FadeIn>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-[#F8485D] to-[#e63946]">
        <div className="container mx-auto px-4 py-16 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            <BlurText text={"Comparer les CV avec votre appel d'offre"} className="inline-block" delay={2.4} duration={1.2} stagger={0.02} />
          </h2>
          <p className="text-red-100 text-lg mb-8 max-w-2xl mx-auto">
            <BlurText text={"Vous avez une mission potentielle ? "} className="inline-block" delay={2.4} duration={1.2} stagger={0.02} />
            <BlurText text={"Besoin de savoir lequel de vos profils est le plus intéressant ?"} className="inline-block" delay={3.4} duration={1.2} stagger={0.02} />
          </p>
          <FadeIn delay={4.5} duration={2}>
            <Link
              to="/compare"
              className="px-8 py-4 bg-white text-[#F8485D] rounded-xl font-semibold text-lg transition-all duration-200 transform hover:scale-105 hover:shadow-xl"
            >
              Comparer maintenant !
            </Link>
          </FadeIn>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900">
        <div className="container mx-auto px-4 py-9">
          <div className="text-center">
            <FadeIn delay={5} duration={2}>
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
            </FadeIn>
          </div>
        </div>
      </footer>
    </div>
  );
}
