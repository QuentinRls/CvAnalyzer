import React, { useState } from 'react';
import { toast } from 'sonner';
import { generatePDF, generatePowerPoint } from '../lib/api';
import type { DossierCompetences } from '../lib/schemas';

interface ExportActionsProps {
  dossierData: DossierCompetences;
  className?: string;
}

export default function ExportActions({ dossierData, className = '' }: ExportActionsProps) {
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  // Google Docs generation removed
  const [isGeneratingPPTX, setIsGeneratingPPTX] = useState(false);

  const handleGeneratePDF = async () => {
    setIsGeneratingPDF(true);
    try {
      const pdfBlob = await generatePDF(dossierData);
      
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      
      const nomComplet = [dossierData.entete?.prenom, dossierData.entete?.nom]
        .filter(Boolean)
        .join('_');
      const filename = nomComplet 
        ? `${nomComplet}_CV.pdf` 
        : 'Dossier_Competences_CV.pdf';
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
      
      toast.success('PDF généré avec succès !');
    } catch (error) {
      console.error('Erreur lors de la génération du PDF:', error);
      toast.error('Erreur lors de la génération du PDF');
    } finally {
      setIsGeneratingPDF(false);
    }
  };

  // Google Docs generation removed

  const handleGeneratePowerPoint = async () => {
    setIsGeneratingPPTX(true);
    try {
      const pptxBlob = await generatePowerPoint(dossierData);
      
      const url = window.URL.createObjectURL(pptxBlob);
      const link = document.createElement('a');
      link.href = url;
      
      const nomComplet = [dossierData.entete?.prenom, dossierData.entete?.nom]
        .filter(Boolean)
        .join('_');
      const filename = nomComplet 
        ? `${nomComplet}_CV_Devoteam.pptx` 
        : 'Dossier_Competences_Devoteam.pptx';
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
      
      toast.success('Présentation PowerPoint Devoteam générée avec succès !');
    } catch (error) {
      console.error('Erreur lors de la génération PowerPoint:', error);
      toast.error('Erreur lors de la génération PowerPoint');
    } finally {
      setIsGeneratingPPTX(false);
    }
  };

  return (
    <div className={`flex flex-col sm:flex-row gap-3 ${className}`}>
      {/* Bouton PDF */}
      <button
        onClick={handleGeneratePDF}
        disabled={isGeneratingPDF}
        className="
          group relative overflow-hidden
          bg-gradient-to-r from-[#F8485D] to-[#e73c52] 
          hover:from-[#e73c52] hover:to-[#d6334a]
          text-white font-semibold py-3 px-6 rounded-xl
          transform transition-all duration-200 
          hover:scale-105 hover:shadow-lg
          disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
          flex items-center justify-center space-x-2
          w-full sm:w-auto
        "
      >
        {/* Background animation */}
        <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/10 to-white/0 skew-x-12 transform -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
        
        {/* Icon */}
        <div className="relative z-10">
          {isGeneratingPDF ? (
            <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          ) : (
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          )}
        </div>
        
        {/* Text */}
        <span className="relative z-10">
          {isGeneratingPDF ? 'Génération PDF...' : 'PDF'}
        </span>
      </button>

      {/* Google Docs button removed */}

      {/* Bouton PowerPoint Devoteam */}
      <button
        onClick={handleGeneratePowerPoint}
        disabled={isGeneratingPPTX}
        className="
          group relative overflow-hidden
          bg-gradient-to-r from-[#FF6B35] to-[#e55a2b] 
          hover:from-[#e55a2b] hover:to-[#cc4e22]
          text-white font-semibold py-3 px-6 rounded-xl
          transform transition-all duration-200 
          hover:scale-105 hover:shadow-lg
          disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
          flex items-center justify-center space-x-2
          w-full sm:w-auto
        "
      >
        {/* Background animation */}
        <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/10 to-white/0 skew-x-12 transform -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
        
        {/* Icon */}
        <div className="relative z-10">
          {isGeneratingPPTX ? (
            <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          ) : (
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m0 0V2a1 1 0 011-1h2a1 1 0 011 1v16a1 1 0 01-1 1H4a1 1 0 01-1-1V5a1 1 0 011-1h2a1 1 0 011-1V4m0 0h10M9 7h6m-6 3h6m-6 3h6" />
            </svg>
          )}
        </div>
        
        {/* Text */}
        <span className="relative z-10">
          {isGeneratingPPTX ? 'Génération PPTX...' : 'PowerPoint'}
        </span>
      </button>
    </div>
  );
}
