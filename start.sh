#!/bin/bash

echo "🚀 Démarrage de l'application fullstack..."

# Installation des dépendances Python
echo "📦 Installation des dépendances Python..."
pip install -r requirements.txt || {
    echo "❌ Erreur lors de l'installation des dépendances Python"
    exit 1
}

# Installation des dépendances Node.js
echo "📦 Installation des dépendances frontend..."
cd frontend
npm ci || {
    echo "❌ Erreur lors de l'installation des dépendances Node.js"
    exit 1
}

# Build du frontend
echo "🔨 Build du frontend..."
npm run build || {
    echo "❌ Erreur lors du build du frontend"
    exit 1
}

# Retour au dossier racine
cd ..

# Démarrage de l'application
echo "✅ Démarrage du serveur..."
python main.py
