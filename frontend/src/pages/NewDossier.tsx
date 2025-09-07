import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { postExtract } from '../lib/api';
import { storage, STORAGE_KEYS, errorHelpers } from '../lib/utils';
import Header from '../components/Header';
import AnalysisLoading from '../components/AnalysisLoading';
import FileUpload from '../components/FileUpload';

export default function NewDossier() {
  const [loading, setLoading] = useState(false);
  const [textInput, setTextInput] = useState('');
  const [analysisStage, setAnalysisStage] = useState('');
  const [progress, setProgress] = useState(0);
  const navigate = useNavigate();

  const simulateProgress = () => {
    const stages = [
      'Initialisation de l\'analyse...',
      'Lecture du document...',
      'Extraction des informations...',
      'Analyse des compétences...',
      'Structuration des données...',
      'Finalisation...'
    ];
    
    let currentStage = 0;
    setProgress(0);
    setAnalysisStage(stages[0]);
    
    const interval = setInterval(() => {
      currentStage++;
      if (currentStage < stages.length) {
        setAnalysisStage(stages[currentStage]);
        setProgress((currentStage / stages.length) * 100);
      } else {
        clearInterval(interval);
      }
    }, 800);
    
    return interval;
  };

  const handleFile = async (file: File) => {
    try {
      setLoading(true);
      const progressInterval = simulateProgress();
      
      const data = await postExtract(file);
      clearInterval(progressInterval);
      
      storage.set(STORAGE_KEYS.LAST_DRAFT, data);
      toast.success('CV analysé avec succès !');
      navigate('/review');
    } catch (error) {
      toast.error(errorHelpers.getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const handleTextSubmit = async () => {
    if (!textInput.trim() || textInput.length < 50) {
      toast.error('Le texte doit contenir au moins 50 caractères');
      return;
    }

    try {
      setLoading(true);
      const progressInterval = simulateProgress();
      
      const data = await postExtract(textInput);
      clearInterval(progressInterval);
      
      storage.set(STORAGE_KEYS.LAST_DRAFT, data);
      toast.success('Texte analysé avec succès !');
      navigate('/review');
    } catch (error) {
      toast.error(errorHelpers.getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  // Afficher l'écran de chargement pendant l'analyse
  if (loading) {
    return <AnalysisLoading stage={analysisStage} progress={progress} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-red-50">
      <Header 
        title="Nouvelle Analyse" 
        subtitle="Importez votre CV pour commencer"
        onNewAnalysis={() => navigate('/')}
      />
      
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              Analyser un nouveau CV
            </h1>
            <p className="text-gray-600">
              Importez votre CV en glissant-déposant un fichier ou en collant le texte directement
            </p>
          </div>

          <div className="space-y-8">
            {/* Upload File Section */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100 bg-gradient-to-r from-gray-50 to-red-50">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
                  <span className="w-1 h-6 bg-[#F8485D] rounded-full"></span>
                  <span>Importer un fichier CV</span>
                </h2>
                <p className="text-gray-600 text-sm mt-1">
                  Formats supportés : PDF, DOCX, TXT
                </p>
              </div>
              <div className="p-6">
                <FileUpload onFileSelect={handleFile} disabled={loading} />
              </div>
            </div>

            {/* Text Input Section */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100 bg-gradient-to-r from-gray-50 to-red-50">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
                  <span className="w-1 h-6 bg-[#F8485D] rounded-full"></span>
                  <span>Ou coller le texte du CV</span>
                </h2>
                <p className="text-gray-600 text-sm mt-1">
                  Minimum 50 caractères requis
                </p>
              </div>
              <div className="p-6">
                <textarea
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  placeholder="Collez ici le contenu de votre CV..."
                  className="w-full h-48 p-4 border-2 border-gray-200 rounded-xl resize-none focus:ring-2 focus:ring-[#F8485D] focus:border-[#F8485D] transition-all duration-200"
                  disabled={loading}
                />
                <div className="flex justify-between items-center mt-4">
                  <span className={`text-sm ${textInput.length >= 50 ? 'text-green-600' : 'text-gray-500'}`}>
                    {textInput.length} caractères {textInput.length >= 50 ? '✓' : `(minimum 50)`}
                  </span>
                  <button
                    onClick={handleTextSubmit}
                    disabled={loading || textInput.length < 50}
                    className="px-6 py-3 bg-[#F8485D] text-white rounded-xl font-semibold transition-all duration-200 transform hover:scale-105 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                  >
                    Analyser le texte
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
