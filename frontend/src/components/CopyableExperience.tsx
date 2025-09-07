import { useState } from 'react';
import { toast } from 'sonner';
import CopyableField from './CopyableField';

interface ExperienceData {
  entreprise?: string;
  poste?: string;
  duree?: string;
  missions?: string[];
  competences?: string[];
}

interface CopyableExperienceProps {
  experience: ExperienceData;
  index: number;
}

export default function CopyableExperience({ experience, index }: CopyableExperienceProps) {
  const [copied, setCopied] = useState(false);

  const formatExperience = () => {
    const parts = [];
    
    // En-tête : Client, Poste, Durée
    if (experience.entreprise) parts.push(experience.entreprise);
    if (experience.poste) parts.push(experience.poste);
    if (experience.duree) parts.push(experience.duree);
    
    // Contexte séparé
    if (experience.missions && experience.missions.length > 0) {
      // Séparer le contexte des autres missions
      const contexteItems = experience.missions.filter(mission => 
        mission.toLowerCase().includes('contexte')
      );
      const autresMissions = experience.missions.filter(mission => 
        !mission.toLowerCase().includes('contexte')
      );
      
      // Ajouter le contexte s'il existe
      if (contexteItems.length > 0) {
        parts.push('Contexte.');
        contexteItems.forEach(contexte => {
          // Enlever "Contexte: " au début s'il existe
          const cleanContexte = contexte.replace(/^Contexte:\s*/i, '');
          parts.push(cleanContexte);
        });
      }
      
      // Ajouter les responsabilités
      if (autresMissions.length > 0) {
        parts.push('Responsabilités.');
        autresMissions.forEach(mission => parts.push(`- ${mission}`));
      }
    }
    
    // Livrables (si on en a dans les missions)
    // Pour l'instant, on les inclut dans responsabilités, mais on pourrait les séparer
    
    // Environnement technique
    if (experience.competences && experience.competences.length > 0) {
      parts.push('Environnement technique.');
      const groupedTech = experience.competences.join(', ');
      parts.push(`- ${groupedTech}`);
    }
    
    return parts.join('\n');
  };

  const handleCopyAll = async () => {
    try {
      const fullText = formatExperience();
      await navigator.clipboard.writeText(fullText);
      setCopied(true);
      toast.success('Expérience complète copiée !');
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast.error('Erreur lors de la copie');
    }
  };

  const handleCopyList = async (items: string[], label: string) => {
    try {
      const textToCopy = items.join('\n- ');
      await navigator.clipboard.writeText(`- ${textToCopy}`);
      toast.success(`${label} copiées !`);
    } catch (error) {
      toast.error('Erreur lors de la copie');
    }
  };

  return (
    <div className="border border-gray-200 rounded-lg p-6 bg-white group">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Expérience {index + 1}
        </h3>
        <button
          onClick={handleCopyAll}
          className={`px-3 py-1 text-xs rounded-md transition-all duration-200 ${
            copied 
              ? 'bg-green-100 text-green-600' 
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200 opacity-0 group-hover:opacity-100'
          }`}
          title="Copier toute l'expérience"
        >
          {copied ? 'Copiée !' : 'Copier tout'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <CopyableField 
          label="Entreprise" 
          value={experience.entreprise}
        />
        <CopyableField 
          label="Poste" 
          value={experience.poste}
        />
        <CopyableField 
          label="Durée" 
          value={experience.duree}
          className="md:col-span-2"
        />
      </div>

      {experience.missions && experience.missions.length > 0 && (
        <div className="mb-4 group/missions">
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700">
              Missions
            </label>
            <button
              onClick={() => handleCopyList(experience.missions!, 'Missions')}
              className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded hover:bg-gray-200 opacity-0 group-hover/missions:opacity-100 transition-opacity"
            >
              Copier
            </button>
          </div>
          <div className="space-y-2">
            {experience.missions.map((mission, idx) => (
              <CopyableField
                key={idx}
                label={`Mission ${idx + 1}`}
                value={mission}
                multiline
              />
            ))}
          </div>
        </div>
      )}

      {experience.competences && experience.competences.length > 0 && (
        <div className="group/competences">
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700">
              Compétences
            </label>
            <button
              onClick={() => handleCopyList(experience.competences!, 'Compétences')}
              className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded hover:bg-gray-200 opacity-0 group-hover/competences:opacity-100 transition-opacity"
            >
              Copier
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {experience.competences.map((comp, idx) => (
              <CopyableField
                key={idx}
                label={`Compétence ${idx + 1}`}
                value={comp}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
