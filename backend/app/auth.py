"""
Service d'authentification Google OAuth 2.0
"""

import os
from typing import Optional, Tuple
import secrets
from datetime import datetime
import requests
from urllib.parse import urlencode

import google.oauth2.credentials
import google_auth_oauthlib.flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .db_auth_service import db_auth_service
from .schemas import User, UserSession, AuthResponse
from .utils.logger import logger
from .database import get_db


class GoogleAuthService:
    """Service pour l'authentification Google OAuth 2.0"""
    
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.project_id = os.getenv('GOOGLE_PROJECT_ID')
        
        if not all([self.client_id, self.client_secret]):
            raise ValueError("Variables d'environnement Google OAuth manquantes")
        
        # Scopes nécessaires pour récupérer les infos utilisateur
        self.scopes = [
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ]
        
        # URL de redirection depuis l'environnement
        # Priorité : OAUTH_REDIRECT_URI (Railway) > BACKEND_URL/api/auth/callback (local)
        self.redirect_uri = os.getenv('OAUTH_REDIRECT_URI')
        if not self.redirect_uri:
            backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000')
            self.redirect_uri = f'{backend_url}/api/auth/callback'
    
    def get_authorization_url(self, state: Optional[str] = None) -> Tuple[str, str]:
        """
        Générer l'URL d'autorisation Google et l'état de sécurité
        Returns: (authorization_url, state)
        """
        if not state:
            state = secrets.token_urlsafe(32)
        
        # Configuration du client secrets (normalement dans un fichier JSON)
        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.redirect_uri]
            }
        }
        
        try:
            # Créer le flow OAuth
            flow = google_auth_oauthlib.flow.Flow.from_client_config(
                client_config,
                scopes=self.scopes
            )
            flow.redirect_uri = self.redirect_uri
            
            # Générer l'URL d'autorisation
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state,
                prompt='consent'
            )
            
            logger.info(f"URL d'autorisation générée: {authorization_url}")
            return authorization_url, state
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'URL d'autorisation: {e}")
            raise
    
    async def complete_oauth_callback(self, code: str, state: str) -> AuthResponse:
        """
        Traiter le callback de Google après authentification
        """
        try:
            # Configuration du client
            client_config = {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            }
            
            # Créer le flow
            flow = google_auth_oauthlib.flow.Flow.from_client_config(
                client_config,
                scopes=self.scopes,
                state=state
            )
            flow.redirect_uri = self.redirect_uri
            
            # Échanger le code contre des tokens
            flow.fetch_token(code=code)
            
            # Récupérer les informations utilisateur
            user_info = self._get_user_info(flow.credentials)
            
            # Créer ou récupérer l'utilisateur
            user = await self._get_or_create_user(user_info)
            
            # Créer une session
            session_token, expires_at = await db_auth_service.create_session(user.id)
            
            # La mise à jour de last_login est déjà faite dans create_or_update_user
            
            logger.info(f"Utilisateur connecté: {user.email}")
            
            # Convertir le modèle SQLAlchemy en schéma Pydantic
            user_schema = User.model_validate(user, from_attributes=True)
            
            return AuthResponse(
                user=user_schema,
                session_token=session_token,
                message="Connexion réussie"
            )
            
        except Exception as e:
            logger.error(f"Erreur lors du callback: {e}")
            raise
    
    def _get_user_info(self, credentials) -> dict:
        """Récupérer les informations utilisateur depuis Google"""
        try:
            # Vérifier d'abord s'il y a un ID token (méthode préférée)
            if hasattr(credentials, 'id_token') and credentials.id_token:
                # Décoder le ID token JWT pour obtenir le 'sub' (Google ID)
                try:
                    id_info = id_token.verify_oauth2_token(
                        credentials.id_token, 
                        google_requests.Request(), 
                        self.client_id
                    )
                    logger.debug(f"Infos du ID token: {id_info}")
                    return id_info
                except Exception as e:
                    logger.warning(f"Erreur lors du décodage du ID token: {e}, fallback vers API userinfo")
            
            # Fallback vers l'API userinfo si pas d'ID token
            userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
            headers = {"Authorization": f"Bearer {credentials.token}"}
            
            response = requests.get(userinfo_url, headers=headers)
            response.raise_for_status()
            
            user_info = response.json()
            logger.info(f"Infos utilisateur récupérées: {user_info.get('email')}")
            logger.debug(f"Toutes les infos Google reçues: {user_info}")
            
            return user_info
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos utilisateur: {e}")
            raise
    
    async def _get_or_create_user(self, google_user_info: dict) -> User:
        """Créer ou récupérer un utilisateur"""
        email = google_user_info.get('email')
        # L'API userinfo v1 retourne 'id' au lieu de 'sub'
        google_id = google_user_info.get('sub') or google_user_info.get('id')
        name = google_user_info.get('name')
        picture = google_user_info.get('picture')
        
        if not email:
            raise ValueError("Email manquant dans les informations Google")
        
        # Si pas de Google ID, utiliser l'email comme identifiant unique
        if not google_id:
            logger.warning(f"Pas de Google ID trouvé pour {email}, utilisation de l'email comme identifiant")
            google_id = f"email:{email}"
        
        logger.debug(f"Création/mise à jour utilisateur: email={email}, google_id={google_id}, name={name}")
        
        # Créer ou mettre à jour l'utilisateur
        user = await db_auth_service.create_or_update_user(
            google_id=google_id,
            email=email,
            name=name,
            picture=picture
        )
        
        return user
    
    async def verify_session(self, session_token: str) -> Optional[User]:
        """Vérifier si une session est valide et retourner l'utilisateur"""
        if not session_token:
            return None
        
        user = await db_auth_service.validate_session(session_token)
        return user
    
    async def logout(self, session_token: str) -> bool:
        """Déconnecter un utilisateur"""
        if session_token:
            await db_auth_service.invalidate_session(session_token)
            logger.info("Utilisateur déconnecté")
            return True
        return False


# Instance globale du service
google_auth_service = GoogleAuthService()