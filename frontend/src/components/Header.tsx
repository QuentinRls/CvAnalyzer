import { Link, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import devoteamLogo from '../images/devoteam.png';
import FadeIn from './FadeIn';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

interface HeaderProps {
  title: string;
  subtitle?: string;
  onNewAnalysis?: () => void;
}

export default function Header({ title, subtitle, onNewAnalysis }: HeaderProps) {
  const location = useLocation();
  const path = location.pathname || '/';

  const [dark, setDark] = useState<boolean>(() => {
    try {
      const stored = localStorage.getItem('theme');
      if (stored) return stored === 'dark';
      return document.documentElement.classList.contains('dark');
    } catch (e) {
      return false;
    }
  });

  useEffect(() => {
    try {
      if (dark) {
        document.documentElement.classList.add('dark');
        localStorage.setItem('theme', 'dark');
      } else {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('theme', 'light');
      }
    } catch (e) {
      // ignore
    }
  }, [dark]);

  // On mount, restore hideScrollbar preference
  useEffect(() => {
    try {
      const hidden = localStorage.getItem('hideScrollbar') === '1';
      if (hidden) document.documentElement.classList.add('hide-scrollbar');
    } catch (e) {
      // ignore
    }
  }, []);

  // Show 'Accueil' button except when on the home page ('/')
  const showHomeButton = path !== '/';
  // Show 'Nouveau' button except when on the '/new' page
  const showNewButton = path !== '/new';

  return (
    <div className="border-b border-gray-200 shadow-sm" style={{ backgroundColor: 'var(--card-bg)' }}>
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center">
          {/* Logo et titre */}
          <div className="flex items-center space-x-4">
            {/* Logo Devoteam */}
            <div className="flex-shrink-0">
              <FadeIn delay={6.5} duration={1.5}>
              <div
                className="w-[75px] h-[75px] rounded-full flex items-center justify-center shadow-md border-2"
                style={{
                  backgroundColor: 'white',
                  borderColor:  '#f3f4f6',
                }}
              >
                <img
                  src={devoteamLogo}
                  alt="Devoteam"
                  className="w-12 h-12 object-contain"
                />
              </div>
              </FadeIn>
            </div>
            
            {/* Titre */}
            <div>
              <h1 className="text-2xl font-bold" style={{ color: 'var(--text)' }}>
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
              {showHomeButton && (
                <FadeIn delay={0.9} duration={0.9}>
                  <Link
                    to="/"
                    className="inline-flex items-center justify-center gap-2 px-3 py-2 bg-gray-100 text-gray-800 rounded-xl hover:bg-gray-200 transition-colors duration-150 text-sm"
                  >
                    Accueil
                  </Link>
                </FadeIn>
              )}

              {/* Comparer */}
              <FadeIn delay={0.9} duration={0.9}>
                  <Link
                    to="/compare"
                    className="inline-flex items-center justify-center gap-2 px-3 py-2 bg-[#F8485D] text-white rounded-xl hover:bg-[#e63946] transition-colors duration-150 text-sm"
                  >
                    <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    <span>Comparer CV / Mission</span>
                  </Link>
              </FadeIn>

              {/* Nouveau dossier / page */}
              {showNewButton && (
                <FadeIn delay={1.4} duration={0.9}>
                  <Link
                    to="/new"
                    className="inline-flex items-center justify-center gap-2 px-3 py-2 bg-[#F8485D] text-white rounded-xl hover:bg-[#e63946] transition-colors duration-150 text-sm"
                  >
                    <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    <span>CV to DT</span>
                  </Link>
                </FadeIn>
              )}
            </div>
          </div>

          {/* Espace droit réservé pour actions : dark toggle */}
          <div className="w-24 flex items-center justify-end">
            <div className="flex items-center">
              <FadeIn delay={6} duration={1.2}>
              <button
                onClick={() => setDark((v) => !v)}
                aria-pressed={dark}
                title={dark ? 'Activer mode clair' : 'Activer mode sombre'}
                className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors mr-2"
              >
                {dark ? (
                  // Sun icon for light (when dark is active)
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10 3a1 1 0 011 1v1a1 1 0 11-2 0V4a1 1 0 011-1zM10 15a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM4.22 4.22a1 1 0 011.42 0L6.64 5.3a1 1 0 11-1.42 1.4L4.22 5.62a1 1 0 010-1.4zM13.36 13.36a1 1 0 011.42 0l1 1a1 1 0 11-1.42 1.42l-1-1a1 1 0 010-1.42zM3 10a1 1 0 011-1H5a1 1 0 110 2H4a1 1 0 01-1-1zM15 10a1 1 0 011-1h1a1 1 0 110 2h-1a1 1 0 01-1-1zM4.22 15.78a1 1 0 010-1.4l1-1a1 1 0 111.42 1.42l-1 1a1 1 0 01-1.42 0zM13.36 6.64a1 1 0 010-1.42l1-1a1 1 0 111.42 1.42l-1 1a1 1 0 01-1.42 0zM10 6a4 4 0 100 8 4 4 0 000-8z" />
                  </svg>
                ) : (
                  // Moon icon for dark (when light is active)
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-gray-800" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M17.293 13.293A8 8 0 116.707 2.707a7 7 0 0010.586 10.586z" />
                  </svg>
                )}
              </button>
              </FadeIn>
              {/* Toggle animations button */}
              <FadeIn delay={7} duration={1.2}>
              <button
                onClick={() => {
                  try {
                    const disabled = localStorage.getItem('animations') === 'off';
                    if (!disabled) {
                      // disable: kill GSAP tweens and ScrollTriggers and persist
                      gsap.killTweensOf('*');
                      ScrollTrigger.getAll().forEach((st) => st.kill());
                      localStorage.setItem('animations', 'off');
                      // also clear any lingering timeline
                      gsap.globalTimeline.clear();
                    } else {
                      // enable: remove flag and reload to reinitialize animations
                      localStorage.removeItem('animations');
                      window.location.reload();
                    }
                  } catch (e) {
                    // ignore
                  }
                }}
                title="Enlever / remettre les animations"
                className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-gray-800" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M3 3h14v2H3V3zm0 4h14v2H3V7zm0 4h14v2H3v-2zm0 4h14v2H3v-2z" />
                </svg>
              </button>
              </FadeIn>
              {/* scrollbar is hidden globally by default (no per-user button) */}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
