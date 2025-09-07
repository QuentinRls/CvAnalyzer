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

# Installation de pip si nécessaire
echo "📦 Vérification de pip..."
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "📦 Installation de pip..."
    if command -v curl &> /dev/null; then
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        $PYTHON_CMD get-pip.py
        rm get-pip.py
    elif $PYTHON_CMD -m ensurepip --version &> /dev/null 2>&1; then
        $PYTHON_CMD -m ensurepip --upgrade
    else
        echo "❌ Impossible d'installer pip"
        exit 1
    fi
fi

# Installation des dépendances Python
echo "📦 Installation des dépendances Python..."
$PYTHON_CMD -m pip install -r requirements.txt || {
    echo "❌ Erreur lors de l'installation des dépendances Python"
    exit 1
}

# Vérification que le frontend est buildé
if [ ! -d "frontend/dist" ]; then
    echo "🔨 Build du frontend..."
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
