# Scripts PowerShell pour le développement

# Démarrer l'environnement de développement
function Start-DevEnvironment {
    Write-Host "🔧 Activation de l'environnement Python..." -ForegroundColor Green
    .venv\Scripts\Activate.ps1
    
    Write-Host "🚀 Démarrage du backend..." -ForegroundColor Green
    Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "python main.py"
    
    Write-Host "🎨 Démarrage du frontend..." -ForegroundColor Green
    Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"
    
    Write-Host "✅ Environnement de développement démarré!" -ForegroundColor Green
    Write-Host "Frontend: http://localhost:5173" -ForegroundColor Yellow
    Write-Host "Backend: http://localhost:8000" -ForegroundColor Yellow
}

# Build production
function Build-Production {
    Write-Host "🏗️  Construction du frontend..." -ForegroundColor Green
    cd frontend
    npm run build
    cd ..
    Write-Host "✅ Build terminé!" -ForegroundColor Green
}

# Installer toutes les dépendances
function Install-Dependencies {
    Write-Host "🐍 Installation des dépendances Python..." -ForegroundColor Green
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    
    Write-Host "📦 Installation des dépendances Node.js..." -ForegroundColor Green
    cd frontend
    npm install
    cd ..
    
    Write-Host "✅ Toutes les dépendances installées!" -ForegroundColor Green
}

# Afficher les alias
Write-Host "🔧 Scripts disponibles:" -ForegroundColor Cyan
Write-Host "  Start-DevEnvironment  - Démarre backend + frontend en mode dev" -ForegroundColor White
Write-Host "  Build-Production      - Construit le frontend pour production" -ForegroundColor White  
Write-Host "  Install-Dependencies  - Installe toutes les dépendances" -ForegroundColor White
