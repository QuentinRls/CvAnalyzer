"""
Générateur de présentation PowerPoint avec template Devoteam
"""
from io import BytesIO
from typing import List
import logging
import os

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

from ..schemas import DossierCompetences, ExperienceProfessionnelle

logger = logging.getLogger(__name__)

# Couleurs Devoteam
DEVOTEAM_RED = RGBColor(248, 72, 93)  # #F8485D
DEVOTEAM_GREEN = RGBColor(0, 150, 136)  # #009688
DARK_GRAY = RGBColor(51, 51, 51)  # #333333
LIGHT_GRAY = RGBColor(102, 102, 102)  # #666666
BACKGROUND_GRAY = RGBColor(245, 245, 245)  # #F5F5F5

# Chemin vers l'image Devoteam
DEVOTEAM_LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "devoteam.png")


class DevoteamPPTXGenerator:
    """Générateur de présentation PowerPoint avec template Devoteam"""
    
    def __init__(self):
        """Initialise le générateur avec une présentation vide"""
        self.prs = Presentation()
        self.prs.slide_width = Inches(13.33)  # Format 16:9
        self.prs.slide_height = Inches(7.5)
        
    def generate_presentation(self, dossier: DossierCompetences) -> BytesIO:
        """
        Génère une présentation PowerPoint complète
        
        Args:
            dossier: Données structurées du CV
            
        Returns:
            BytesIO contenant le fichier PPTX
        """
        try:
            # Slide 1: Page de présentation
            self._create_title_slide(dossier)
            
            # Slide 2: Compétences
            self._create_skills_slide(dossier)
            
            # Slides 3+: Expériences détaillées
            if dossier.experiences_professionnelles:
                for exp in dossier.experiences_professionnelles:
                    self._create_experience_slide(exp)
            
            # Sauvegarder en BytesIO
            buffer = BytesIO()
            self.prs.save(buffer)
            buffer.seek(0)
            
            logger.info("Présentation PowerPoint générée avec succès")
            return buffer
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération PowerPoint : {str(e)}")
            raise
    
    def _add_devoteam_logo(self, slide, x=Inches(0.5), y=Inches(0.3), size=Inches(0.8)):
        """Ajoute le logo Devoteam à une slide en préservant ses proportions originales"""
        try:
            if os.path.exists(DEVOTEAM_LOGO_PATH):
                # Utiliser l'image réelle avec ses dimensions naturelles
                # On spécifie largeur ET hauteur pour forcer des proportions carrées
                logo_shape = slide.shapes.add_picture(DEVOTEAM_LOGO_PATH, x, y, width=size, height=size)
                return logo_shape
            else:
                # Fallback avec texte si l'image n'existe pas
                logger.warning(f"Image Devoteam non trouvée à {DEVOTEAM_LOGO_PATH}, utilisation du texte")
                # Pour le texte, on utilise des dimensions carrées
                logo_box = slide.shapes.add_textbox(x, y, size, size)
                logo_frame = logo_box.text_frame
                logo_frame.text = "devoteam"
                logo_para = logo_frame.paragraphs[0]
                logo_para.font.size = Pt(20)
                logo_para.font.color.rgb = DEVOTEAM_RED
                logo_para.font.bold = True
                return logo_box
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du logo : {str(e)}")
            # Fallback avec texte en cas d'erreur
            logo_box = slide.shapes.add_textbox(x, y, size, size)
            logo_frame = logo_box.text_frame
            logo_frame.text = "devoteam"
            logo_para = logo_frame.paragraphs[0]
            logo_para.font.size = Pt(20)
            logo_para.font.color.rgb = DEVOTEAM_RED
            logo_para.font.bold = True
            return logo_box
    
    def _create_title_slide(self, dossier: DossierCompetences):
        """Crée la slide de titre avec présentation générale"""
        slide_layout = self.prs.slide_layouts[6]  # Layout vide
        slide = self.prs.slides.add_slide(slide_layout)
        
        # Fond blanc
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(255, 255, 255)  # Blanc
        
        # Logo Devoteam avec image - positionné plus en haut et plus à gauche
        self._add_devoteam_logo(slide, Inches(0.2), Inches(0.1), Inches(0.8))
        
        # Titre principal
        if dossier.entete and dossier.entete.intitule_poste:
            title_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(12), Inches(1))
            title_frame = title_box.text_frame
            title_frame.text = dossier.entete.intitule_poste
            title_para = title_frame.paragraphs[0]
            title_para.font.size = Pt(36)
            title_para.font.color.rgb = DEVOTEAM_RED
            title_para.font.bold = True
        
        # Sous-titre (années d'expérience)
        if dossier.entete and dossier.entete.annees_experience:
            subtitle_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.3), Inches(12), Inches(0.5))
            subtitle_frame = subtitle_box.text_frame
            
            # Ajouter "années d'expérience" si ce n'est pas déjà présent
            exp_text = dossier.entete.annees_experience
            if not any(word in exp_text.lower() for word in ['année', 'ans', 'expérience']):
                exp_text = f"{exp_text} années d'expérience"
            
            subtitle_frame.text = exp_text
            subtitle_para = subtitle_frame.paragraphs[0]
            subtitle_para.font.size = Pt(18)
            subtitle_para.font.color.rgb = DEVOTEAM_RED
        
        # Nom
        if dossier.entete:
            nom_complet = f"{dossier.entete.prenom or ''} {dossier.entete.nom or ''}".strip()
            if nom_complet:
                name_box = slide.shapes.add_textbox(Inches(0.5), Inches(3), Inches(12), Inches(0.7))
                name_frame = name_box.text_frame
                name_frame.text = nom_complet
                name_para = name_frame.paragraphs[0]
                name_para.font.size = Pt(24)
                name_para.font.color.rgb = DEVOTEAM_RED
                name_para.font.bold = True
        
        # Résumé professionnel (si disponible) - Bloc plus compact et remonté
        if dossier.entete and dossier.entete.resume_profil:
            summary_box = slide.shapes.add_textbox(Inches(0.5), Inches(3.8), Inches(5), Inches(0.8))
            summary_frame = summary_box.text_frame
            summary_frame.text = dossier.entete.resume_profil
            summary_para = summary_frame.paragraphs[0]
            summary_para.font.size = Pt(14)
            summary_para.font.color.rgb = LIGHT_GRAY
            summary_para.font.italic = True
        
        # Section gauche: Diplômes - remontée
        diplomes_title = slide.shapes.add_textbox(Inches(0.5), Inches(4.8), Inches(5.5), Inches(0.4))
        diplomes_title_frame = diplomes_title.text_frame
        diplomes_title_frame.text = "Diplômes."
        diplomes_title_para = diplomes_title_frame.paragraphs[0]
        diplomes_title_para.font.size = Pt(18)
        diplomes_title_para.font.color.rgb = DEVOTEAM_RED
        diplomes_title_para.font.bold = True
        
        # Contenu des diplômes
        if dossier.diplomes:
            diplomes_content = []
            for diplome in dossier.diplomes:
                diplome_text = f"🎓 {diplome.intitule or 'Diplôme'}"
                if diplome.etablissement:
                    diplome_text += f"\n{diplome.etablissement}"
                if diplome.annee:
                    diplome_text += f"\n{diplome.annee}"
                diplomes_content.append(diplome_text)
            
            diplomes_box = slide.shapes.add_textbox(Inches(0.5), Inches(5.3), Inches(5.5), Inches(1.5))
            diplomes_frame = diplomes_box.text_frame
            diplomes_frame.text = "\n\n".join(diplomes_content)
            for para in diplomes_frame.paragraphs:
                para.font.size = Pt(12)
                para.font.color.rgb = DARK_GRAY
        
        # Section droite: Expériences clés - remontée
        exp_title = slide.shapes.add_textbox(Inches(7), Inches(2.8), Inches(5.5), Inches(0.4))
        exp_title_frame = exp_title.text_frame
        exp_title_frame.text = "Expériences clés récentes."
        exp_title_para = exp_title_frame.paragraphs[0]
        exp_title_para.font.size = Pt(18)
        exp_title_para.font.color.rgb = DEVOTEAM_RED
        exp_title_para.font.bold = True
        
        # Contenu des expériences clés avec mise en forme améliorée
        if dossier.experiences_cles_recentes:
            exp_box = slide.shapes.add_textbox(Inches(7), Inches(3.3), Inches(5.5), Inches(1.5))
            exp_frame = exp_box.text_frame
            exp_frame.clear()  # Effacer le contenu par défaut
            
            for i, exp in enumerate(dossier.experiences_cles_recentes):
                if i > 0:
                    # Ajouter un saut de ligne entre les expériences
                    p = exp_frame.add_paragraph()
                    p.text = ""
                
                # Titre de l'expérience en gras et souligné
                title_parts = []
                if exp.client:
                    title_parts.append(exp.client)
                if exp.intitule_poste:
                    title_parts.append(exp.intitule_poste)
                if exp.duree:
                    title_parts.append(f"({exp.duree})")
                
                if title_parts:
                    title_text = " - ".join(title_parts) + " :"
                    if i == 0:
                        # Premier paragraphe
                        exp_frame.text = title_text
                        title_para = exp_frame.paragraphs[0]
                    else:
                        # Paragraphes suivants
                        title_para = exp_frame.add_paragraph()
                        title_para.text = title_text
                    
                    title_para.font.size = Pt(11)
                    title_para.font.bold = True
                    title_para.font.underline = True
                    title_para.font.color.rgb = DARK_GRAY
                
                # Description
                if exp.description_breve:
                    desc_para = exp_frame.add_paragraph()
                    desc_para.text = exp.description_breve
                    desc_para.font.size = Pt(10)
                    desc_para.font.color.rgb = DARK_GRAY
                para.font.size = Pt(12)
                para.font.color.rgb = DARK_GRAY
    
    def _create_skills_slide(self, dossier: DossierCompetences):
        """Crée la slide des compétences"""
        slide_layout = self.prs.slide_layouts[6]  # Layout vide
        slide = self.prs.slides.add_slide(slide_layout)
        
        # Fond blanc
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(255, 255, 255)  # Blanc
        
        # Logo Devoteam avec image - positionné plus en haut et plus à gauche
        self._add_devoteam_logo(slide, Inches(0.2), Inches(0.1), Inches(0.8))
        
        # Titre de la slide
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.8), Inches(12), Inches(0.5))
        title_frame = title_box.text_frame
        title_frame.text = "Compétences techniques et fonctionnelles"
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(24)
        title_para.font.color.rgb = DEVOTEAM_RED
        title_para.font.bold = True
        
        # Compétences techniques (section gauche)
        tech_title = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(6), Inches(0.4))
        tech_title_frame = tech_title.text_frame
        tech_title_frame.text = "Compétences techniques."
        tech_title_para = tech_title_frame.paragraphs[0]
        tech_title_para.font.size = Pt(18)
        tech_title_para.font.color.rgb = DEVOTEAM_RED
        tech_title_para.font.bold = True
        
        if dossier.competences_techniques:
            comp_tech = dossier.competences_techniques
            
            skills_sections = [
                ("Language framework :", comp_tech.language_framework),
                ("CI/CD :", comp_tech.ci_cd),
                ("State management :", comp_tech.state_management),
                ("Tests :", comp_tech.tests),
                ("Outils :", comp_tech.outils),
                ("Base de données/Big data :", comp_tech.base_de_donnees_big_data),
                ("Data Analytics/Visualisation :", comp_tech.data_analytics_visualisation),
                ("Collaboration :", comp_tech.collaboration),
                ("UX/UI :", comp_tech.ux_ui)
            ]
            
            tech_box = slide.shapes.add_textbox(Inches(0.5), Inches(2), Inches(6), Inches(5))
            tech_frame = tech_box.text_frame
            tech_frame.clear()
            
            first_section = True
            for section_name, skills_list in skills_sections:
                if skills_list:
                    if not first_section:
                        # Ajouter un saut de ligne entre les sections
                        p = tech_frame.add_paragraph()
                        p.text = ""
                    
                    # Titre de la section en gras et souligné
                    if first_section:
                        tech_frame.text = section_name
                        title_para = tech_frame.paragraphs[0]
                        first_section = False
                    else:
                        title_para = tech_frame.add_paragraph()
                        title_para.text = section_name
                    
                    title_para.font.size = Pt(12)
                    title_para.font.bold = True
                    title_para.font.underline = True
                    title_para.font.color.rgb = DARK_GRAY
                    
                    # Contenu des compétences
                    content_para = tech_frame.add_paragraph()
                    content_para.text = ', '.join(skills_list)
                    content_para.font.size = Pt(11)
                    content_para.font.color.rgb = DARK_GRAY
        
        # Compétences fonctionnelles (section droite)
        func_title = slide.shapes.add_textbox(Inches(7), Inches(1.5), Inches(6), Inches(0.4))
        func_title_frame = func_title.text_frame
        func_title_frame.text = "Compétences fonctionnelles."
        func_title_para = func_title_frame.paragraphs[0]
        func_title_para.font.size = Pt(18)
        func_title_para.font.color.rgb = DEVOTEAM_RED
        func_title_para.font.bold = True
        
        if dossier.competences_fonctionnelles:
            comp_func = dossier.competences_fonctionnelles
            
            func_box = slide.shapes.add_textbox(Inches(7), Inches(2), Inches(6), Inches(5))
            func_frame = func_box.text_frame
            func_frame.clear()
            
            first_section = True
            
            # Gestion de projet
            if comp_func.gestion_de_projet:
                if first_section:
                    func_frame.text = "Gestion de projet :"
                    title_para = func_frame.paragraphs[0]
                    first_section = False
                else:
                    title_para = func_frame.add_paragraph()
                    title_para.text = "Gestion de projet :"
                
                title_para.font.size = Pt(12)
                title_para.font.bold = True
                title_para.font.underline = True
                title_para.font.color.rgb = DARK_GRAY
                
                content_para = func_frame.add_paragraph()
                content_para.text = ', '.join(comp_func.gestion_de_projet)
                content_para.font.size = Pt(11)
                content_para.font.color.rgb = DARK_GRAY
            
            # Méthodologie scrum
            if comp_func.methodologie_scrum:
                if not first_section:
                    p = func_frame.add_paragraph()
                    p.text = ""
                
                if first_section:
                    func_frame.text = "Méthodologie scrum :"
                    title_para = func_frame.paragraphs[0]
                    first_section = False
                else:
                    title_para = func_frame.add_paragraph()
                    title_para.text = "Méthodologie scrum :"
                
                title_para.font.size = Pt(12)
                title_para.font.bold = True
                title_para.font.underline = True
                title_para.font.color.rgb = DARK_GRAY
                
                content_para = func_frame.add_paragraph()
                content_para.text = ' / '.join(comp_func.methodologie_scrum)
                content_para.font.size = Pt(11)
                content_para.font.color.rgb = DARK_GRAY
            
            # Encadrement
            if comp_func.encadrement:
                if not first_section:
                    p = func_frame.add_paragraph()
                    p.text = ""
                
                if first_section:
                    func_frame.text = "Encadrement :"
                    title_para = func_frame.paragraphs[0]
                    first_section = False
                else:
                    title_para = func_frame.add_paragraph()
                    title_para.text = "Encadrement :"
                
                title_para.font.size = Pt(12)
                title_para.font.bold = True
                title_para.font.underline = True
                title_para.font.color.rgb = DARK_GRAY
                
                content_para = func_frame.add_paragraph()
                content_para.text = comp_func.encadrement
                content_para.font.size = Pt(11)
                content_para.font.color.rgb = DARK_GRAY
            
            # Compétences booléennes
            bool_skills = []
            if comp_func.revue_de_code:
                bool_skills.append("Revue de code")
            if comp_func.peer_programming:
                bool_skills.append("Peer programming")
            if comp_func.qualite_des_livrables:
                bool_skills.append("Qualité des livrables")
            
            if bool_skills:
                if not first_section:
                    p = func_frame.add_paragraph()
                    p.text = ""
                
                if first_section:
                    func_frame.text = "Autres compétences :"
                    title_para = func_frame.paragraphs[0]
                    first_section = False
                else:
                    title_para = func_frame.add_paragraph()
                    title_para.text = "Autres compétences :"
                
                title_para.font.size = Pt(12)
                title_para.font.bold = True
                title_para.font.underline = True
                title_para.font.color.rgb = DARK_GRAY
                
                content_para = func_frame.add_paragraph()
                content_para.text = ', '.join(bool_skills)
                content_para.font.size = Pt(11)
                content_para.font.color.rgb = DARK_GRAY
        
        # Section langues en bas
        if dossier.langues:
            lang_title = slide.shapes.add_textbox(Inches(0.5), Inches(6.2), Inches(12), Inches(0.3))
            lang_title_frame = lang_title.text_frame
            lang_title_frame.text = "Langues."
            lang_title_para = lang_title_frame.paragraphs[0]
            lang_title_para.font.size = Pt(16)
            lang_title_para.font.color.rgb = DEVOTEAM_RED
            lang_title_para.font.bold = True
            
            # Cercles de langues
            x_pos = 1
            for langue in dossier.langues:
                # Cercle (simulation avec forme)
                circle = slide.shapes.add_shape(
                    MSO_SHAPE.OVAL, 
                    Inches(x_pos), Inches(6.6), 
                    Inches(0.6), Inches(0.6)
                )
                circle.fill.solid()
                circle.fill.fore_color.rgb = RGBColor(255, 255, 255)
                circle.line.color.rgb = DEVOTEAM_RED
                circle.line.width = Pt(3)
                
                # Texte dans le cercle
                niveau_text = "natif" if langue.niveau and "natif" in langue.niveau.lower() else "technique"
                circle_text = circle.text_frame
                circle_text.text = niveau_text
                circle_para = circle_text.paragraphs[0]
                circle_para.font.size = Pt(10)
                circle_para.font.color.rgb = DEVOTEAM_RED
                circle_para.font.bold = True
                circle_para.alignment = PP_ALIGN.CENTER
                circle_text.vertical_anchor = MSO_ANCHOR.MIDDLE
                
                # Nom de la langue
                lang_name = slide.shapes.add_textbox(
                    Inches(x_pos - 0.1), Inches(7.3), 
                    Inches(0.8), Inches(0.2)
                )
                lang_name_frame = lang_name.text_frame
                lang_name_frame.text = langue.langue or "Langue"
                lang_name_para = lang_name_frame.paragraphs[0]
                lang_name_para.font.size = Pt(10)
                lang_name_para.font.color.rgb = DARK_GRAY
                lang_name_para.alignment = PP_ALIGN.CENTER
                
                x_pos += 1.5
    
    def _create_experience_slide(self, exp: ExperienceProfessionnelle):
        """Crée une slide pour une expérience professionnelle détaillée"""
        slide_layout = self.prs.slide_layouts[6]  # Layout vide
        slide = self.prs.slides.add_slide(slide_layout)
        
        # Fond blanc
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(255, 255, 255)  # Blanc
        
        # Logo Devoteam avec image - positionné plus en haut et plus à gauche
        self._add_devoteam_logo(slide, Inches(0.2), Inches(0.1), Inches(0.8))
        
        # Titre de la slide
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.8), Inches(12), Inches(0.5))
        title_frame = title_box.text_frame
        title_frame.text = "Expériences professionnelles récentes."
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(24)
        title_para.font.color.rgb = DEVOTEAM_RED
        title_para.font.bold = True
        
        # Logo de l'entreprise (placeholder)
        company_name = exp.client or "CLIENT"
        logo_text = company_name.upper() if len(company_name) > 6 else company_name.upper()
        company_logo = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(1.5), Inches(1))
        company_logo_frame = company_logo.text_frame
        company_logo_frame.text = logo_text
        company_logo_para = company_logo_frame.paragraphs[0]
        company_logo_para.font.size = Pt(14)
        company_logo_para.font.color.rgb = LIGHT_GRAY
        company_logo_para.font.bold = True
        company_logo_para.alignment = PP_ALIGN.CENTER
        company_logo_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        
        # Informations de l'expérience
        info_box = slide.shapes.add_textbox(Inches(2.2), Inches(1.5), Inches(10), Inches(1))
        info_frame = info_box.text_frame
        
        info_text = ""
        if exp.client:
            info_text += f"Client\n"
        if exp.intitule_poste:
            info_text += f"{exp.intitule_poste}\n"
        if exp.date_debut or exp.date_fin:
            duration = f"{exp.date_debut or ''} à {exp.date_fin or ''}".strip()
            info_text += f"{duration}"
        
        info_frame.text = info_text
        for i, para in enumerate(info_frame.paragraphs):
            if i == 0:  # "Client"
                para.font.size = Pt(16)
                para.font.color.rgb = DARK_GRAY
                para.font.bold = True
            elif i == 1:  # Poste
                para.font.size = Pt(14)
                para.font.color.rgb = DEVOTEAM_RED
                para.font.bold = True
            else:  # Durée
                para.font.size = Pt(12)
                para.font.color.rgb = LIGHT_GRAY
        
        # Contexte
        if exp.contexte:
            context_title = slide.shapes.add_textbox(Inches(0.5), Inches(2.8), Inches(12), Inches(0.3))
            context_title_frame = context_title.text_frame
            context_title_frame.text = "Contexte."
            context_title_para = context_title_frame.paragraphs[0]
            context_title_para.font.size = Pt(16)
            context_title_para.font.color.rgb = DEVOTEAM_RED
            context_title_para.font.bold = True
            
            context_box = slide.shapes.add_textbox(Inches(0.5), Inches(3.2), Inches(12), Inches(1))
            context_frame = context_box.text_frame
            context_frame.text = exp.contexte
            context_para = context_frame.paragraphs[0]
            context_para.font.size = Pt(12)
            context_para.font.color.rgb = DARK_GRAY
        
        # Responsabilités
        if exp.responsabilites:
            resp_title = slide.shapes.add_textbox(Inches(0.5), Inches(4.4), Inches(6), Inches(0.3))
            resp_title_frame = resp_title.text_frame
            resp_title_frame.text = "Responsabilités."
            resp_title_para = resp_title_frame.paragraphs[0]
            resp_title_para.font.size = Pt(16)
            resp_title_para.font.color.rgb = DEVOTEAM_RED
            resp_title_para.font.bold = True
            
            resp_content = "\n".join([f"• {resp}" for resp in exp.responsabilites])
            resp_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.8), Inches(6), Inches(2.5))
            resp_frame = resp_box.text_frame
            resp_frame.text = resp_content
            for para in resp_frame.paragraphs:
                para.font.size = Pt(11)
                para.font.color.rgb = DARK_GRAY
        
        # Livrables
        if exp.livrables:
            deliv_title = slide.shapes.add_textbox(Inches(7), Inches(4.4), Inches(6), Inches(0.3))
            deliv_title_frame = deliv_title.text_frame
            deliv_title_frame.text = "Livrables."
            deliv_title_para = deliv_title_frame.paragraphs[0]
            deliv_title_para.font.size = Pt(16)
            deliv_title_para.font.color.rgb = DEVOTEAM_RED
            deliv_title_para.font.bold = True
            
            deliv_content = "\n".join([f"• {deliv}" for deliv in exp.livrables])
            deliv_box = slide.shapes.add_textbox(Inches(7), Inches(4.8), Inches(6), Inches(2.5))
            deliv_frame = deliv_box.text_frame
            deliv_frame.text = deliv_content
            for para in deliv_frame.paragraphs:
                para.font.size = Pt(11)
                para.font.color.rgb = DARK_GRAY


def generate_devoteam_pptx(dossier: DossierCompetences) -> BytesIO:
    """
    Génère une présentation PowerPoint avec le template Devoteam
    
    Args:
        dossier: Données structurées du CV
        
    Returns:
        BytesIO contenant le fichier PPTX
    """
    try:
        generator = DevoteamPPTXGenerator()
        return generator.generate_presentation(dossier)
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération PowerPoint : {str(e)}")
        raise
