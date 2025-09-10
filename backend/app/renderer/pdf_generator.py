from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from io import BytesIO
from typing import List
import logging

from ..schemas import DossierCompetences, ExperienceProfessionnelle

logger = logging.getLogger(__name__)


class CVPDFGenerator:
    """Générateur de PDF pour les dossiers de compétences"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configuration des styles personnalisés"""
        # Utilisons des variables d'instance pour éviter les conflits
        
        # Style pour les titres de section
        self.section_style = ParagraphStyle(
            'CVSectionTitle',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=8,
            textColor=colors.HexColor('#F8485D'),
            fontName='Helvetica-Bold'
        )
        
        # Style pour les sous-titres
        self.subtitle_style = ParagraphStyle(
            'CVSubTitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=4,
            textColor=colors.HexColor('#333333'),
            fontName='Helvetica-Bold'
        )
        
        # Style pour le texte principal
        self.body_style = ParagraphStyle(
            'CVBodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=3,
            textColor=colors.HexColor('#555555')
        )
        
        # Style pour les listes
        self.bullet_style = ParagraphStyle(
            'CVBulletText',
            parent=self.styles['Normal'],
            fontSize=9,
            leftIndent=15,
            bulletIndent=8,
            spaceAfter=2,
            textColor=colors.HexColor('#666666')
        )
    
    def generate_pdf(self, dossier: DossierCompetences) -> BytesIO:
        """Génère un PDF à partir des données du dossier de compétences"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Construction du contenu
        story = []
        
        # En-tête
        self._add_header(story, dossier.entete)
        
        # Résumé professionnel
        if dossier.entete.resume_profil:
            self._add_professional_summary(story, dossier.entete.resume_profil)
        
        # Expériences clés récentes
        if dossier.experiences_cles_recentes:
            self._add_key_experiences(story, dossier.experiences_cles_recentes)
        
        # Compétences techniques
        self._add_technical_skills(story, dossier.competences_techniques)
        
        # Compétences fonctionnelles
        self._add_functional_skills(story, dossier.competences_fonctionnelles)
        
        # Formation et certifications
        self._add_education_certifications(story, dossier.diplomes, dossier.certifications)
        
        # Langues
        if dossier.langues:
            self._add_languages(story, dossier.langues)
        
        # Expériences professionnelles détaillées
        if dossier.experiences_professionnelles:
            self._add_detailed_experiences(story, dossier.experiences_professionnelles)
        
        # Construction du PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _add_header(self, story: List, entete):
        """Ajoute l'en-tête du CV"""
        # Nom complet
        nom_complet = f"{entete.prenom} {entete.nom}".strip()
        if nom_complet:
            story.append(Paragraph(nom_complet, self.styles['Title']))
            story.append(Spacer(1, 4))  # Réduit de 6 à 4
        
        # Intitulé de poste
        if entete.intitule_poste:
            story.append(Paragraph(entete.intitule_poste, self.subtitle_style))
            story.append(Spacer(1, 4))  # Réduit de 6 à 4
        
        # Années d'expérience
        if entete.annees_experience:
            story.append(Paragraph(f"<b>Expérience :</b> {entete.annees_experience}", self.body_style))
            story.append(Spacer(1, 8))  # Réduit de 12 à 8
    
    def _add_professional_summary(self, story: List, resume_profil: str):
        """Ajoute le résumé professionnel"""
        story.append(Paragraph("Résumé Professionnel", self.section_style))
        story.append(Paragraph(resume_profil, self.body_style))
        story.append(Spacer(1, 8))  # Réduit de 12 à 8
    
    def _add_key_experiences(self, story: List, experiences):
        """Ajoute les expériences clés récentes"""
        story.append(Paragraph("Expériences Clés Récentes", self.section_style))
        
        for exp in experiences:
            if exp.client or exp.intitule_poste:
                # Afficher le titre avec la durée sur la même ligne
                title = f"<b>{exp.client}</b> - {exp.intitule_poste}" if exp.client else exp.intitule_poste
                if exp.duree:
                    title += f" - ({exp.duree})"
                story.append(Paragraph(title, self.subtitle_style))
            
            if exp.description_breve:
                story.append(Paragraph(exp.description_breve, self.body_style))
            
            story.append(Spacer(1, 6))  # Réduit de 8 à 6
        
        story.append(Spacer(1, 6))  # Réduit de 8 à 6
    
    def _add_technical_skills(self, story: List, competences):
        """Ajoute les compétences techniques"""
        story.append(Paragraph("Compétences Techniques", self.section_style))
        
        skills_sections = [
            ("Langages & Frameworks", competences.language_framework),
            ("CI/CD", competences.ci_cd),
            ("State Management", competences.state_management),
            ("Tests", competences.tests),
            ("Outils", competences.outils),
            ("Base de données & Big Data", competences.base_de_donnees_big_data),
            ("Data Analytics & Visualisation", competences.data_analytics_visualisation),
            ("Collaboration", competences.collaboration),
            ("UX/UI", competences.ux_ui)
        ]
        
        for section_name, skills_list in skills_sections:
            if skills_list:
                story.append(Paragraph(f"<b>{section_name} :</b>", self.body_style))
                skills_text = " • ".join(skills_list)
                story.append(Paragraph(skills_text, self.bullet_style))
                story.append(Spacer(1, 3))  # Réduit de 4 à 3
        
        story.append(Spacer(1, 6))  # Réduit de 8 à 6
    
    def _add_functional_skills(self, story: List, competences):
        """Ajoute les compétences fonctionnelles"""
        story.append(Paragraph("Compétences Fonctionnelles", self.section_style))
        
        if competences.gestion_de_projet:
            story.append(Paragraph("<b>Gestion de Projet :</b>", self.body_style))
            skills_text = " • ".join(competences.gestion_de_projet)
            story.append(Paragraph(skills_text, self.bullet_style))
        
        if competences.methodologie_scrum:
            story.append(Paragraph("<b>Méthodologie Scrum :</b>", self.body_style))
            skills_text = " • ".join(competences.methodologie_scrum)
            story.append(Paragraph(skills_text, self.bullet_style))
        
        if competences.encadrement:
            story.append(Paragraph(f"<b>Encadrement :</b> {competences.encadrement}", self.body_style))
        
        # Compétences booléennes
        bool_skills = []
        if competences.revue_de_code:
            bool_skills.append("Revue de code")
        if competences.peer_programming:
            bool_skills.append("Peer programming")
        if competences.qualite_des_livrables:
            bool_skills.append("Qualité des livrables")
        
        if bool_skills:
            story.append(Paragraph("<b>Autres compétences :</b>", self.body_style))
            skills_text = " • ".join(bool_skills)
            story.append(Paragraph(skills_text, self.bullet_style))
        
        story.append(Spacer(1, 6))  # Réduit de 12 à 6
    
    def _add_education_certifications(self, story: List, diplomes, certifications):
        """Ajoute la formation et les certifications"""
        if diplomes or certifications:
            story.append(Paragraph("Formation & Certifications", self.section_style))
        
        if diplomes:
            story.append(Paragraph("<b>Diplômes :</b>", self.body_style))
            for diplome in diplomes:
                text = f"{diplome.intitule}"
                if diplome.etablissement:
                    text += f" - {diplome.etablissement}"
                if diplome.annee:
                    text += f" ({diplome.annee})"
                story.append(Paragraph(f"• {text}", self.bullet_style))
        
        if certifications:
            story.append(Paragraph("<b>Certifications :</b>", self.body_style))
            for cert in certifications:
                text = f"{cert.intitule}"
                if cert.organisme:
                    text += f" - {cert.organisme}"
                if cert.annee:
                    text += f" ({cert.annee})"
                story.append(Paragraph(f"• {text}", self.bullet_style))
        
        if diplomes or certifications:
            story.append(Spacer(1, 6))  # Réduit de 12 à 6
    
    def _add_languages(self, story: List, langues):
        """Ajoute les langues"""
        story.append(Paragraph("Langues", self.section_style))
        for langue in langues:
            text = f"{langue.langue}"
            if langue.niveau:
                text += f" - {langue.niveau}"
            story.append(Paragraph(f"• {text}", self.bullet_style))
        story.append(Spacer(1, 6))  # Réduit de 12 à 6
    
    def _add_detailed_experiences(self, story: List, experiences: List[ExperienceProfessionnelle]):
        """Ajoute les expériences professionnelles détaillées"""
        story.append(PageBreak())
        story.append(Paragraph("Expériences Professionnelles Détaillées", self.section_style))
        
        for i, exp in enumerate(experiences):
            if i > 0:
                story.append(Spacer(1, 12))  # Réduit de 16 à 12
            
            # Titre de l'expérience
            title = f"<b>{exp.client}</b> - {exp.intitule_poste}" if exp.client else exp.intitule_poste
            story.append(Paragraph(title, self.subtitle_style))
            
            # Dates
            if exp.date_debut or exp.date_fin:
                dates = f"{exp.date_debut or ''} - {exp.date_fin or 'En cours'}"
                story.append(Paragraph(f"<i>{dates}</i>", self.body_style))
            
            # Contexte
            if exp.contexte:
                story.append(Paragraph("<b>Contexte :</b>", self.body_style))
                story.append(Paragraph(exp.contexte, self.body_style))
            
            # Responsabilités
            if exp.responsabilites:
                story.append(Paragraph("<b>Responsabilités :</b>", self.body_style))
                for resp in exp.responsabilites:
                    story.append(Paragraph(f"• {resp}", self.bullet_style))
            
            # Livrables
            if exp.livrables:
                story.append(Paragraph("<b>Livrables :</b>", self.body_style))
                for livrable in exp.livrables:
                    story.append(Paragraph(f"• {livrable}", self.bullet_style))
            
            # Environnement technique
            if hasattr(exp, 'environnement_technique') and exp.environnement_technique:
                env_tech = exp.environnement_technique
                tech_items = []
                
                if env_tech.language_framework:
                    tech_items.extend(env_tech.language_framework)
                if env_tech.outils:
                    tech_items.extend(env_tech.outils)
                if env_tech.base_de_donnees_big_data:
                    tech_items.extend(env_tech.base_de_donnees_big_data)
                
                if tech_items:
                    story.append(Paragraph("<b>Environnement technique :</b>", self.body_style))
                    tech_text = " • ".join(tech_items)
                    story.append(Paragraph(tech_text, self.bullet_style))


def generate_cv_pdf(dossier: DossierCompetences) -> BytesIO:
    """Fonction principale pour générer un PDF du CV"""
    try:
        generator = CVPDFGenerator()
        return generator.generate_pdf(dossier)
    except Exception as e:
        logger.error(f"Erreur lors de la génération du PDF: {e}")
        raise
