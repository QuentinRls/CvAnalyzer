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
    
    # Configuration du port - Railway utilise PORT, d'autres services utilisent parfois RAILWAY_PORT
    port = int(os.environ.get("PORT", os.environ.get("RAILWAY_PORT", 8000)))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Démarrage du serveur sur {host}:{port}")
    print(f"📁 Répertoire backend: {backend_dir}")
    print(f"🌍 Variables d'environnement de déploiement:")
    print(f"   PORT: {os.environ.get('PORT', 'non défini')}")
    print(f"   RAILWAY_PORT: {os.environ.get('RAILWAY_PORT', 'non défini')}")
    print(f"   HOST: {host}")
    
    # Debug: Afficher toutes les variables d'environnement liées à OpenAI
    print("🔍 Debug - Variables d'environnement:")
    env_vars = [key for key in os.environ.keys() if 'OPENAI' in key.upper() or 'API' in key.upper()]
    if env_vars:
        for var in env_vars:
            value = os.environ.get(var, '')
            masked_value = f"{value[:8]}..." if len(value) > 8 else "***"
            print(f"   {var} = {masked_value}")
    else:
        print("   ❌ Aucune variable contenant 'OPENAI' ou 'API' trouvée")
    
    # Vérifier la configuration OpenAI
    openai_key = os.environ.get('OPENAI_API_KEY')
    if openai_key:
        print(f"🔑 OpenAI configuré: ✅ (longueur: {len(openai_key)} caractères)")
    else:
        print(f"🔑 OpenAI configuré: ❌ (OPENAI_API_KEY non définie)")
        print("⚠️  L'extraction de CV ne fonctionnera pas sans clé API OpenAI")
    
    print("💡 Pour configurer OpenAI, définissez la variable d'environnement OPENAI_API_KEY")
    print(f"🌐 L'application va démarrer sur http://{host}:{port}")
    print("📝 Health check disponible sur /health")
    print("📚 Documentation API disponible sur /docs")
    
    try:
        # Démarrage de l'application
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ Erreur lors du démarrage de l'application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
