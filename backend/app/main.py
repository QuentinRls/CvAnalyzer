from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

from .routes import router
from .utils import logger


# Create FastAPI app
app = FastAPI(
    title="CV to Dossier de Compétences",
    description="API pour convertir un CV en dossier de compétences structuré",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

@app.get("/api")
async def root():
    """API root endpoint"""
    return {
        "message": "CV to Dossier de Compétences API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }

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


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("CV2Dossier API starting up...")
    
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
        log_level="info"
    )
