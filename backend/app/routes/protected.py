"""
Exemple d'utilisation des routes protégées
"""

from fastapi import APIRouter, Depends
from typing import Optional

from ..schemas import User
from ..routes.auth import get_current_user_dependency, get_current_user_optional

router = APIRouter(prefix="/api/protected", tags=["Protected Routes"])


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user_dependency)):
    """Route protégée - nécessite une authentification"""
    return {
        "message": f"Bonjour {current_user.name}!",
        "user": current_user,
        "protected": True
    }


@router.get("/dashboard")
async def dashboard(current_user: User = Depends(get_current_user_dependency)):
    """Dashboard utilisateur - route protégée"""
    return {
        "message": "Bienvenue sur votre dashboard",
        "user": {
            "name": current_user.name,
            "email": current_user.email,
            "picture": current_user.picture
        },
        "data": {
            "total_cvs_processed": 0,  # À implémenter avec votre logique
            "last_login": current_user.last_login
        }
    }


@router.get("/public-info")
async def public_info(current_user: Optional[User] = Depends(get_current_user_optional)):
    """Route publique avec info utilisateur optionnelle"""
    if current_user:
        return {
            "message": f"Bonjour {current_user.name}, vous êtes connecté!",
            "authenticated": True,
            "user": current_user
        }
    else:
        return {
            "message": "Bonjour visiteur anonyme!",
            "authenticated": False,
            "user": None
        }