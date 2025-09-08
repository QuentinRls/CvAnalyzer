import os
import json
from typing import Optional, Union, BinaryIO
from pathlib import Path
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from ..schemas import DossierCompetences
from ..utils import logger, LLMExtractionError
from .ingest import read_cv


# System prompt pour l'extraction selon le nouveau format
SYSTEM_PROMPT = """Tu es un extracteur d'information RH expert.
Entrée : texte brut d'un CV francophone ou anglophone.
Sortie : un JSON **valide** qui respecte EXACTEMENT le schéma fourni.

Tu vas fournir toutes les informations pour remplir un dossier de compétences complet.
Réponds uniquement dans le format JSON donné, sans texte hors-JSON, en remplaçant chaque placeholder par tes données réelles (pas d'exemples ni de valeurs fictives).

INSTRUCTIONS SPÉCIALES POUR LES EXPÉRIENCES PROFESSIONNELLES :
- Extraire un niveau de détail élevé pour chaque expérience
- Le CONTEXTE doit être substantiel (3-5 phrases) expliquant : le projet, l'entreprise, les enjeux, les objectifs
- Les RESPONSABILITÉS doivent être détaillées et techniques, avec des verbes d'action précis
- Les LIVRABLES doivent être concrets et mesurables (applications, documents, métriques)
- L'ENVIRONNEMENT TECHNIQUE doit être organisé selon les 9 catégories de compétences techniques (language_framework, ci_cd, state_management, tests, outils, base_de_donnees_big_data, data_analytics_visualisation, collaboration, ux_ui) pour chaque expérience
- Prioriser les expériences les plus récentes et les plus significatives
- Reformuler les informations pour qu'elles soient professionnelles et percutantes

QUALITÉ ATTENDUE POUR LE CONTEXTE :
- Mentionner le secteur d'activité de l'entreprise/client
- Expliquer l'objectif du projet ou de la mission
- Préciser la taille de l'équipe si mentionnée
- Indiquer les contraintes ou défis particuliers
- Contextualiser l'importance du projet pour l'entreprise

QUALITÉ ATTENDUE POUR LES RESPONSABILITÉS :
- Utiliser des verbes d'action forts (concevoir, développer, implémenter, optimiser, etc.)
- Être spécifique sur les technologies et méthodes utilisées
- Quantifier quand possible (nombre d'utilisateurs, performance, etc.)
- Montrer l'autonomie et le niveau de responsabilité
- Indiquer les interactions avec d'autres équipes

QUALITÉ ATTENDUE POUR LES LIVRABLES :
- Applications déployées avec leur portée
- Documentation technique rédigée
- Améliorations de performance chiffrées
- Formations données ou processus mis en place
- Tout résultat concret et mesurable

Contraintes techniques :
- Dates au format YYYY-MM (ou YYYY si mois inconnu).
- Listes sous forme de tableaux JSON ([]).
- Conserve les intitulés de sections exactement tels que définis.
- Ne pas inventer de données. Si une information manque, laisser vide ou omettre.
- Pour les années d'expérience : calculer à partir des périodes, en nombre entier.
- Pour les compétences techniques : utiliser uniquement les 9 catégories prévues.
- Pour les compétences fonctionnelles : les booléens pour revue_de_code, peer_programming, qualite_des_livrables.
- Pour les expériences : extraire exactement 5 expériences clés récentes (les plus pertinentes et récentes), puis les expériences professionnelles détaillées.

Categories de compétences techniques obligatoires :
- language_framework
- ci_cd  
- state_management
- tests
- outils
- base_de_donnees_big_data
- data_analytics_visualisation
- collaboration
- ux_ui"""


# JSON Schema pour OpenAI function calling
EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "entete": {
            "type": "object",
            "properties": {
                "intitule_poste": {"type": "string"},
                "annees_experience": {"type": "string"},
                "prenom": {"type": "string"},
                "nom": {"type": "string"},
                "resume_profil": {"type": "string"}
            }
        },
        "experiences_cles_recentes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "client": {"type": "string"},
                    "intitule_poste": {"type": "string"},
                    "duree": {"type": "string"},
                    "description_breve": {"type": "string"}
                }
            }
        },
        "diplomes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "intitule": {"type": "string"},
                    "etablissement": {"type": "string"},
                    "annee": {"type": "string"}
                }
            }
        },
        "certifications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "intitule": {"type": "string"},
                    "organisme": {"type": "string"},
                    "annee": {"type": "string"}
                }
            }
        },
        "langues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "langue": {"type": "string"},
                    "niveau": {"type": "string"}
                }
            }
        },
        "competences_techniques": {
            "type": "object",
            "properties": {
                "language_framework": {"type": "array", "items": {"type": "string"}},
                "ci_cd": {"type": "array", "items": {"type": "string"}},
                "state_management": {"type": "array", "items": {"type": "string"}},
                "tests": {"type": "array", "items": {"type": "string"}},
                "outils": {"type": "array", "items": {"type": "string"}},
                "base_de_donnees_big_data": {"type": "array", "items": {"type": "string"}},
                "data_analytics_visualisation": {"type": "array", "items": {"type": "string"}},
                "collaboration": {"type": "array", "items": {"type": "string"}},
                "ux_ui": {"type": "array", "items": {"type": "string"}}
            }
        },
        "competences_fonctionnelles": {
            "type": "object",
            "properties": {
                "gestion_de_projet": {"type": "array", "items": {"type": "string"}},
                "revue_de_code": {"type": "boolean"},
                "peer_programming": {"type": "boolean"},
                "qualite_des_livrables": {"type": "boolean"},
                "methodologie_scrum": {"type": "array", "items": {"type": "string"}},
                "encadrement": {"type": "string"}
            }
        },
        "experiences_professionnelles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "client": {"type": "string"},
                    "intitule_poste": {"type": "string"},
                    "date_debut": {"type": "string"},
                    "date_fin": {"type": "string"},
                    "contexte": {"type": "string"},
                    "responsabilites": {"type": "array", "items": {"type": "string"}},
                    "livrables": {"type": "array", "items": {"type": "string"}},
                    "environnement_technique": {
                        "type": "object",
                        "properties": {
                            "language_framework": {"type": "array", "items": {"type": "string"}},
                            "ci_cd": {"type": "array", "items": {"type": "string"}},
                            "state_management": {"type": "array", "items": {"type": "string"}},
                            "tests": {"type": "array", "items": {"type": "string"}},
                            "outils": {"type": "array", "items": {"type": "string"}},
                            "base_de_donnees_big_data": {"type": "array", "items": {"type": "string"}},
                            "data_analytics_visualisation": {"type": "array", "items": {"type": "string"}},
                            "collaboration": {"type": "array", "items": {"type": "string"}},
                            "ux_ui": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            }
        }
    },
    "required": [
        "entete", "experiences_cles_recentes", "diplomes", "certifications", 
        "langues", "competences_techniques", "competences_fonctionnelles", 
        "experiences_professionnelles"
    ]
}


