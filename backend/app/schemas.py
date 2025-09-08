from pydantic import BaseModel, Field
from typing import List, Optional, Union


# En-tête
class Entete(BaseModel):
    intitule_poste: str = ""
    annees_experience: str = ""
    prenom: str = ""
    nom: str = ""
    resume_profil: str = ""


# Expériences clés récentes
class ExperienceCleRecente(BaseModel):
    client: str = ""
    intitule_poste: str = ""
    duree: str = ""
    description_breve: str = ""


# Diplômes
class Diplome(BaseModel):
    intitule: str = ""
    etablissement: str = ""
    annee: str = ""


# Certifications
class Certification(BaseModel):
    intitule: str = ""
    organisme: str = ""
    annee: str = ""


# Langues
class Langue(BaseModel):
    langue: str = ""
    niveau: str = ""


# Compétences techniques
class CompetencesTechniques(BaseModel):
    language_framework: List[str] = []
    ci_cd: List[str] = []
    state_management: List[str] = []
    tests: List[str] = []
    outils: List[str] = []
    base_de_donnees_big_data: List[str] = []
    data_analytics_visualisation: List[str] = []
    collaboration: List[str] = []
    ux_ui: List[str] = []


# Compétences fonctionnelles
class CompetencesFonctionnelles(BaseModel):
    gestion_de_projet: List[str] = []
    revue_de_code: bool = False
    peer_programming: bool = False
    qualite_des_livrables: bool = False
    methodologie_scrum: List[str] = []
    encadrement: str = ""


# Expérience professionnelle détaillée
class ExperienceProfessionnelle(BaseModel):
    client: str = ""
    intitule_poste: str = ""
    date_debut: str = ""
    date_fin: str = ""
    contexte: str = ""
    responsabilites: List[str] = []
    livrables: List[str] = []
    environnement_technique: CompetencesTechniques = Field(default_factory=CompetencesTechniques)


# Modèle principal
class DossierCompetences(BaseModel):
    entete: Entete
    experiences_cles_recentes: List[ExperienceCleRecente] = []
    diplomes: List[Diplome] = []
    certifications: List[Certification] = []
    langues: List[Langue] = []
    competences_techniques: CompetencesTechniques
    competences_fonctionnelles: CompetencesFonctionnelles
    experiences_professionnelles: List[ExperienceProfessionnelle] = []


# Input/Output schemas for API
class CVTextRequest(BaseModel):
    cv_text: str = Field(..., min_length=50, description="Raw text from CV")


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
