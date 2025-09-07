import { z } from 'zod';

// En-tête
export const EnteteSchema = z.object({
  intitule_poste: z.string().optional().default(''),
  annees_experience: z.string().optional().default(''),
  prenom: z.string().optional().default(''),
  nom: z.string().optional().default(''),
  resume_profil: z.string().optional().default(''),
});

// Expérience clé récente
export const ExperienceCleRecenteSchema = z.object({
  client: z.string().optional().default(''),
  intitule_poste: z.string().optional().default(''),
  duree: z.string().optional().default(''),
  description_breve: z.string().optional().default(''),
});

// Diplôme
export const DiplomeSchema = z.object({
  intitule: z.string().optional().default(''),
  etablissement: z.string().optional().default(''),
  annee: z.string().optional().default(''),
});

// Certification
export const CertificationSchema = z.object({
  intitule: z.string().optional().default(''),
  organisme: z.string().optional().default(''),
  annee: z.string().optional().default(''),
});

// Langue
export const LangueSchema = z.object({
  langue: z.string().optional().default(''),
  niveau: z.string().optional().default(''),
});

// Compétences techniques
export const CompetencesTechniquesSchema = z.object({
  language_framework: z.array(z.string()).optional().default([]),
  ci_cd: z.array(z.string()).optional().default([]),
  state_management: z.array(z.string()).optional().default([]),
  tests: z.array(z.string()).optional().default([]),
  outils: z.array(z.string()).optional().default([]),
  base_de_donnees_big_data: z.array(z.string()).optional().default([]),
  data_analytics_visualisation: z.array(z.string()).optional().default([]),
  collaboration: z.array(z.string()).optional().default([]),
  ux_ui: z.array(z.string()).optional().default([]),
});

// Compétences fonctionnelles
export const CompetencesFonctionnellesSchema = z.object({
  gestion_de_projet: z.array(z.string()).optional().default([]),
  revue_de_code: z.boolean().optional().default(false),
  peer_programming: z.boolean().optional().default(false),
  qualite_des_livrables: z.boolean().optional().default(false),
  methodologie_scrum: z.array(z.string()).optional().default([]),
  encadrement: z.string().optional().default(''),
});

// Expérience professionnelle
export const ExperienceProfessionnelleSchema = z.object({
  client: z.string().optional().default(''),
  intitule_poste: z.string().optional().default(''),
  date_debut: z.string().optional().default(''),
  date_fin: z.string().optional().default(''),
  contexte: z.string().optional().default(''),
  responsabilites: z.array(z.string()).optional().default([]),
  livrables: z.array(z.string()).optional().default([]),
  environnement_technique: z.array(z.string()).optional().default([]),
});

// Schéma principal
export const DossierCompetencesSchema = z.object({
  entete: EnteteSchema.optional(),
  experiences_cles_recentes: z.array(ExperienceCleRecenteSchema).optional().default([]),
  diplomes: z.array(DiplomeSchema).optional().default([]),
  certifications: z.array(CertificationSchema).optional().default([]),
  langues: z.array(LangueSchema).optional().default([]),
  competences_techniques: CompetencesTechniquesSchema.optional(),
  competences_fonctionnelles: CompetencesFonctionnellesSchema.optional(),
  experiences_professionnelles: z.array(ExperienceProfessionnelleSchema).optional().default([]),
});

// Request schema
export const CVTextRequestSchema = z.object({
  cv_text: z.string(),
});

// Export des types
export type Entete = z.infer<typeof EnteteSchema>;
export type ExperienceCleRecente = z.infer<typeof ExperienceCleRecenteSchema>;
export type Diplome = z.infer<typeof DiplomeSchema>;
export type Certification = z.infer<typeof CertificationSchema>;
export type Langue = z.infer<typeof LangueSchema>;
export type CompetencesTechniques = z.infer<typeof CompetencesTechniquesSchema>;
export type CompetencesFonctionnelles = z.infer<typeof CompetencesFonctionnellesSchema>;
export type ExperienceProfessionnelle = z.infer<typeof ExperienceProfessionnelleSchema>;
export type DossierCompetences = z.infer<typeof DossierCompetencesSchema>;
export type CVTextRequest = z.infer<typeof CVTextRequestSchema>;
