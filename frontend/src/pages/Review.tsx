import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { storage, STORAGE_KEYS } from '../lib/utils.ts';
import type { DossierCompetences } from '../lib/schemas.ts';
import CopyableField from '../components/CopyableField';
import CopyableList from '../components/CopyableList';
import CopyableExperiencesCles from '../components/CopyableExperiencesCles';
import CopyableExperienceProfessionnelle from '../components/CopyableExperienceProfessionnelle';
import CollapsableSection from '../components/CollapsableSection';
import Header from '../components/Header';
import LoadingSpinner from '../components/LoadingSpinner';
import ExportActions from '../components/ExportActions';
import devoteamLogo from '../images/devoteam.png';

export default function Review() {
  const navigate = useNavigate();
  const [dossierData, setDossierData] = useState<DossierCompetences | null>(null);
  
  const extractedData = storage.get(STORAGE_KEYS.LAST_DRAFT, null);
  
  useEffect(() => {
    if (!extractedData) {
      toast.error('Aucune analyse trouvée');
      navigate('/');
      return;
    }
    setDossierData(extractedData);
  }, [extractedData, navigate]);

  const handleNewAnalysis = () => {
    storage.remove(STORAGE_KEYS.LAST_DRAFT);
    storage.remove(STORAGE_KEYS.LAST_EXTRACTION);
    navigate('/new');
  };

  if (!dossierData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full mx-4">
          <div className="flex justify-center mb-6">
            <div className="w-[75px] h-[75px] bg-white rounded-full flex items-center justify-center shadow-lg border-2 border-gray-100">
              <img 
                src={devoteamLogo} 
                alt="Devoteam" 
                className="w-12 h-12 object-contain"
              />
            </div>
          </div>
          <div className="text-center">
            <LoadingSpinner size="lg" color="secondary" className="mb-4" />
            <p className="text-gray-600">Chargement de l'analyse...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header avec logo Devoteam */}
      <Header 
        title="Dossier de Compétences" 
        subtitle="Analyse Complète"
        onNewAnalysis={handleNewAnalysis}
      />

      {/* Contenu principal */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-5xl mx-auto space-y-8">
          
          {/* Actions principales */}
          <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-200">
            <div className="flex flex-col gap-4">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Actions disponibles</h2>
                <p className="text-gray-600 text-sm">Générez des documents professionnels ou copiez les sections individuellement</p>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm text-gray-600 flex-1">
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-[#F8485D] rounded-full mt-2 flex-shrink-0"></div>
                    <div>
                      <strong className="text-gray-800">PDF :</strong> Document prêt à imprimer, conserve la mise en forme
                    </div>
                  </div>
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-[#4285F4] rounded-full mt-2 flex-shrink-0"></div>
                    <div>
                      <strong className="text-gray-800">Google Docs :</strong> Fichier HTML à ouvrir et copier dans Google Docs
                    </div>
                  </div>
                </div>
                
                <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
                  <ExportActions 
                    dossierData={dossierData} 
                    className="w-full sm:w-auto"
                  />
                  <button
                    onClick={handleNewAnalysis}
                    className="
                      bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold 
                      py-3 px-6 rounded-xl transition-all duration-200 
                      border border-gray-300 hover:border-gray-400
                      w-full sm:w-auto
                    "
                  >
                    Nouvelle analyse
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* En-tête */}
          {dossierData.entete && (
            <CollapsableSection title="En-tête Professionnel">
              {/* Boutons de copie par blocs */}
              <div className="mb-6 p-4 bg-gradient-to-r from-gray-50 to-red-50 rounded-xl border border-gray-200">
                <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center space-x-2">
                  <span className="w-2 h-2 bg-[#F8485D] rounded-full"></span>
                  <span>Copie par blocs :</span>
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  <button
                    onClick={() => {
                      const nomComplet = [dossierData.entete?.prenom, dossierData.entete?.nom].filter(Boolean).join(' ');
                      if (nomComplet) {
                        navigator.clipboard.writeText(nomComplet);
                        toast.success('Nom complet copié !');
                      }
                    }}
                    className="px-3 py-2 text-xs rounded-lg bg-white text-gray-700 border border-gray-200 hover:border-[#F8485D] hover:text-[#F8485D] transition-all duration-200 hover:shadow-sm"
                  >
                    Nom complet
                  </button>
                  <button
                    onClick={() => {
                      if (dossierData.entete?.intitule_poste) {
                        navigator.clipboard.writeText(dossierData.entete.intitule_poste);
                        toast.success('Intitulé de poste copié !');
                      }
                    }}
                    className="px-3 py-2 text-xs rounded-lg bg-white text-gray-700 border border-gray-200 hover:border-[#F8485D] hover:text-[#F8485D] transition-all duration-200 hover:shadow-sm"
                  >
                    Intitulé de poste
                  </button>
                  <button
                    onClick={() => {
                      if (dossierData.entete?.annees_experience) {
                        navigator.clipboard.writeText(dossierData.entete.annees_experience.toString());
                        toast.success('Années d\'expérience copiées !');
                      }
                    }}
                    className="px-3 py-2 text-xs rounded-lg bg-white text-gray-700 border border-gray-200 hover:border-[#F8485D] hover:text-[#F8485D] transition-all duration-200 hover:shadow-sm"
                  >
                    Années d'expérience
                  </button>
                  <button
                    onClick={() => {
                      if (dossierData.entete?.resume_profil) {
                        navigator.clipboard.writeText(dossierData.entete.resume_profil);
                        toast.success('Résumé profil copié !');
                      }
                    }}
                    className="px-3 py-2 text-xs rounded-lg bg-white text-gray-700 border border-gray-200 hover:border-[#F8485D] hover:text-[#F8485D] transition-all duration-200 hover:shadow-sm md:col-span-2"
                  >
                    Résumé profil
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <CopyableField 
                  label="Nom complet" 
                  value={[dossierData.entete.prenom, dossierData.entete.nom].filter(Boolean).join(' ')}
                />
                <CopyableField 
                  label="Intitulé de Poste" 
                  value={dossierData.entete.intitule_poste}
                />
                <CopyableField 
                  label="Années d'Expérience" 
                  value={dossierData.entete.annees_experience?.toString()}
                />
                <CopyableField 
                  label="Résumé Profil" 
                  value={dossierData.entete.resume_profil}
                  multiline
                  className="md:col-span-2"
                />
              </div>
            </CollapsableSection>
          )}

          {/* Expériences clés récentes */}
          {dossierData.experiences_cles_recentes && dossierData.experiences_cles_recentes.length > 0 && (
            <CollapsableSection title="Expériences Clés Récentes">
              <CopyableExperiencesCles experiences={dossierData.experiences_cles_recentes} />
            </CollapsableSection>
          )}

          {/* Diplômes */}
          {dossierData.diplomes && dossierData.diplomes.length > 0 && (
            <CollapsableSection title="Diplômes">
              {/* Boutons de copie individuels */}
              <div className="mb-6 p-4 bg-green-50 rounded-lg border">
                <h4 className="text-sm font-medium text-green-900 mb-3">Copie par diplôme :</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {dossierData.diplomes.map((diplome, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        const diplomeText = [diplome.intitule, diplome.etablissement, diplome.annee].filter(Boolean).join(', ');
                        if (diplomeText) {
                          navigator.clipboard.writeText(diplomeText);
                          toast.success(`Diplôme ${index + 1} copié !`);
                        }
                      }}
                      className="px-3 py-2 text-xs rounded-md bg-white text-green-600 border border-green-200 hover:bg-green-50"
                    >
                      Copier diplôme {index + 1}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-6">
                {dossierData.diplomes.map((diplome, index) => (
                  <div key={index} className="border-l-4 border-green-200 pl-6 group">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">
                        Diplôme {index + 1}
                      </h3>
                      <button
                        onClick={() => {
                          const diplomeText = [diplome.intitule, diplome.etablissement, diplome.annee].filter(Boolean).join(', ');
                          if (diplomeText) {
                            navigator.clipboard.writeText(diplomeText);
                            toast.success(`Diplôme ${index + 1} copié !`);
                          }
                        }}
                        className="px-3 py-1 text-xs bg-green-100 text-green-600 rounded hover:bg-green-200 opacity-0 group-hover:opacity-100 transition-opacity"
                        title={`Copier diplôme ${index + 1}`}
                      >
                        Copier diplôme {index + 1}
                      </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <CopyableField 
                        label="Intitulé" 
                        value={diplome.intitule}
                      />
                      <CopyableField 
                        label="Établissement" 
                        value={diplome.etablissement}
                      />
                      <CopyableField 
                        label="Année" 
                        value={diplome.annee?.toString()}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CollapsableSection>
          )}

          {/* Certifications */}
          {dossierData.certifications && dossierData.certifications.length > 0 && (
            <CollapsableSection title="Certifications">
              {/* Boutons de copie par blocs */}
              <div className="mb-6 p-4 bg-purple-50 rounded-lg border">
                <h4 className="text-sm font-medium text-purple-900 mb-3">Copie par blocs :</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                  <button
                    onClick={() => {
                      const intitules = dossierData.certifications?.map(c => c.intitule).filter(Boolean).join('\n') || '';
                      if (intitules) {
                        navigator.clipboard.writeText(intitules);
                        toast.success('Intitulés des certifications copiés !');
                      }
                    }}
                    className="px-3 py-2 text-xs rounded-md bg-white text-purple-600 border border-purple-200 hover:bg-purple-50"
                  >
                    Tous les intitulés
                  </button>
                  <button
                    onClick={() => {
                      const organismes = dossierData.certifications?.map(c => c.organisme).filter(Boolean).join('\n') || '';
                      if (organismes) {
                        navigator.clipboard.writeText(organismes);
                        toast.success('Organismes copiés !');
                      }
                    }}
                    className="px-3 py-2 text-xs rounded-md bg-white text-purple-600 border border-purple-200 hover:bg-purple-50"
                  >
                    Tous les organismes
                  </button>
                  <button
                    onClick={() => {
                      const certifications = dossierData.certifications?.map(c => 
                        [c.intitule, c.organisme, c.annee].filter(Boolean).join(', ')
                      ).join('\n') || '';
                      if (certifications) {
                        navigator.clipboard.writeText(certifications);
                        toast.success('Toutes les certifications copiées !');
                      }
                    }}
                    className="px-3 py-2 text-xs rounded-md bg-white text-purple-600 border border-purple-200 hover:bg-purple-50"
                  >
                    Liste complète
                  </button>
                </div>
              </div>

              <div className="space-y-6">
                {dossierData.certifications.map((cert, index) => (
                  <div key={index} className="border-l-4 border-purple-200 pl-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <CopyableField 
                        label="Intitulé" 
                        value={cert.intitule}
                      />
                      <CopyableField 
                        label="Organisme" 
                        value={cert.organisme}
                      />
                      <CopyableField 
                        label="Année" 
                        value={cert.annee?.toString()}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CollapsableSection>
          )}

          {/* Langues */}
          {dossierData.langues && dossierData.langues.length > 0 && (
            <CollapsableSection title="Langues">
              {/* Boutons de copie par blocs */}
              <div className="mb-6 p-4 bg-indigo-50 rounded-lg border">
                <h4 className="text-sm font-medium text-indigo-900 mb-3">Copie par blocs :</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                  <button
                    onClick={() => {
                      const langues = dossierData.langues?.map(l => l.langue).filter(Boolean).join('\n') || '';
                      if (langues) {
                        navigator.clipboard.writeText(langues);
                        toast.success('Langues copiées !');
                      }
                    }}
                    className="px-3 py-2 text-xs rounded-md bg-white text-indigo-600 border border-indigo-200 hover:bg-indigo-50"
                  >
                    Toutes les langues
                  </button>
                  <button
                    onClick={() => {
                      const niveaux = dossierData.langues?.map(l => `${l.langue}: ${l.niveau}`).filter(Boolean).join('\n') || '';
                      if (niveaux) {
                        navigator.clipboard.writeText(niveaux);
                        toast.success('Langues avec niveaux copiées !');
                      }
                    }}
                    className="px-3 py-2 text-xs rounded-md bg-white text-indigo-600 border border-indigo-200 hover:bg-indigo-50"
                  >
                    Langues + niveaux
                  </button>
                  <button
                    onClick={() => {
                      const languesFormat = dossierData.langues?.map(l => 
                        `${l.langue} (${l.niveau})`
                      ).join(', ') || '';
                      if (languesFormat) {
                        navigator.clipboard.writeText(languesFormat);
                        toast.success('Format compact copié !');
                      }
                    }}
                    className="px-3 py-2 text-xs rounded-md bg-white text-indigo-600 border border-indigo-200 hover:bg-indigo-50"
                  >
                    Format compact
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {dossierData.langues.map((langue, index) => (
                  <div key={index} className="bg-gray-50 p-4 rounded-lg">
                    <CopyableField 
                      label="Langue" 
                      value={langue.langue}
                    />
                    <CopyableField 
                      label="Niveau" 
                      value={langue.niveau}
                      className="mt-2"
                    />
                  </div>
                ))}
              </div>
            </CollapsableSection>
          )}

          {/* Compétences techniques */}
          {dossierData.competences_techniques && (
            <CollapsableSection title="Compétences Techniques">
              {/* Bouton pour copier toutes les compétences techniques */}
              <div className="mb-6 p-4 bg-blue-50 rounded-lg border">
                <button
                  onClick={() => {
                    const allSkills = Object.entries(dossierData.competences_techniques || {})
                      .filter(([_, skills]) => skills && Array.isArray(skills) && skills.length > 0)
                      .map(([category, skills]) => {
                        const categoryName = category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                        return `${categoryName}:\n${(skills as string[]).map(skill => `- ${skill}`).join(',\n')}`;
                      })
                      .join('\n\n');
                    
                    if (allSkills) {
                      navigator.clipboard.writeText(allSkills);
                      toast.success('Toutes les compétences techniques copiées !');
                    }
                  }}
                  className="px-4 py-2 text-sm rounded-md bg-white text-blue-600 border border-blue-200 hover:bg-blue-50"
                >
                  Copier toutes les compétences techniques
                </button>
              </div>
              
              <div className="space-y-6">
                {Object.entries(dossierData.competences_techniques).map(([category, skills]) => (
                  skills && Array.isArray(skills) && skills.length > 0 && (
                    <CopyableList
                      key={category}
                      label={category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      items={skills}
                    />
                  )
                ))}
              </div>
            </CollapsableSection>
          )}

          {/* Expériences professionnelles détaillées */}
          {dossierData.experiences_professionnelles && dossierData.experiences_professionnelles.length > 0 && (
            <CollapsableSection title="Expériences Professionnelles Détaillées">
              <div className="space-y-8">
                {dossierData.experiences_professionnelles.map((exp, index) => (
                  <CopyableExperienceProfessionnelle
                    key={index}
                    experience={{
                      client: exp.client,
                      intitule_poste: exp.intitule_poste,
                      date_debut: exp.date_debut,
                      date_fin: exp.date_fin,
                      contexte: exp.contexte,
                      responsabilites: exp.responsabilites,
                      livrables: exp.livrables,
                      environnement_technique: exp.environnement_technique
                    }}
                    index={index}
                  />
                ))}
              </div>
            </CollapsableSection>
          )}
        </div>
      </div>
    </div>
  );
}
