#!/usr/bin/env python3
"""
Script de migration pour initialiser la base de données PostgreSQL sur Railway
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def main():
    """Exécuter les migrations Alembic"""
    
    print("🗄️ Initialisation de la base de données PostgreSQL...")
    
    # Vérifier la présence de la DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ Erreur: DATABASE_URL non définie")
        sys.exit(1)
    
    print(f"📍 Base de données: {database_url[:50]}...")
    
    try:
        # Vérifier la version actuelle
        print("\n📋 Vérification de l'état actuel des migrations...")
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "current"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print(f"✅ État actuel: {result.stdout.strip()}")
        else:
            print("⚠️ Aucune migration détectée (base vide)")
        
        # Exécuter les migrations
        print("\n🚀 Exécution des migrations...")
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Migrations exécutées avec succès!")
            print("📊 Tables créées:")
            print("   - users (utilisateurs)")
            print("   - user_sessions (sessions)")
            print("   - cv_analyses (analyses CV)")
            
            if result.stdout:
                print(f"\n📝 Détails: {result.stdout}")
        else:
            print(f"❌ Erreur lors des migrations: {result.stderr}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()