"""
Routes d'authentification Google OAuth 2.0
"""

from fastapi import APIRouter, HTTPException, Request, Response, Cookie, Depends
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from typing import Optional
import secrets
import os

from ..auth import google_auth_service
from ..db_auth_service import db_auth_service
from ..simple_auth import simple_auth_service
from ..schemas import User, AuthResponse
from ..utils.logger import logger


router = APIRouter(prefix="/auth", tags=["Authentication"])


# Store temporaire pour les états OAuth (en production, utilisez Redis)
oauth_states = {}


@router.get("/login")
async def login():
    """Initier la connexion Google OAuth"""
    try:
        # Vérifier que Google OAuth est configuré
        if not google_auth_service.is_configured:
            logger.error("Google OAuth non configuré - vérifiez GOOGLE_CLIENT_ID et GOOGLE_CLIENT_SECRET")
            raise HTTPException(status_code=500, detail="Authentification non configurée")
        
        # Générer un état de sécurité
        state = secrets.token_urlsafe(32)
        
        # Obtenir l'URL d'autorisation Google - essayer le service normal puis le simplifié
        try:
            auth_url, _ = google_auth_service.get_authorization_url(state)
        except Exception as e:
            if "greenlet" in str(e).lower() or "libstdc" in str(e).lower():
                logger.warning(f"Erreur greenlet détectée au login, utilisation du service simplifié: {e}")
                auth_url, _ = simple_auth_service.get_authorization_url(state)
            else:
                raise e
        
        # Stocker l'état temporairement
        oauth_states[state] = True
        
        logger.info(f"Redirection vers Google OAuth: {auth_url}")
        
        return {
            "auth_url": auth_url,
            "state": state,
            "message": "Redirigez vers auth_url pour vous connecter"
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initiation de la connexion: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'initiation de la connexion")


@router.get("/callback")
async def callback(code: str, state: str, response: Response):
    """Callback après authentification Google"""
    try:
        # Vérifier l'état de sécurité
        if state not in oauth_states:
            logger.warning(f"État OAuth invalide: {state}")
            raise HTTPException(status_code=400, detail="État OAuth invalide")
        
        # Supprimer l'état utilisé
        del oauth_states[state]
        
        # Traiter le callback - essayer d'abord le service normal, puis le simplifié si erreur greenlet
        try:
            auth_response = await google_auth_service.complete_oauth_callback(code, state)
        except Exception as db_error:
            if "greenlet" in str(db_error).lower() or "libstdc" in str(db_error).lower():
                logger.warning(f"Erreur greenlet détectée, utilisation du service simplifié: {db_error}")
                # Utiliser le service simplifié sans base de données
                auth_response = simple_auth_service.complete_oauth_callback(code, state)
            else:
                raise db_error
        
        # Définir le cookie de session
        response.set_cookie(
            key="session_token",
            value=auth_response.session_token,
            httponly=True,
            secure=False,  # True en production avec HTTPS
            samesite="lax",
            max_age=24 * 60 * 60,  # 24 heures
            domain=None,  # Domaine automatique basé sur l'hôte
            path="/"  # Disponible sur tous les chemins
        )
        
        logger.info(f"Connexion réussie pour: {auth_response.user.email}")
        
        # URL du frontend depuis l'environnement
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        
        # Créer une page HTML qui définit le cookie et redirige
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Connexion réussie</title>
        </head>
        <body>
            <div style="text-align: center; font-family: Arial, sans-serif; margin-top: 50px;">
                <h2>Connexion réussie ✅</h2>
                <p>Redirection en cours...</p>
                <script>
                    // Définir le cookie côté client (domaine dynamique)
                    const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
                    const cookieDomain = isProduction ? window.location.hostname : 'localhost';
                    document.cookie = `session_token={auth_response.session_token}; path=/; domain=${{cookieDomain}}; max-age=86400; SameSite=Lax`;
                    
                    // Redirection vers le frontend (URL dynamique)
                    const frontendUrl = '{frontend_url}';
                    setTimeout(() => {{
                        window.location.href = frontendUrl + '/dashboard';
                    }}, 1000);
                </script>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Erreur lors du callback: {e}")
        # Rediriger vers la page de login avec erreur
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return RedirectResponse(
            url=f"{frontend_url}/login?error=auth_failed",
            status_code=302
        )


@router.get("/me", response_model=User)
async def get_current_user(session_token: Optional[str] = Cookie(None)):
    """Obtenir les informations de l'utilisateur connecté"""
    if not session_token:
        raise HTTPException(status_code=401, detail="Session token manquant")
    
    user = await google_auth_service.verify_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Session invalide ou expirée")
    
    return user


@router.post("/logout")
async def logout(response: Response, session_token: Optional[str] = Cookie(None)):
    """Déconnecter l'utilisateur"""
    if session_token:
        await google_auth_service.logout(session_token)
    
    # Supprimer le cookie avec les mêmes paramètres que lors de la création
    response.delete_cookie(
        key="session_token", 
        domain="localhost", 
        path="/"
    )
    
    return {"message": "Déconnexion réussie"}


@router.get("/status")
async def auth_status(session_token: Optional[str] = Cookie(None)):
    """Vérifier le statut d'authentification"""
    if not session_token:
        return {"authenticated": False, "user": None}
    
    user = await google_auth_service.verify_session(session_token)
    if not user:
        return {"authenticated": False, "user": None}
    
    return {"authenticated": True, "user": user}


@router.get("/stats")
async def auth_stats():
    """Obtenir des statistiques d'authentification (pour debug)"""
    stats = await db_auth_service.get_user_stats()
    return {
        "stats": stats,
        "oauth_states_count": len(oauth_states)
    }


# Dependency pour obtenir l'utilisateur connecté
async def get_current_user_dependency(session_token: Optional[str] = Cookie(None)) -> User:
    """Dependency pour récupérer l'utilisateur connecté"""
    if not session_token:
        raise HTTPException(status_code=401, detail="Session token manquant")
    
    user = await google_auth_service.verify_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Session invalide ou expirée")
    
    return user


# Dependency pour les routes optionnellement protégées
async def get_current_user_optional(session_token: Optional[str] = Cookie(None)) -> Optional[User]:
    """Dependency pour récupérer l'utilisateur connecté (optionnel)"""
    if not session_token:
        return None
    
    return await google_auth_service.verify_session(session_token)