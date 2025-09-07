# CV2Dossier - Analyseur de CV Intelligent

## Description
Application web d'analyse automatique de CV utilisant l'intelligence artificielle pour extraire et structurer les données professionnelles avec le branding Devoteam.

## Architecture
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + Python + OpenAI API
- **Base de données**: Stockage local (extensions possibles)

## Fonctionnalités
- ✅ Upload de CV (PDF, DOCX)
- ✅ Analyse IA avec OpenAI
- ✅ Extraction structurée des données
- ✅ Interface moderne avec branding Devoteam
- ✅ Animations et UX optimisée
- ✅ Export et copie des données

## Installation locale

### Prérequis
- Node.js 18+
- Python 3.8+
- Clé API OpenAI

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Configuration
# Créer un fichier .env avec :
# OPENAI_API_KEY=your_openai_api_key_here

# Démarrage
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Déploiement

### Variables d'environnement requises
- `OPENAI_API_KEY`: Clé API OpenAI pour l'analyse IA
- `VITE_API_URL`: URL de l'API backend (pour le frontend)

### Backend (Railway/Render)
1. Connecter le repository
2. Configurer les variables d'environnement
3. Définir le port 8000
4. Commande de démarrage: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel/Netlify)
1. Connecter le repository
2. Dossier de build: `frontend`
3. Commande de build: `npm run build`
4. Dossier de sortie: `dist`
5. Variables d'environnement: `VITE_API_URL`

## Technologies utilisées
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- React Router (navigation)
- Sonner (notifications)
- FastAPI (API backend)
- Pydantic (validation)
- OpenAI API (IA)
- PDFPlumber (extraction PDF)

## Branding
Interface conçue avec l'identité visuelle Devoteam :
- Couleur principale: #F8485D
- Logo Devoteam intégré
- Design moderne et professionnel

## Contribution
Ce projet utilise les meilleures pratiques de développement moderne avec TypeScript, validation de schémas, et architecture modulaire.
