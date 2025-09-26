"""
Middleware d'authentification pour FastAPI
"""

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import secrets

from .auth import google_auth_service
from .schemas import User
from .utils.logger import logger


class AuthMiddleware:
    """Middleware pour vérifier l'authentification sur les routes protégées"""
    
    def __init__(self):
        self.security = HTTPBearer(auto_error=False)
    
    async def __call__(self, request: Request) -> Optional[User]:
        """
        Vérifier si l'utilisateur est authentifié
        Retourne l'utilisateur ou None si pas connecté
        """
        # Récupérer le token depuis les cookies
        session_token = request.cookies.get('session_token')
        
        if not session_token:
            return None
        
        # Vérifier la session
        user = google_auth_service.verify_session(session_token)
        
        if user:
            # Ajouter l'utilisateur à la request pour utilisation ultérieure
            request.state.user = user
            logger.debug(f"Utilisateur authentifié: {user.email}")
        
        return user


# Instance globale du middleware
auth_middleware = AuthMiddleware()


def require_auth(user: Optional[User] = None) -> User:
    """
    Dependency qui requiert une authentification
    Lève une exception si l'utilisateur n'est pas connecté
    """
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentification requise"
        )
    return user


def optional_auth(user: Optional[User] = None) -> Optional[User]:
    """
    Dependency qui accepte un utilisateur optionnel
    Ne lève pas d'exception si l'utilisateur n'est pas connecté
    """
    return user


# Decorator pour protéger des routes
def protected_route(func):
    """
    Décorateur pour protéger une route
    Usage: @protected_route
    """
    async def wrapper(*args, **kwargs):
        # Récupérer la request depuis les arguments
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        
        if not request:
            raise HTTPException(status_code=500, detail="Request not found")
        
        # Vérifier l'authentification
        user = await auth_middleware(request)
        if not user:
            raise HTTPException(status_code=401, detail="Authentification requise")
        
        # Ajouter l'utilisateur aux kwargs
        kwargs['current_user'] = user
        
        return await func(*args, **kwargs)
    
    return wrapper