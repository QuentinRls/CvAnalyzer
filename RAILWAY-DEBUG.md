# Alternative: Simple Railway Configuration

## Option 1: Utiliser seulement le dossier backend

1. Sur Railway, dans les paramètres du projet :
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Option 2: Variables d'environnement Railway

```
OPENAI_API_KEY=sk-votre-clé-openai
PORT=8000
PYTHONPATH=/app
```

## Option 3: Si problème persiste

Supprimer le Dockerfile racine et utiliser seulement Nixpacks :

1. Delete root Dockerfile
2. Railway auto-détectera Python
3. Utilisera automatiquement requirements.txt du backend

## Structure recommandée pour Railway :

```
backend/
├── Dockerfile          # ✅ Nouveau Dockerfile optimisé
├── nixpacks.toml       # ✅ Configuration Nixpacks
├── requirements.txt    # ✅ Dependencies Python
├── app/               
│   └── main.py        # ✅ Point d'entrée FastAPI
└── ...
```

## Test en local :

```bash
cd backend
docker build -t cv2dossier-backend .
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key cv2dossier-backend
```
