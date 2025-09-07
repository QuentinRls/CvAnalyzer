#!/bin/bash

echo "🚀 Démarrage de l'application fullstack..."

# Détection de la commande Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Aucune commande Python trouvée"
    exit 1
fi

echo "✅ Utilisation de: $PYTHON_CMD"

# Vérification que les dépendances sont installées
echo "📦 Vérification des dépendances Python..."
$PYTHON_CMD -c "import fastapi, uvicorn" || {
    echo "📦 Installation des dépendances Python..."
    $PYTHON_CMD -m pip install -r requirements.txt || {
        echo "❌ Erreur lors de l'installation des dépendances Python"
        exit 1
    }
}

# Vérification que le frontend est buildé
if [ ! -d "frontend/dist" ]; then
    echo "� Build du frontend..."
    cd frontend
    npm ci || {
        echo "❌ Erreur lors de l'installation des dépendances Node.js"
        exit 1
    }
    npm run build || {
        echo "❌ Erreur lors du build du frontend"
        exit 1
    }
    cd ..
fi

# Démarrage de l'application
echo "✅ Démarrage du serveur..."
exec $PYTHON_CMD main.py
