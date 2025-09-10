#!/bin/bash
echo "🚀 Démarrage de l'application..."

# Debug: vérifier la structure des fichiers
echo "📁 Contenu du répertoire racine:"
ls -la

echo "📁 Contenu du répertoire backend:"
ls -la backend/

echo "📁 Contenu du répertoire backend/app:"
ls -la backend/app/

# Vérifier que Python peut importer l'application
echo "🔍 Test d'import de l'application..."
python3 -c "
import sys
import os
sys.path.insert(0, './backend')
try:
    from app.main import app
    print('✅ Import réussi!')
except Exception as e:
    print(f'❌ Erreur d\\'import: {e}')
    import traceback
    traceback.print_exc()
"

echo "🚀 Démarrage du serveur..."
# Démarrer l'application directement
exec python3 main.py