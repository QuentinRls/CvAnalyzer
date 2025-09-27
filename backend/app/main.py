from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

from .utils import logger

# Configuration des URLs depuis les variables d'environnement
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
FRONTEND_DEV_URL = os.getenv("FRONTEND_DEV_URL", "http://localhost:5173")

# Create FastAPI app
app = FastAPI(
    title="CV to Dossier de Compétences",
    description="API pour convertir un CV en dossier de compétences structuré",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS avec URLs d'environnement
allowed_origins = [FRONTEND_URL]
if FRONTEND_DEV_URL != FRONTEND_URL:
    allowed_origins.append(FRONTEND_DEV_URL)

# Ajouter l'URL Railway pour les tests cross-environment
railway_url = "https://cvanalyzer-production-36bc.up.railway.app"
if railway_url not in allowed_origins:
    allowed_origins.append(railway_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,  # Nécessaire pour les cookies
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include CV routes from cv_routes.py
try:
    from . import cv_routes
    app.include_router(cv_routes.router)
    logger.info("Routes CV chargées avec succès")
except Exception as e:
    logger.error(f"Erreur lors du chargement des routes CV: {e}")

# Include auth routes separately
try:
    from .routes.auth import router as auth_router
    app.include_router(auth_router, prefix="/api")
    logger.info("Routes d'authentification chargées avec succès")
except Exception as e:
    logger.error(f"Erreur lors du chargement des routes d'authentification: {e}")

@app.get("/api")
async def root():
    """API root endpoint"""
    return {
        "message": "CV to Dossier de Compétences API",
        "version": "0.1.0",
        "docs": "/docs"
    }

@app.get("/debug/routes")
async def debug_routes():
    """Debug endpoint to list all routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": getattr(route, 'name', 'Unknown')
            })
    return {"routes": routes}


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment"""
    return {"status": "healthy", "timestamp": "2025-09-10"}




# Configuration pour servir les fichiers statiques du frontend
# IMPORTANT: Ceci doit être APRÈS toutes les routes API
frontend_dist_path = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist_path), html=True), name="frontend")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


async def run_migrations():
    """Run Alembic migrations automatically"""
    try:
        logger.info("Running database migrations...")
        
        # Get the backend directory path
        backend_dir = Path(__file__).parent.parent
        
        # Run Alembic upgrade
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("Database migrations completed successfully")
            logger.debug(f"Migration output: {result.stdout}")
        else:
            logger.error(f"Migration failed: {result.stderr}")
            # Don't raise exception to allow app to start even if migrations fail
            
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        # Don't raise exception to allow app to start even if migrations fail


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("CV2Dossier API starting up...")
    
    # Auto-migrate database on startup (for Railway deployment)
    await run_migrations()
    
    # Validate environment
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not set - extraction will fail")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("CV2Dossier API shutting down...")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        workers=1,  # Garde 1 worker en mode reload
        limit_concurrency=100,  # Augmente la limite de concurrence
        limit_max_requests=1000,  # Augmente la limite de requêtes
        timeout_keep_alive=30  # Garde les connexions ouvertes plus longtemps
    )
