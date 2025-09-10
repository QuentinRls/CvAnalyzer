import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { CompetencesTechniques } from '../lib/schemas';
import CopyableImage from './CopyableImage';
import { getCompanyLogo } from '../lib/api';

interface ExperienceProfessionnelleData {
  client?: string;
  intitule_poste?: string;
  date_debut?: string;
  date_fin?: string;
  contexte?: string;
  responsabilites?: string[];
  livrables?: string[];
  environnement_technique?: CompetencesTechniques;
}

interface CopyableExperienceProfessionnelleProps {
  experience: ExperienceProfessionnelleData;
  index: number;
}

export default function CopyableExperienceProfessionnelle({ 
  experience, 
  index 
}: CopyableExperienceProfessionnelleProps) {
  const [copied, setCopied] = useState<{ [key: string]: boolean }>({});
  const [isExpanded, setIsExpanded] = useState(true);
  const [logoUrl, setLogoUrl] = useState<string | null>(null);
  const [logoLoading, setLogoLoading] = useState(false);

  // Charger le logo de l'entreprise via l'API
  useEffect(() => {
    if (experience.client) {
      setLogoLoading(true);
      getCompanyLogo(experience.client)
        .then((url) => {
          setLogoUrl(url);
        })
        .catch((error) => {
          console.warn(`Erreur chargement logo ${experience.client}:`, error);
          setLogoUrl(null);
        })
        .finally(() => {
          setLogoLoading(false);
        });
    }
  }, [experience.client]);

  // Nettoyer l'URL du logo quand le composant se démonte
  useEffect(() => {
    return () => {
      if (logoUrl) {
        URL.revokeObjectURL(logoUrl);
      }
    };
  }, [logoUrl]);

  // Bloc 1 : En-tête (Client, Poste, Dates)
  const formatBloc1 = () => {
    const parts = [];
    if (experience.client) parts.push(experience.client);
    if (experience.intitule_poste) parts.push(experience.intitule_poste);
    if (experience.date_debut && experience.date_fin) {
      const dateFin = experience.date_fin === 'en_cours' ? 'En cours' : experience.date_fin;
      parts.push(`De ${experience.date_debut} à ${dateFin}`);
    }
    return parts.join('\n');
  };

  // Bloc 2 : Contexte (sans le mot "Contexte")
  const formatBloc2 = () => {
    return experience.contexte || '';
  };

  // Bloc 3 : Responsabilités (sans le mot "Responsabilités", sans bullet points)
  const formatBloc3 = () => {
    if (!experience.responsabilites || experience.responsabilites.length === 0) return '';
    return experience.responsabilites.join('\n');
  };

  // Bloc 4 : Livrables (sans le mot "Livrables", sans bullet points)
  const formatBloc4 = () => {
    if (!experience.livrables || experience.livrables.length === 0) return '';
    return experience.livrables.join('\n');
  };

  // Bloc 5 : Environnement technique (organisé par catégories)
  const formatBloc5 = () => {
    if (!experience.environnement_technique) return '';
    
    const parts: string[] = [];
    const envTech = experience.environnement_technique;
    
    // Parcourir chaque catégorie et ajouter les compétences s'il y en a
    if (envTech.language_framework?.length) {
      parts.push(`Language Framework:\n${envTech.language_framework.map(tech => `${tech}`).join(',')}`);
    }
    if (envTech.ci_cd?.length) {
      parts.push(`Ci Cd:\n${envTech.ci_cd.map(tech => `${tech}`).join(',')}`);
    }
    if (envTech.state_management?.length) {
      parts.push(`State Management:\n${envTech.state_management.map(tech => `${tech}`).join(',')}`);
    }
    if (envTech.tests?.length) {
      parts.push(`Tests:\n${envTech.tests.map(tech => `${tech}`).join(',')}`);
    }
    if (envTech.outils?.length) {
      parts.push(`Outils:\n${envTech.outils.map(tech => `${tech}`).join(',')}`);
    }
    if (envTech.base_de_donnees_big_data?.length) {
      parts.push(`Base De Donnees Big Data:\n${envTech.base_de_donnees_big_data.map(tech => `${tech}`).join(',')}`);
    }
    if (envTech.data_analytics_visualisation?.length) {
      parts.push(`Data Analytics Visualisation:\n${envTech.data_analytics_visualisation.map(tech => `${tech}`).join(',')}`);
    }
    if (envTech.collaboration?.length) {
      parts.push(`Collaboration:\n${envTech.collaboration.map(tech => `${tech}`).join(',')}`);
    }
    if (envTech.ux_ui?.length) {
      parts.push(`Ux Ui:\n${envTech.ux_ui.map(tech => `${tech}`).join(',')}`);
    }
    
    return parts.join('\n\n');
  };

  // Expérience complète (format original avec titres)
  const formatExperience = () => {
    const parts = [];
    
    // En-tête principal
    if (experience.client) parts.push(experience.client);
    if (experience.intitule_poste) parts.push(experience.intitule_poste);
    
    // Dates
    if (experience.date_debut && experience.date_fin) {
      const dateFin = experience.date_fin === 'en_cours' ? 'En cours' : experience.date_fin;
      parts.push(`De ${experience.date_debut} à ${dateFin}`);
    }
    
    // Contexte
    if (experience.contexte) {
      parts.push('Contexte.');
      parts.push(experience.contexte);
    }
    
    // Responsabilités
    if (experience.responsabilites && experience.responsabilites.length > 0) {
      parts.push('Responsabilités.');
      experience.responsabilites.forEach(resp => parts.push(`${resp}`));
    }
    
    // Livrables
    if (experience.livrables && experience.livrables.length > 0) {
      parts.push('Livrables.');
      experience.livrables.forEach(livrable => parts.push(`${livrable}`));
    }
    
    // Environnement technique
    if (experience.environnement_technique) {
      const envTech = experience.environnement_technique;
      const techParts: string[] = [];
      
      // Vérifier s'il y a au moins une catégorie avec des données
      const hasAnyTech = Object.values(envTech).some(category => Array.isArray(category) && category.length > 0);
      
      if (hasAnyTech) {
        parts.push('Environnement technique.');
        
        // Ajouter chaque catégorie qui a des données
        if (envTech.language_framework?.length) {
          techParts.push(`Language Framework: ${envTech.language_framework.join(', ')}`);
        }
        if (envTech.ci_cd?.length) {
          techParts.push(`CI/CD: ${envTech.ci_cd.join(', ')}`);
        }
        if (envTech.state_management?.length) {
          techParts.push(`State Management: ${envTech.state_management.join(', ')}`);
        }
        if (envTech.tests?.length) {
          techParts.push(`Tests: ${envTech.tests.join(', ')}`);
        }
        if (envTech.outils?.length) {
          techParts.push(`Outils: ${envTech.outils.join(', ')}`);
        }
        if (envTech.base_de_donnees_big_data?.length) {
          techParts.push(`Bases de données/Big Data: ${envTech.base_de_donnees_big_data.join(', ')}`);
        }
        if (envTech.data_analytics_visualisation?.length) {
          techParts.push(`Data Analytics/Visualisation: ${envTech.data_analytics_visualisation.join(', ')}`);
        }
        if (envTech.collaboration?.length) {
          techParts.push(`Collaboration: ${envTech.collaboration.join(', ')}`);
        }
        if (envTech.ux_ui?.length) {
          techParts.push(`UX/UI: ${envTech.ux_ui.join(', ')}`);
        }
        
        techParts.forEach(techPart => parts.push(`- ${techPart}`));
      }
    }
    
    return parts.join('\n');
  };

  const handleCopyBloc = async (blocNumber: number, content: string, label: string) => {
    if (!content.trim()) {
      toast.error(`${label} est vide`);
      return;
    }
    
    try {
      await navigator.clipboard.writeText(content);
      setCopied({ ...copied, [`bloc${blocNumber}`]: true });
      toast.success(`${label} copié !`);
      setTimeout(() => setCopied({ ...copied, [`bloc${blocNumber}`]: false }), 2000);
    } catch (error) {
      toast.error('Erreur lors de la copie');
    }
  };

  const handleCopyAll = async () => {
    try {
      const fullText = formatExperience();
      await navigator.clipboard.writeText(fullText);
      setCopied({ ...copied, all: true });
      toast.success('Expérience complète copiée !');
      setTimeout(() => setCopied({ ...copied, all: false }), 2000);
    } catch (error) {
      toast.error('Erreur lors de la copie');
    }
  };

  return (
    <div className="border border-gray-200 rounded-lg bg-white">
      {/* En-tête collapsable */}
      <div 
        className="flex justify-between items-center p-4 cursor-pointer hover:bg-gray-50 transition-colors border-b border-gray-100"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <h3 className="text-lg font-semibold text-gray-900">
          Expérience Professionnelle {index + 1}
          {experience.client && ` - ${experience.client}`}
          {experience.intitule_poste && ` (${experience.intitule_poste})`}
        </h3>
        <div className="flex items-center space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleCopyAll();
            }}
            className={`px-3 py-1 text-xs rounded-md transition-all duration-200 ${
              copied.all 
                ? 'bg-green-100 text-green-600' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
            title="Copier toute l'expérience au format détaillé"
          >
            {copied.all ? 'Complète copiée !' : 'Copier complète'}
          </button>
          <button 
            className="p-1 rounded-md hover:bg-gray-200 transition-colors"
            aria-label={isExpanded ? 'Réduire' : 'Développer'}
          >
            <svg 
              className={`w-5 h-5 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </div>

      {/* Contenu collapsable */}
      {isExpanded && (
        <div className="p-6">
          {/* Boutons de copie par blocs */}
          <div className="mb-6 p-4 bg-blue-50 rounded-lg border">
            <h4 className="text-sm font-medium text-blue-900 mb-3">Copie par blocs :</h4>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2">
              {/* Bloc 1 : En-tête */}
              <button
                onClick={() => handleCopyBloc(1, formatBloc1(), "En-tête")}
                disabled={!formatBloc1().trim()}
                className={`px-3 py-2 text-xs rounded-md transition-all duration-200 ${
                  copied.bloc1 
                    ? 'bg-green-100 text-green-600' 
                    : 'bg-white text-blue-600 border border-blue-200 hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed'
                }`}
              >
                {copied.bloc1 ? 'Copié !' : 'Bloc 1: En-tête'}
              </button>

              {/* Bloc 2 : Contexte */}
              <button
                onClick={() => handleCopyBloc(2, formatBloc2(), "Contexte")}
                disabled={!formatBloc2().trim()}
                className={`px-3 py-2 text-xs rounded-md transition-all duration-200 ${
                  copied.bloc2 
                    ? 'bg-green-100 text-green-600' 
                    : 'bg-white text-blue-600 border border-blue-200 hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed'
                }`}
              >
                {copied.bloc2 ? 'Copié !' : 'Bloc 2: Contexte'}
              </button>

              {/* Bloc 3 : Responsabilités */}
              <button
                onClick={() => handleCopyBloc(3, formatBloc3(), "Responsabilités")}
                disabled={!formatBloc3().trim()}
                className={`px-3 py-2 text-xs rounded-md transition-all duration-200 ${
                  copied.bloc3 
                    ? 'bg-green-100 text-green-600' 
                    : 'bg-white text-blue-600 border border-blue-200 hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed'
                }`}
              >
                {copied.bloc3 ? 'Copié !' : 'Bloc 3: Responsabilités'}
              </button>

              {/* Bloc 4 : Livrables */}
              <button
                onClick={() => handleCopyBloc(4, formatBloc4(), "Livrables")}
                disabled={!formatBloc4().trim()}
                className={`px-3 py-2 text-xs rounded-md transition-all duration-200 ${
                  copied.bloc4 
                    ? 'bg-green-100 text-green-600' 
                    : 'bg-white text-blue-600 border border-blue-200 hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed'
                }`}
              >
                {copied.bloc4 ? 'Copié !' : 'Bloc 4: Livrables'}
              </button>

              {/* Bloc 5 : Environnement technique */}
              <button
                onClick={() => handleCopyBloc(5, formatBloc5(), "Environnement technique")}
                disabled={!formatBloc5().trim()}
                className={`px-3 py-2 text-xs rounded-md transition-all duration-200 ${
                  copied.bloc5 
                    ? 'bg-green-100 text-green-600' 
                    : 'bg-white text-blue-600 border border-blue-200 hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed'
                }`}
              >
                {copied.bloc5 ? 'Copié !' : 'Bloc 5: Env. technique'}
              </button>
            </div>
          </div>

          {/* Logo de l'entreprise */}
          {experience.client && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg border">
              <h4 className="text-sm font-medium text-gray-700 mb-3">Logo de l'entreprise :</h4>
              <div className="flex items-center space-x-4">
                {logoLoading ? (
                  <div className="w-16 h-16 bg-gray-100 rounded border border-gray-300 flex items-center justify-center">
                    <svg className="animate-spin h-6 w-6 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  </div>
                ) : logoUrl ? (
                  <CopyableImage
                    src={logoUrl}
                    alt={`Logo ${experience.client}`}
                    title={`Logo ${experience.client} - Cliquer pour copier`}
                    className="w-16 h-16 object-contain rounded border border-gray-200 bg-white"
                    fallbackText={experience.client?.substring(0, 3).toUpperCase() || '???'}
                  />
                ) : (
                  <div className="w-16 h-16 bg-gray-200 rounded border border-gray-300 flex items-center justify-center">
                    <span className="text-gray-500 text-xs font-medium">
                      {experience.client?.substring(0, 3).toUpperCase() || '???'}
                    </span>
                  </div>
                )}
                <div className="flex-1">
                  <p className="text-sm text-gray-600">
                    {logoLoading 
                      ? `Chargement du logo ${experience.client}...`
                      : logoUrl 
                        ? `✅ Logo disponible pour ${experience.client}` 
                        : `❌ Logo non disponible pour ${experience.client}`}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {logoLoading 
                      ? 'Recherche en cours...'
                      : logoUrl 
                        ? 'Cliquez sur le logo pour le copier dans votre presse-papiers'
                        : 'Le logo pourra être ajouté automatiquement dans les documents générés'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Aperçu par blocs */}
          <div className="mb-6 space-y-4">
            {/* Bloc 1 Aperçu */}
            {formatBloc1().trim() && (
              <div 
                className="p-3 bg-gray-50 rounded border-l-4 border-blue-200 cursor-pointer hover:bg-blue-50 transition-colors"
                onClick={() => handleCopyBloc(1, formatBloc1(), "En-tête")}
                title="Cliquer pour copier ce bloc"
              >
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-medium text-gray-600">Bloc 1 : En-tête</label>
                  <span className="text-xs text-gray-500">Cliquer pour copier</span>
                </div>
                <div className="text-sm text-gray-700 whitespace-pre-line font-mono">
                  {formatBloc1()}
                </div>
              </div>
            )}

            {/* Bloc 2 Aperçu */}
            {formatBloc2().trim() && (
              <div 
                className="p-3 bg-gray-50 rounded border-l-4 border-green-200 cursor-pointer hover:bg-green-50 transition-colors"
                onClick={() => handleCopyBloc(2, formatBloc2(), "Contexte")}
                title="Cliquer pour copier ce bloc"
              >
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-medium text-gray-600">Bloc 2 : Contexte</label>
                  <span className="text-xs text-gray-500">Cliquer pour copier</span>
                </div>
                <div className="text-sm text-gray-700 whitespace-pre-line">
                  {formatBloc2()}
                </div>
              </div>
            )}

            {/* Bloc 3 Aperçu */}
            {formatBloc3().trim() && (
              <div 
                className="p-3 bg-gray-50 rounded border-l-4 border-yellow-200 cursor-pointer hover:bg-yellow-50 transition-colors"
                onClick={() => handleCopyBloc(3, formatBloc3(), "Responsabilités")}
                title="Cliquer pour copier ce bloc"
              >
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-medium text-gray-600">Bloc 3 : Responsabilités</label>
                  <span className="text-xs text-gray-500">Cliquer pour copier</span>
                </div>
                <div className="text-sm text-gray-700 whitespace-pre-line">
                  {formatBloc3()}
                </div>
              </div>
            )}

            {/* Bloc 4 Aperçu */}
            {formatBloc4().trim() && (
              <div 
                className="p-3 bg-gray-50 rounded border-l-4 border-purple-200 cursor-pointer hover:bg-purple-50 transition-colors"
                onClick={() => handleCopyBloc(4, formatBloc4(), "Livrables")}
                title="Cliquer pour copier ce bloc"
              >
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-medium text-gray-600">Bloc 4 : Livrables</label>
                  <span className="text-xs text-gray-500">Cliquer pour copier</span>
                </div>
                <div className="text-sm text-gray-700 whitespace-pre-line">
                  {formatBloc4()}
                </div>
              </div>
            )}

            {/* Bloc 5 Aperçu */}
            {formatBloc5().trim() && (
              <div 
                className="p-3 bg-gray-50 rounded border-l-4 border-red-200 cursor-pointer hover:bg-red-50 transition-colors"
                onClick={() => handleCopyBloc(5, formatBloc5(), "Environnement technique")}
                title="Cliquer pour copier ce bloc"
              >
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-medium text-gray-600">Bloc 5 : Environnement technique</label>
                  <span className="text-xs text-gray-500">Cliquer pour copier</span>
                </div>
                <div className="text-sm text-gray-700 whitespace-pre-line">
                  {formatBloc5()}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
