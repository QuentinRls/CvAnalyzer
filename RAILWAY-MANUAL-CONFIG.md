# 🚨 SOLUTION RAILWAY - Configuration Manuelle

## Le healthcheck échoue ? Voici la solution !

### 🛠️ Configuration manuelle Railway (RECOMMANDÉE)

1. **Allez dans Railway Settings de votre projet**

2. **Dans l'onglet "Settings" → "Service Settings"** :

```
Build Command: pip install -r requirements.txt
Start Command: python main.py
Root Directory: (laisser vide)
```

3. **Dans l'onglet "Variables"** :
```
OPENAI_API_KEY=sk-proj-VOTRE-CLÉ-OPENAI-ICI
PORT=8000
PYTHONPATH=/app/backend
```

4. **Redéployez** en cliquant "Deploy"

### 🔧 Alternative - Configuration Railway avancée

Si la première méthode ne marche pas :

**Settings → Service Settings** :
```
Build Command: pip install -r requirements.txt && pip install -r backend/requirements.txt
Start Command: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
Root Directory: (vide)
```

### 🎯 Test après déploiement

Une fois redéployé, testez ces URLs :
- `https://votre-url.railway.app/` → Doit retourner info de l'API
- `https://votre-url.railway.app/health` → Doit retourner `{"status": "healthy"}`
- `https://votre-url.railway.app/docs` → Documentation FastAPI

### 🔍 Debugging - Vérifiez les logs

Dans Railway **Deployments** → **Votre déploiement** → **View Logs** :

Vous devriez voir :
```
✅ FastAPI app importée avec succès
🚀 Démarrage du serveur sur le port 8000
🔑 OpenAI configuré: True
INFO: Started server process
INFO: Uvicorn running on http://0.0.0.0:8000
```

### 🆘 Si ça ne marche toujours pas

**Option Fallback - Déploiement simple** :

1. **Supprimez railway.toml**
2. **Laissez Railway détecter automatiquement**
3. **Configuration manuelle seulement** :
   ```
   Start Command: python main.py
   Variables: OPENAI_API_KEY + PORT=8000
   ```

### 📞 Support

Si le problème persiste :
1. Partagez les **Deploy Logs** complets
2. Vérifiez que votre **clé OpenAI** fonctionne sur platform.openai.com
3. Testez en local : `python main.py`

**🎯 La configuration manuelle Railway est souvent plus fiable que les fichiers de config !**
