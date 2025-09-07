# 🚀 Railway - Déploiement Fullstack

## Configuration Nixpacks

Cette configuration utilise Nixpacks pour installer :
- **Python 3.11** avec pip et setuptools
- **Node.js 18** pour le frontend
- **Build automatique** du frontend React
- **Démarrage direct** avec `python main.py`

### 📁 Structure essentielle
```
├── main.py              # Point d'entrée principal
├── nixpacks.toml        # Configuration Nixpacks
├── railway.toml         # Configuration déploiement Railway  
├── package.json         # Config Node.js pour le frontend
├── requirements.txt     # Dépendances Python
├── backend/             # Code API FastAPI
└── frontend/            # Code React/Vite
```

### 🔧 Variables d'environnement Railway
```
OPENAI_API_KEY=sk-votre-clé-openai-ici
PORT=8000
```

### 🚀 Le build automatique
1. Installe Python 3.11 + pip + Node.js 18
2. Installe les dépendances Python (`pip install -r requirements.txt`)
3. Installe les dépendances Node.js (`npm ci`)
4. Build le frontend (`npm run build`)
5. Démarre le serveur avec `python main.py`

### 🌐 URLs après déploiement
- **Site complet**: `https://votre-app.railway.app`
- **API**: `https://votre-app.railway.app/api/v1/`
- **Docs**: `https://votre-app.railway.app/docs`
- **Health**: `https://votre-app.railway.app/health`

**✅ Configuration optimisée avec Nixpacks pour Railway !**
