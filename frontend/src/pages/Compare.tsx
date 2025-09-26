import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import FileUpload from '../components/FileUpload';
import AnalysisLoading from '../components/AnalysisLoading';

export default function Compare() {
  const navigate = useNavigate();

  const [cvFiles, setCvFiles] = useState<File[]>([]);
  const [missionFile, setMissionFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [analysisStage, setAnalysisStage] = useState('');
  const [progress, setProgress] = useState(0);
  const simulateProgress = () => {
    const stages = [
      "Initialisation de la comparaison...",
      "Lecture des fichiers...",
      "Extraction des informations...",
      "Analyse des compétences...",
      "Structuration des résultats...",
      "Finalisation..."
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
    }, 700);
    return interval;
  };

  const addCvFile = (file: File) => {
    setCvFiles((prev) => {
      const exists = prev.some((f) => f.name === file.name && f.size === file.size);
      if (exists) return prev;
      return [...prev, file];
    });
  };

  const setMultipleCvFiles = (files: FileList | null) => {
    if (!files) return;
    const arr = Array.from(files);
    setCvFiles((prev) => {
      const combined = [...prev];
      for (const f of arr) {
        if (!combined.some((c) => c.name === f.name && c.size === f.size)) combined.push(f);
      }
      return combined;
    });
  };

  const removeCvFile = (file: File) => {
    setCvFiles((prev) => prev.filter((f) => !(f.name === file.name && f.size === file.size)));
  };

  const clearAll = () => {
    setCvFiles([]);
    setMissionFile(null);
  };

  const canStart = cvFiles.length > 0 && missionFile !== null && !loading;

  const handleStartComparison = async () => {
    if (!canStart) return;
    // Prepare FormData for backend
    const form = new FormData();
    cvFiles.forEach((f) => form.append('cvs', f, f.name));
    form.append('mission', missionFile as File, missionFile!.name);

  setLoading(true);
  const progressInterval = simulateProgress();
    try {
      // Configuration de l'API dynamique
      const getApiBase = () => {
        if (import.meta.env.VITE_API_URL) {
          return import.meta.env.VITE_API_URL;
        }
        if (typeof window !== 'undefined') {
          const hostname = window.location.hostname;
          if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
            return window.location.origin;
          }
        }
        return 'http://localhost:8000';
      };
      
      const baseUrl = getApiBase();
      const resp = await fetch(`${baseUrl}/api/v1/compare`, {
        method: 'POST',
        body: form
      });

      if (!resp.ok) {
        const ct = resp.headers.get('content-type') || '';
        let body: any = null;
        let textBody = await resp.text();
        if (ct.includes('application/json')) {
          try { body = JSON.parse(textBody); } catch (_e) { body = textBody; }
        } else {
          body = textBody;
        }
        throw { status: resp.status, body, text: textBody };
      }

  const data = await resp.json();
  // Save full results to sessionStorage and navigate to dedicated results page
  try { sessionStorage.setItem('last_compare_results', JSON.stringify(data.results || [])); } catch (_e) {}
  navigate('/compare/result', { state: { results: data.results || [] } });

    } catch (err: any) {
      console.error('Compare error:', err);
      // Prefer structured backend detail
      if (err && err.body) {
        if (typeof err.body === 'object' && err.body.detail) {
          alert('Erreur lors de la comparaison: ' + err.body.detail);
          return;
        }
        try {
          alert('Erreur lors de la comparaison: ' + JSON.stringify(err.body, null, 2));
          return;
        } catch (_e) {
          // fallthrough
        }
      }

      // If it's a normal Error with message
      if (err && typeof err.message === 'string') {
        alert('Erreur lors de la comparaison: ' + err.message);
        return;
      }

      // Fallback: stringify the whole error
      try {
        alert('Erreur lors de la comparaison: ' + JSON.stringify(err, null, 2));
      } catch (_e) {
        alert('Erreur lors de la comparaison: ' + String(err));
      }
    } finally {
      try { clearInterval(progressInterval); } catch (_e) {}
      setLoading(false);
    }
  };

  // Results state
  const [results, setResults] = useState<Array<any>>([]);

  // Afficher l'écran de chargement pendant l'analyse
  if (loading) {
    return <AnalysisLoading stage={analysisStage} progress={progress} />;
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--bg)' }}>
      <Header title="" />

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Comparer un ou plusieurs CV avec une mission</h1>
            <p className="text-gray-600">Importez vos CV (un ou plusieurs) et le fichier de mission, puis lancez la comparaison.</p>
          </div>

          <div className="space-y-8">
            {/* CVs card */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100 bg-gradient-to-r from-gray-50 to-red-50">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
                  <span className="w-1 h-6 bg-[#F8485D] rounded-full" />
                  <span>Importer CV(s)</span>
                </h2>
                <p className="text-gray-600 text-sm mt-1">Formats supportés : PDF, DOCX, TXT</p>
              </div>
              <div className="p-6">
                <div className="mb-4">
                  {/* Use FileUpload in multiple mode so users can drop/select many CVs */}
                  <FileUpload
                    onFileSelect={addCvFile}
                    onFilesSelect={(files) => setCvFiles((prev) => {
                      const combined = [...prev];
                      for (const f of files) {
                        if (!combined.some((c) => c.name === f.name && c.size === f.size)) combined.push(f);
                      }
                      return combined;
                    })}
                    multiple
                    accept=".pdf,.docx,.pptx,.doc,.txt"
                    primaryText={'Glissez-déposez vos CV'}
                    browseText={'cliquez pour parcourir'}
                    supportedText={'Formats supportés : PDF, DOCX, TXT'}
                    maxSizeText={'Taille maximum : 10 MB'}
                    disabled={loading}
                  />

                  </div>

                  {cvFiles.length > 0 && (
                  <div className="mt-4 bg-gray-50 rounded-lg p-3 border border-gray-100">
                    <h3 className="text-sm font-medium mb-2">CV sélectionnés ({cvFiles.length})</h3>
                    <ul className="text-sm text-gray-700 space-y-1">
                      {cvFiles.map((f, idx) => (
                        <li key={`${f.name}-${f.size}-${idx}`} className="flex items-center justify-between">
                          <span className="truncate max-w-xs">{f.name}</span>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-gray-500">{Math.round(f.size / 1024)} KB</span>
                            <button className="text-sm text-red-600 ml-4" onClick={() => removeCvFile(f)}>Supprimer</button>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>

            {/* Mission card */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100 bg-gradient-to-r from-gray-50 to-red-50">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
                  <span className="w-1 h-6 bg-[#F8485D] rounded-full" />
                  <span>Fichier de mission</span>
                </h2>
                <p className="text-gray-600 text-sm mt-1">Formats supportés : PDF, DOCX, TXT</p>
              </div>
              <div className="p-6">
                <FileUpload
                  onFileSelect={(f) => setMissionFile(f)}
                  accept=".pdf,.docx,.pptx,.doc,.txt"
                  primaryText={'Glissez-déposez votre mission'}
                  browseText={'cliquez pour parcourir'}
                  supportedText={'Formats supportés : PDF, DOCX, TXT'}
                  maxSizeText={'Taille maximum : 10 MB'}
                  disabled={loading}
                />

                {missionFile && (
                  <div className="mt-4 bg-gray-50 rounded-lg p-3 border border-gray-100 flex items-center justify-between">
                    <span className="truncate max-w-xs">{missionFile.name}</span>
                    <button className="text-sm text-red-600 ml-4" onClick={() => setMissionFile(null)}>Supprimer</button>
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button className={`px-4 py-2 rounded-xl font-semibold text-white ${canStart ? 'bg-[#F8485D] hover:bg-[#e63946]' : 'bg-gray-300 cursor-not-allowed'}`} onClick={handleStartComparison} disabled={!canStart}>{loading ? 'Lancement...' : 'Lancer la comparaison'}</button>
              <button className="px-4 py-2 rounded-xl border border-gray-200" onClick={clearAll}>Réinitialiser</button>
            </div>

            {/* Results panel */}
            {results && results.length > 0 && (
              <div className="mt-6 bg-white rounded-2xl shadow-md border border-gray-200 p-6">
                <h3 className="text-lg font-semibold mb-3">Résultats de la comparaison</h3>
                <p className="text-sm text-gray-600 mb-4">CVs classés du plus pertinent au moins pertinent selon la mission.</p>

                <ol className="space-y-4">
                  {results.map((r: any, idx: number) => (
                    <li key={`res-${idx}`} className={`${idx === 0 ? 'border-2 border-[#F8485D] p-4 rounded-lg' : 'p-4 border border-gray-100 rounded-lg'}`}>
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-3">
                            <button className="font-medium text-left p-0" onClick={() => {
                              try { sessionStorage.setItem('last_compare_result', JSON.stringify(r)); } catch (_e) {}
                              navigate('/compare/result', { state: { result: r } });
                            }}>{r.filename || r.file || `CV ${idx + 1}`}</button>
                            <span className="text-xs text-gray-500">{r.score !== undefined ? `Score: ${r.score}` : ''}</span>
                          </div>
                          {r.summary && <p className="text-sm text-gray-600 mt-1">{r.summary}</p>}
                        </div>
                      </div>

                      {r.strengths && r.strengths.length > 0 && (
                        <ul className="mt-3 list-disc list-inside text-sm text-gray-700 space-y-1">
                          {r.strengths.map((s: string, i: number) => (
                            <li key={`s-${i}`}>{s}</li>
                          ))}
                        </ul>
                      )}
                    </li>
                  ))}
                </ol>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
