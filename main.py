"""
Entry point for Railway deployment
"""
import sys
import os
from pathlib import Path

# Configuration des chemins
current_dir = Path(__file__).parent
backend_dir = current_dir / "backend"

# Ajouter le répertoire backend au PYTHONPATH
sys.path.insert(0, str(backend_dir))

# Vérifier que les modules sont accessibles
try:
    from app.main import app
    print("✅ FastAPI app importée avec succès")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print(f"PYTHONPATH: {sys.path}")
    print(f"Backend dir exists: {backend_dir.exists()}")
    if backend_dir.exists():
        print(f"Backend contents: {list(backend_dir.iterdir())}")
    sys.exit(1)

if __name__ == "__main__":
    import uvicorn
    
    # Configuration du port
    port = int(os.environ.get("PORT", 8000))
    
    print(f"🚀 Démarrage du serveur sur le port {port}")
    print(f"📁 Répertoire backend: {backend_dir}")
    print(f"🔑 OpenAI configuré: {bool(os.environ.get('OPENAI_API_KEY'))}")
    
    # Démarrage de l'application
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