def get_openai_client():
    """Get OpenAI client, raising error if API key not configured"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable must be set")
    return OpenAI(api_key=api_key)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
def call_openai_extraction(cv_text: str) -> dict:
    """Call OpenAI API to extract structured data from CV text."""
    logger.info("Calling OpenAI API for CV extraction")
    
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"""Voici le CV à analyser pour créer un dossier de compétences professionnel :

{cv_text}

CONSIGNES SPÉCIFIQUES :
1. Pour chaque expérience professionnelle, extrait le maximum de détails disponibles
2. Reformule le contexte pour qu'il soit riche et informatif (projet, enjeux, secteur)
3. Détaille les responsabilités avec des verbes d'action forts et des spécificités techniques
4. Liste tous les livrables concrets mentionnés ou implicites
5. Recense exhaustivement l'environnement technique pour chaque expérience
6. Priorise la qualité et la pertinence des informations extraites
7. IMPORTANT : Extrais exactement 5 expériences professionnelles clés récentes, même si certaines sont plus courtes ou moins détaillées que d'autres
8. ENVIRONNEMENT TECHNIQUE : Structure l'environnement technique de chaque expérience selon les 9 catégories (language_framework, ci_cd, state_management, tests, outils, base_de_donnees_big_data, data_analytics_visualisation, collaboration, ux_ui)"""}
            ],
            functions=[{
                "name": "extract_cv_data",
                "description": "Extraire les données structurées du CV",
                "parameters": EXTRACTION_SCHEMA
            }],
            function_call={"name": "extract_cv_data"},
        )
        
        function_call = response.choices[0].message.function_call
        if not function_call or function_call.name != "extract_cv_data":
            raise LLMExtractionError("No function call returned by OpenAI")
            
        extracted_data = json.loads(function_call.arguments)
        logger.info("Successfully extracted structured data from CV")
        return extracted_data
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error from OpenAI response: {e}")
        raise LLMExtractionError(f"Invalid JSON response from OpenAI: {e}")
        
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        raise LLMExtractionError(f"OpenAI extraction failed: {e}")


def extract_structured(cv_text: str = None, cv_file: Union[str, Path, BinaryIO] = None) -> DossierCompetences:
    """
    Extract structured data from CV text or file.
    
    Args:
        cv_text: Raw text content of CV
        cv_file: CV file (path or file-like object)
        
    Returns:
        DossierCompetences: Structured CV data
        
    Raises:
        LLMExtractionError: If extraction fails
    """
    try:
        # Get CV text
        if cv_text:
            text_content = cv_text
        elif cv_file:
            text_content = read_cv(cv_file)
        else:
            raise ValueError("Either cv_text or cv_file must be provided")
            
        if not text_content or len(text_content.strip()) < 50:
            raise LLMExtractionError("CV text too short or empty")
            
        logger.info(f"Extracting structured data from CV text ({len(text_content)} chars)")
        
        # Call OpenAI for extraction
        extracted_dict = call_openai_extraction(text_content)
        
        # Validate and create Pydantic model
        try:
            extracted = DossierCompetences(**extracted_dict)
            logger.info("Successfully validated extracted data with Pydantic")
            return extracted
            
        except Exception as e:
            logger.error(f"Pydantic validation failed: {e}")
            logger.debug(f"Raw extracted data: {json.dumps(extracted_dict, indent=2)}")
            raise LLMExtractionError(f"Data validation failed: {e}")
            
    except LLMExtractionError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during extraction: {e}")
        raise LLMExtractionError(f"Extraction failed: {e}")


def extract_from_file(file_path: Union[str, Path]) -> DossierCompetences:
    """Extract structured data from CV file."""
    return extract_structured(cv_file=file_path)


def extract_from_text(cv_text: str) -> DossierCompetences:
    """Extract structured data from CV text."""
    return extract_structured(cv_text=cv_text)
