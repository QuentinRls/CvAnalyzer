# 🚀 CV2Dossier - Quick Deploy

## ⚡ Déploiement Rapide (5 minutes)

### 1. GitHub Repository
```bash
# Déjà fait ! Votre repo est initialisé localement
# Il vous suffit de créer le repo sur GitHub et pusher
```

### 2. Railway (Backend) - 2 minutes
1. 🔗 [railway.app](https://railway.app) → Login GitHub
2. ➕ New Project → Deploy from GitHub repo
3. 📂 Sélectionner `cv2dossier`
4. ⚙️ Variables → Ajouter `OPENAI_API_KEY`
5. ✅ Auto-deploy activé !

### 3. Vercel (Frontend) - 2 minutes
1. 🔗 [vercel.com](https://vercel.com) → Login GitHub  
2. ➕ New Project → Import Git Repository
3. 📂 Sélectionner `cv2dossier`
4. ⚙️ Settings:
   - Framework: **Vite**
   - Root Directory: **frontend**
   - Build Command: **npm run build**
   - Output Directory: **dist**
5. 🔧 Environment Variables → `VITE_API_URL=https://your-railway-url.railway.app`
6. 🚀 Deploy !

### 4. Test Final - 1 minute
- ✅ Backend Health: `https://your-railway-url.railway.app/health`
- ✅ Frontend: `https://your-vercel-app.vercel.app`
- ✅ Upload CV test

## 🎯 URLs à retenir
- **Docs API**: `https://your-railway-url.railway.app/docs`
- **Frontend**: `https://your-vercel-app.vercel.app`

## 💡 Pro Tips
- 🔑 Clé OpenAI prête ? → [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- 📊 Monitoring → Railway Dashboard & Vercel Analytics
- 🔄 Auto-deploy → Chaque push GitHub = nouveau déploiement

## 🆘 Support
Erreur ? Vérifiez:
1. Variables d'environnement Railway
2. URL backend dans Vercel
3. Logs Railway/Vercel pour debug

**🎉 Votre CV2Dossier sera en ligne en moins de 5 minutes !**
