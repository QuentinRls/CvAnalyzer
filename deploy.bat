@echo off
REM Script de déploiement automatisé pour CV2Dossier (Windows)

echo 🚀 Déploiement de CV2Dossier...

REM Vérification de Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git n'est pas installé
    pause
    exit /b 1
)

REM Vérification de Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js n'est pas installé
    pause
    exit /b 1
)

REM Configuration Git
set /p git_username="📝 Nom d'utilisateur Git: "
set /p git_email="📝 Email Git: "

git config --global user.name "%git_username%"
git config --global user.email "%git_email%"

REM Initialisation du repository Git
echo 📦 Initialisation du repository Git...
git init
git add .
git commit -m "Initial commit: CV2Dossier with Devoteam branding"

echo.
echo 📋 ÉTAPES SUIVANTES:
echo.
echo 1️⃣  CRÉER UN REPOSITORY GITHUB:
echo    - Aller sur https://github.com/new
echo    - Nom: cv2dossier
echo    - Description: Analyseur de CV intelligent avec IA
echo    - Public ou Privé (selon vos préférences)
echo    - NE PAS initialiser avec README, .gitignore ou licence
echo.

echo 2️⃣  CONNECTER LE REPOSITORY LOCAL:
echo    git remote add origin https://github.com/VOTRE_USERNAME/cv2dossier.git
echo    git branch -M main
echo    git push -u origin main
echo.

echo 3️⃣  DÉPLOYER LE BACKEND (Railway):
echo    - Aller sur https://railway.app
echo    - Connecter votre compte GitHub
echo    - New Project ^> Deploy from GitHub repo
echo    - Sélectionner cv2dossier
echo    - Ajouter les variables d'environnement:
echo      * OPENAI_API_KEY=votre_clé_openai
echo      * PORT=8000
echo.

echo 4️⃣  DÉPLOYER LE FRONTEND (Vercel):
echo    - Aller sur https://vercel.com
echo    - Connecter votre compte GitHub
echo    - New Project ^> Import Git Repository
echo    - Sélectionner cv2dossier
echo    - Framework Preset: Vite
echo    - Root Directory: frontend
echo    - Build Command: npm run build
echo    - Output Directory: dist
echo    - Ajouter la variable d'environnement:
echo      * VITE_API_URL=https://votre-backend-railway.up.railway.app
echo.

echo 5️⃣  TESTER LE DÉPLOIEMENT:
echo    - Backend: https://votre-backend-railway.up.railway.app/health
echo    - Frontend: https://votre-app-vercel.app
echo.

echo ✅ Fichiers de configuration créés avec succès!
echo 📁 Repository Git initialisé et prêt pour le déploiement
echo.
echo 💡 ASTUCE: Assurez-vous d'avoir votre clé API OpenAI prête!
echo.
pause
