import { useState } from 'react';
import { toast } from 'sonner';
import CopyableField from './CopyableField';

interface ExperienceCleData {
  intitule_poste?: string;
  client?: string;
  duree?: string;
  description_breve?: string;
}

interface CopyableExperiencesClesProps {
  experiences: ExperienceCleData[];
}

export default function CopyableExperiencesCles({ experiences }: CopyableExperiencesClesProps) {
  const [copied, setCopied] = useState(false);

  const formatAllExperiences = () => {
    let result = "Expériences clés récentes.\n";
    
    experiences.forEach(exp => {
      // Format: "Client x Entreprise, Poste, Durée"
      if (exp.client && exp.intitule_poste && exp.duree) {
        result += `${exp.client}, ${exp.intitule_poste}, ${exp.duree}\n`;
      } else {
        // Fallback si certains champs manquent
        const line = [exp.client, exp.intitule_poste, exp.duree].filter(Boolean).join(', ');
        if (line) result += `${line}\n`;
      }
      
      // Description développée avec retour à la ligne automatique
      if (exp.description_breve) {
        // Découper la description en lignes de maximum 80 caractères
        const words = exp.description_breve.split(' ');
        let currentLine = '';
        
        words.forEach(word => {
          if (currentLine.length + word.length + 1 <= 80) {
            currentLine += (currentLine ? ' ' : '') + word;
          } else {
            if (currentLine) result += `${currentLine}\n`;
            currentLine = word;
          }
        });
        
        if (currentLine) result += `${currentLine}\n`;
      }
      
      // Ajouter une ligne vide entre les expériences
      result += '\n';
    });
    
    return result.trim();
  };

  const formatSingleExperience = (exp: ExperienceCleData) => {
    let result = '';
    
    // Format: "Client, Poste, Durée"
    if (exp.client && exp.intitule_poste && exp.duree) {
      result += `${exp.client}, ${exp.intitule_poste}, ${exp.duree}\n`;
    } else {
      const line = [exp.client, exp.intitule_poste, exp.duree].filter(Boolean).join(', ');
      if (line) result += `${line}\n`;
    }
    
    // Description développée avec retour à la ligne automatique
    if (exp.description_breve) {
      // Découper la description en lignes de maximum 80 caractères
      const words = exp.description_breve.split(' ');
      let currentLine = '';
      
      words.forEach(word => {
        if (currentLine.length + word.length + 1 <= 80) {
          currentLine += (currentLine ? ' ' : '') + word;
        } else {
          if (currentLine) result += `${currentLine}\n`;
          currentLine = word;
        }
      });
      
      if (currentLine) result += `${currentLine}`;
    }
    
    return result;
  };

  const handleCopyAll = async () => {
    try {
      const fullText = formatAllExperiences();
      await navigator.clipboard.writeText(fullText);
      setCopied(true);
      toast.success('Toutes les expériences clés copiées !');
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast.error('Erreur lors de la copie');
    }
  };

  const handleCopySingle = async (exp: ExperienceCleData, index: number) => {
    try {
      const text = formatSingleExperience(exp);
      await navigator.clipboard.writeText(text);
      toast.success(`Expérience ${index + 1} copiée !`);
    } catch (error) {
      toast.error('Erreur lors de la copie');
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <button
          onClick={handleCopyAll}
          className={`px-4 py-2 text-sm rounded-md transition-all duration-200 ${
            copied 
              ? 'bg-green-100 text-green-600' 
              : 'bg-blue-100 text-blue-600 hover:bg-blue-200'
          }`}
          title="Copier toutes les expériences au format demandé"
        >
          {copied ? 'Toutes copiées !' : 'Copier toutes les expériences'}
        </button>
      </div>
      <div className="space-y-6">
        {experiences.map((exp, index) => (
          <div key={index} className="border-l-4 border-blue-200 pl-6 group">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Expérience {index + 1}
              </h3>
              <button
                onClick={() => handleCopySingle(exp, index)}
                className="px-3 py-1 text-xs bg-gray-100 text-gray-600 rounded hover:bg-gray-200 opacity-0 group-hover:opacity-100 transition-opacity"
                title="Copier cette expérience au format demandé"
              >
                Copier cette expérience
              </button>
            </div>

            {/* Aperçu du format */}
            <div className="mb-4 p-3 bg-gray-50 rounded-lg border">
              <label className="block text-xs font-medium text-gray-500 mb-1">
                Aperçu du format de copie :
              </label>
              <div className="text-sm text-gray-700 whitespace-pre-line">
                {formatSingleExperience(exp) || 'Informations manquantes'}
              </div>
            </div>

            {/* Champs individuels éditables */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <CopyableField 
                label="Client" 
                value={exp.client}
              />
              <CopyableField 
                label="Intitulé de Poste" 
                value={exp.intitule_poste}
              />
              <CopyableField 
                label="Durée" 
                value={exp.duree}
              />
              <CopyableField 
                label="Description Brève" 
                value={exp.description_breve}
                multiline
                className="md:col-span-2"
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
