"""
Générateur de contenu HTML formaté pour Google Docs - Template Devoteam
"""
from typing import List
import logging

from ..schemas import DossierCompetences, ExperienceProfessionnelle

logger = logging.getLogger(__name__)


def generate_google_docs_html(dossier: DossierCompetences) -> str:
    """
    Génère un contenu HTML formaté pour Google Docs avec le style Devoteam
    
    Args:
        dossier: Données structurées du CV
        
    Returns:
        Contenu HTML formaté
    """
    try:
        html_parts = []
        
        # En-tête HTML avec styles Devoteam
        html_parts.append("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Dossier de Compétences</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.3;
            margin: 40px;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .devoteam-logo {
            color: #F8485D;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 30px;
        }
        
        .main-title {
            color: #F8485D;
            font-size: 32px;
            font-weight: bold;
            margin: 30px 0 5px 0;
            line-height: 1.1;
        }
        
        .subtitle {
            color: #F8485D;
            font-size: 16px;
            margin: 0 0 30px 0;
            font-weight: normal;
        }
        
        .name {
            color: #F8485D;
            font-size: 20px;
            font-weight: bold;
            margin: 30px 0 40px 0;
        }
        
        .section-title {
            color: #F8485D;
            font-size: 18px;
            font-weight: bold;
            margin: 30px 0 15px 0;
        }
        
        .section-content {
            background-color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        
        .experience-item {
            margin-bottom: 20px;
        }
        
        .experience-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        
        .experience-subtitle {
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
        }
        
        .experience-description {
            color: #555;
            line-height: 1.4;
        }
        
        .skills-category {
            margin-bottom: 15px;
        }
        
        .skills-category-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        
        .skills-list {
            color: #555;
            margin-left: 0;
        }
        
        .certification-item {
            margin-bottom: 8px;
            color: #555;
        }
        
        .language-item {
            display: inline-block;
            margin-right: 30px;
            margin-bottom: 10px;
            text-align: center;
        }
        
        .language-circle {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            border: 3px solid #F8485D;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 5px;
            font-size: 12px;
            color: #F8485D;
            font-weight: bold;
        }
        
        .language-name {
            text-align: center;
            font-size: 14px;
            color: #333;
        }
        
        .professional-summary {
            background-color: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            font-style: italic;
            color: #666;
        }
        
        .page-break {
            page-break-before: always;
        }
        
        .experience-detail {
            background-color: white;
            padding: 25px;
            margin-bottom: 25px;
            border-radius: 5px;
        }
        
        .experience-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .company-logo {
            width: 80px;
            height: 80px;
            margin-right: 20px;
            background-color: #f0f0f0;
            border-radius: 5px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #666;
        }
        
        .experience-info h3 {
            margin: 0;
            color: #333;
            font-size: 18px;
        }
        
        .experience-info .position {
            color: #F8485D;
            font-weight: bold;
            margin: 5px 0;
        }
        
        .experience-info .duration {
            color: #666;
            font-size: 14px;
        }
        
        .context-section, .responsibilities-section, .deliverables-section, .tech-env-section {
            margin-bottom: 20px;
        }
        
        .context-section h4, .responsibilities-section h4, .deliverables-section h4, .tech-env-section h4 {
            color: #F8485D;
            font-size: 16px;
            margin-bottom: 10px;
        }
        
        ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        
        li {
            margin-bottom: 5px;
            color: #555;
        }
        
        .two-column {
            display: flex;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .column {
            flex: 1;
        }
    </style>
</head>
<body>""")
        
        # Logo Devoteam
        html_parts.append('<div class="devoteam-logo">🟢 devoteam</div>')
        
        # Titre principal et sous-titre
        if dossier.entete:
            if dossier.entete.intitule_poste:
                html_parts.append(f'<div class="main-title">{dossier.entete.intitule_poste}</div>')
            
            if dossier.entete.annees_experience:
                html_parts.append(f'<div class="subtitle">{dossier.entete.annees_experience}</div>')
            
            # Nom
            nom_complet = f"{dossier.entete.prenom or ''} {dossier.entete.nom or ''}".strip()
            if nom_complet:
                html_parts.append(f'<div class="name">{nom_complet}</div>')
        
        # Résumé professionnel si disponible
        if dossier.resume_profil:
            html_parts.append(f'<div class="professional-summary">{dossier.resume_profil}</div>')
        
        # Section 1: Diplômes + Expériences clés (côte à côte)
        html_parts.append('<div class="two-column">')
        
        # Diplômes (colonne gauche)
        html_parts.append('<div class="column">')
        html_parts.append('<div class="section-title">Diplômes.</div>')
        html_parts.append('<div class="section-content">')
        
        if dossier.diplomes:
            for diplome in dossier.diplomes:
                html_parts.append('<div class="certification-item">')
                if diplome.niveau and diplome.intitule:
                    html_parts.append(f'🎓 <strong>{diplome.niveau}</strong><br>')
                    html_parts.append(f'{diplome.intitule}<br>')
                if diplome.etablissement:
                    html_parts.append(f'{diplome.etablissement}<br>')
                if diplome.annee:
                    html_parts.append(f'{diplome.annee}')
                html_parts.append('</div><br>')
        
        html_parts.append('</div></div>')  # Fin diplômes
        
        # Expériences clés (colonne droite)
        html_parts.append('<div class="column">')
        html_parts.append('<div class="section-title">Expériences clés récentes.</div>')
        html_parts.append('<div class="section-content">')
        
        if dossier.experiences_cles:
            for exp in dossier.experiences_cles:
                html_parts.append('<div class="experience-item">')
                
                title_parts = []
                if exp.client:
                    title_parts.append(f'<strong>{exp.client}</strong>')
                if exp.intitule_poste:
                    title_parts.append(exp.intitule_poste)
                if exp.duree:
                    title_parts.append(f'<em>{exp.duree}</em>')
                
                if title_parts:
                    html_parts.append(f'<div class="experience-title">{", ".join(title_parts)}</div>')
                
                if exp.description_breve:
                    html_parts.append(f'<div class="experience-description">{exp.description_breve}</div>')
                
                html_parts.append('</div>')
        
        html_parts.append('</div></div>')  # Fin expériences clés
        html_parts.append('</div>')  # Fin section côte à côte
        
        # Certifications
        html_parts.append('<div class="section-title">Certifications.</div>')
        html_parts.append('<div class="section-content">')
        
        if dossier.certifications:
            for cert in dossier.certifications:
                html_parts.append('<div class="certification-item">')
                if cert.nom:
                    html_parts.append(f'<strong>{cert.nom}</strong>')
                if cert.organisme:
                    html_parts.append(f' - {cert.organisme}')
                if cert.annee:
                    html_parts.append(f' ({cert.annee})')
                html_parts.append('</div>')
        else:
            html_parts.append('<div class="certification-item">XXX<br>xxx</div>')
        
        html_parts.append('</div>')
        
        # Langues avec cercles
        html_parts.append('<div class="section-title">Langues.</div>')
        html_parts.append('<div class="section-content">')
        
        if dossier.langues:
            for langue in dossier.langues:
                html_parts.append('<div class="language-item">')
                
                # Niveau dans le cercle
                niveau_short = "natif" if langue.niveau and "natif" in langue.niveau.lower() else "technique"
                html_parts.append(f'<div class="language-circle">{niveau_short}</div>')
                html_parts.append(f'<div class="language-name">{langue.langue or "Langue"}</div>')
                
                html_parts.append('</div>')
        else:
            # Langues par défaut comme dans l'image
            html_parts.append('<div class="language-item">')
            html_parts.append('<div class="language-circle">natif</div>')
            html_parts.append('<div class="language-name">Français</div>')
            html_parts.append('</div>')
            
            html_parts.append('<div class="language-item">')
            html_parts.append('<div class="language-circle">technique</div>')
            html_parts.append('<div class="language-name">Anglais</div>')
            html_parts.append('</div>')
        
        html_parts.append('</div>')
        
        # Nouvelle page pour les compétences
        html_parts.append('<div class="page-break"></div>')
        html_parts.append('<div class="devoteam-logo">🟢 devoteam</div>')
        
        # Répéter titre et nom sur page 2
        if dossier.entete:
            if dossier.entete.intitule_poste:
                html_parts.append(f'<div class="main-title">{dossier.entete.intitule_poste}</div>')
            if dossier.entete.annees_experience:
                html_parts.append(f'<div class="subtitle">{dossier.entete.annees_experience}</div>')
            nom_complet = f"{dossier.entete.prenom or ''} {dossier.entete.nom or ''}".strip()
            if nom_complet:
                html_parts.append(f'<div class="name">{nom_complet}</div>')
        
        # Compétences techniques
        html_parts.append('<div class="section-title">Compétences techniques.</div>')
        html_parts.append('<div class="section-content">')
        
        if dossier.competences_techniques:
            comp_tech = dossier.competences_techniques
            
            # Toutes les catégories de compétences
            skills_sections = [
                ("Language framework", comp_tech.language_framework),
                ("Intégration continue CI/CD", comp_tech.ci_cd),
                ("State management", comp_tech.state_management),
                ("Tests", comp_tech.tests),
                ("Outils", comp_tech.outils),
                ("Base de données/Big data", comp_tech.base_de_donnees_big_data),
                ("Data Analytics/Visualisation", comp_tech.data_analytics_visualisation),
                ("Collaboration", comp_tech.collaboration),
                ("UX/UI", comp_tech.ux_ui)
            ]
            
            for section_name, skills_list in skills_sections:
                if skills_list:
                    html_parts.append(f'<div class="skills-category">')
                    html_parts.append(f'<div class="skills-category-title">{section_name}</div>')
                    html_parts.append(f'<div class="skills-list">{", ".join(skills_list)}</div>')
                    html_parts.append('</div>')
        
        html_parts.append('</div>')
        
        # Compétences fonctionnelles
        html_parts.append('<div class="section-title">Compétences fonctionnelles.</div>')
        html_parts.append('<div class="section-content">')
        
        if dossier.competences_fonctionnelles:
            comp_func = dossier.competences_fonctionnelles
            
            if comp_func.gestion_de_projet:
                html_parts.append('<div class="skills-category">')
                html_parts.append('<div class="skills-category-title">Gestion de projet</div>')
                html_parts.append(f'<div class="skills-list">{", ".join(comp_func.gestion_de_projet)}</div>')
                html_parts.append('</div>')
            
            if comp_func.methodologie_scrum:
                html_parts.append('<div class="skills-category">')
                html_parts.append('<div class="skills-category-title">Méthodologie scrum</div>')
                methodologies = []
                for method in comp_func.methodologie_scrum:
                    if method.lower() in ["storymapping", "sprint planning", "sprint reviews", "demo"]:
                        methodologies.append(method)
                if methodologies:
                    html_parts.append(f'<div class="skills-list">{" / ".join(methodologies)}</div>')
                html_parts.append('</div>')
            
            if comp_func.encadrement:
                html_parts.append('<div class="skills-category">')
                html_parts.append('<div class="skills-category-title">Encadrement</div>')
                html_parts.append(f'<div class="skills-list">{comp_func.encadrement}</div>')
                html_parts.append('</div>')
        
        html_parts.append('</div>')
        
        # Nouvelle page pour les expériences détaillées
        if dossier.experiences_professionnelles:
            html_parts.append('<div class="page-break"></div>')
            html_parts.append('<div class="devoteam-logo">🟢 devoteam</div>')
            html_parts.append('<div class="section-title">Expériences professionnelles récentes.</div>')
            
            for exp in dossier.experiences_professionnelles:
                html_parts.append('<div class="experience-detail">')
                
                # En-tête avec logo
                html_parts.append('<div class="experience-header">')
                
                # Logo de l'entreprise (placeholder)
                company_name = exp.client or "CLIENT"
                logo_text = company_name.upper() if len(company_name) > 6 else company_name.upper()
                html_parts.append(f'<div class="company-logo">{logo_text}</div>')
                
                # Informations de l'expérience
                html_parts.append('<div class="experience-info">')
                if exp.client:
                    html_parts.append(f'<h3>Client</h3>')
                if exp.intitule_poste:
                    html_parts.append(f'<div class="position">{exp.intitule_poste}</div>')
                if exp.duree:
                    html_parts.append(f'<div class="duration">{exp.duree}</div>')
                html_parts.append('</div>')
                
                html_parts.append('</div>')  # Fin header
                
                # Contexte
                if exp.contexte:
                    html_parts.append('<div class="context-section">')
                    html_parts.append('<h4>Contexte.</h4>')
                    html_parts.append(f'<p>{exp.contexte}</p>')
                    html_parts.append('</div>')
                
                # Responsabilités
                if exp.responsabilites:
                    html_parts.append('<div class="responsibilities-section">')
                    html_parts.append('<h4>Responsabilités.</h4>')
                    html_parts.append('<ul>')
                    for resp in exp.responsabilites:
                        html_parts.append(f'<li>{resp}</li>')
                    html_parts.append('</ul>')
                    html_parts.append('</div>')
                
                # Livrables
                if exp.livrables:
                    html_parts.append('<div class="deliverables-section">')
                    html_parts.append('<h4>Livrables.</h4>')
                    html_parts.append('<ul>')
                    for livrable in exp.livrables:
                        html_parts.append(f'<li>{livrable}</li>')
                    html_parts.append('</ul>')
                    html_parts.append('</div>')
                
                # Environnement technique
                if exp.environnement_technique:
                    html_parts.append('<div class="tech-env-section">')
                    html_parts.append('<h4>Environnement technique.</h4>')
                    html_parts.append('<ul>')
                    for tech in exp.environnement_technique:
                        html_parts.append(f'<li>{tech}</li>')
                    html_parts.append('</ul>')
                    html_parts.append('</div>')
                
                html_parts.append('</div>')  # Fin experience-detail
        
        # Fermeture HTML
        html_parts.append('</body></html>')
        
        # Joindre toutes les parties
        html_content = ''.join(html_parts)
        
        logger.info("HTML généré avec succès pour Google Docs")
        return html_content
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du HTML : {str(e)}")
        raise
