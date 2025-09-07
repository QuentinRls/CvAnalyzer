# 🚀 Guide de Déploiement CV2Dossier

## Vue d'ensemble
Ce guide vous accompagne pour déployer votre application CV2Dossier en ligne avec un backend Railway et un frontend Vercel.

## Architecture de déploiement
```
Frontend (Vercel) → Backend (Railway) → OpenAI API
```

## 📋 Prérequis

### Comptes nécessaires
- [ ] Compte GitHub
- [ ] Compte Vercel (connecté à GitHub)
- [ ] Compte Railway (connecté à GitHub)
- [ ] Clé API OpenAI (https://platform.openai.com/api-keys)

### Outils locaux
- [ ] Git installé
- [ ] Node.js 18+ installé
- [ ] Éditeur de code (VS Code recommandé)

## 🎯 Étape 1: Préparation du repository GitHub

### 1.1 Créer le repository
1. Aller sur https://github.com/new
2. **Nom**: `cv2dossier` (ou votre choix)
3. **Description**: `Analyseur de CV intelligent avec IA - Branding Devoteam`
4. **Visibilité**: Public ou Privé
5. **Important**: NE PAS cocher "Add a README file", "Add .gitignore", ou "Choose a license"
6. Cliquer "Create repository"

### 1.2 Connecter le projet local
```bash
# Dans votre dossier de projet
git init
git add .
git commit -m "Initial commit: CV2Dossier with Devoteam branding"
git branch -M main
git remote add origin https://github.com/VOTRE_USERNAME/cv2dossier.git
git push -u origin main
```

## 🖥️ Étape 2: Déploiement du Backend (Railway)

### 2.1 Créer le projet Railway
1. Aller sur https://railway.app
2. Se connecter avec GitHub
3. Cliquer "New Project"
4. Sélectionner "Deploy from GitHub repo"
5. Choisir votre repository `cv2dossier`
6. Railway détectera automatiquement Python

### 2.2 Configuration des variables d'environnement
1. Dans le dashboard Railway, aller dans l'onglet "Variables"
2. Ajouter les variables suivantes:
   ```
   OPENAI_API_KEY=sk-votre-clé-openai-ici
   PORT=8000
   ENVIRONMENT=production
   ```

### 2.3 Configuration du déploiement
1. Railway devrait détecter automatiquement votre `railway.toml`
2. Le build se lance automatiquement
3. Votre backend sera accessible à une URL comme: `https://cv2dossier-production.up.railway.app`

### 2.4 Vérification
- URL de test: `https://votre-url-railway.up.railway.app/health`
- Devrait retourner: `{"status": "healthy", "version": "0.1.0", "openai_configured": true}`

## 🌐 Étape 3: Déploiement du Frontend (Vercel)

### 3.1 Créer le projet Vercel
1. Aller sur https://vercel.com
2. Se connecter avec GitHub
3. Cliquer "New Project"
4. Sélectionner "Import Git Repository"
5. Choisir votre repository `cv2dossier`

### 3.2 Configuration du projet
```
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

### 3.3 Variables d'environnement
Dans les paramètres Vercel, ajouter:
```
VITE_API_URL=https://votre-url-railway.up.railway.app
```

### 3.4 Déploiement
1. Cliquer "Deploy"
2. Attendre la fin du build (environ 2-5 minutes)
3. Votre application sera accessible à: `https://votre-app.vercel.app`

## 🔧 Étape 4: Configuration finale

### 4.1 CORS (si nécessaire)
Si vous avez des erreurs CORS, modifier `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://votre-app.vercel.app"],  # Remplacer par votre URL Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4.2 Test de l'application complète
1. Aller sur votre URL Vercel
2. Tester l'upload d'un CV
3. Vérifier que l'analyse fonctionne

## 🚨 Dépannage

### Problèmes fréquents

#### Backend ne démarre pas
- Vérifier la variable `OPENAI_API_KEY`
- Vérifier les logs Railway
- S'assurer que `requirements.txt` est correct

#### Frontend ne se connecte pas au backend
- Vérifier la variable `VITE_API_URL`
- Tester l'endpoint `/health` du backend
- Vérifier la configuration CORS

#### Erreurs OpenAI
- Vérifier que la clé API est valide
- Vérifier le quota de votre compte OpenAI
- Vérifier les logs dans Railway

### URLs importantes
- **Backend Health**: `https://votre-backend.railway.app/health`
- **Backend Docs**: `https://votre-backend.railway.app/docs`
- **Frontend**: `https://votre-app.vercel.app`

## 📊 Monitoring

### Railway
- Dashboard: Métriques CPU, RAM, réseau
- Logs: Surveillance en temps réel
- Alerts: Configuration des alertes

### Vercel
- Analytics: Trafic et performances
- Functions: Monitoring des fonctions
- Logs: Surveillance des erreurs

## 🔄 Déploiement continu

Une fois configuré, les déploiements futurs sont automatiques:
1. Push sur GitHub
2. Railway redéploie automatiquement le backend
3. Vercel redéploie automatiquement le frontend

## 💰 Coûts estimés

### Gratuit (pour démarrer)
- Railway: 500h/mois gratuites
- Vercel: 100GB bandwidth gratuit
- OpenAI: Pay-as-you-use (quelques dollars/mois pour usage modéré)

### Production
- Railway Pro: $5/mois
- Vercel Pro: $20/mois
- OpenAI: Variable selon utilisation

## ✅ Checklist finale

- [ ] Repository GitHub créé et pushé
- [ ] Backend déployé sur Railway
- [ ] Variables d'environnement configurées
- [ ] Frontend déployé sur Vercel
- [ ] URL backend configurée dans le frontend
- [ ] Test complet de l'application
- [ ] Monitoring configuré

🎉 **Félicitations ! Votre CV2Dossier est maintenant en ligne !**
