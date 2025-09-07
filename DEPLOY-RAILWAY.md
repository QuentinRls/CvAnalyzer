# 🚀 Railway - Déploiement Fullstack

## Configuration Railway pour Backend + Frontend

### 📁 Structure essentielle
```
├── main.py              # Point d'entrée principal
├── package.json         # Config Node.js pour le frontend
├── nixpacks.toml        # Config build Railway
├── railway.toml         # Config déploiement Railway
├── requirements.txt     # Dépendances Python
├── backend/             # Code API FastAPI
└── frontend/            # Code React/Vite
```

### 🔧 Variables d'environnement Railway
```
OPENAI_API_KEY=sk-votre-clé-openai-ici
PORT=8000
```

### 🌐 URLs après déploiement
- **Site complet**: `https://votre-app.railway.app`
- **API**: `https://votre-app.railway.app/api/v1/`
- **Docs**: `https://votre-app.railway.app/docs`
- **Health**: `https://votre-app.railway.app/health`

### 🚀 Le build automatique
1. Installe Node.js et Python
2. Build le frontend (`npm run build`)
3. Installe les dépendances Python
4. Démarre le serveur avec `python main.py`

**✅ Configuration optimisée pour déploiement fullstack sur Railway !**
