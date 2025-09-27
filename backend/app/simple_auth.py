"""
Version synchrone temporaire de l'authentification pour Railway
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

from .schemas import User, AuthResponse
from .utils.logger import logger


class SimpleAuthService:
    """Service d'authentification Google OAuth 2.0 simplifié (sans base de données async)"""
    
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        if not all([self.client_id, self.client_secret]):
            logger.error("Variables d'environnement Google OAuth manquantes")
            self.is_configured = False
        else:
            self.is_configured = True
        
        # Scopes nécessaires
        self.scopes = [
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ]
        
        # URL de redirection
        self.redirect_uri = os.getenv('OAUTH_REDIRECT_URI')
        if not self.redirect_uri:
            backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000')
            self.redirect_uri = f'{backend_url}/api/auth/callback'
    
    def get_authorization_url(self, state: Optional[str] = None) -> Tuple[str, str]:
        """Générer l'URL d'autorisation Google"""
        if not state:
            state = secrets.token_urlsafe(32)
        
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
            flow = google_auth_oauthlib.flow.Flow.from_client_config(
                client_config,
                scopes=self.scopes
            )
            flow.redirect_uri = self.redirect_uri
            
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state,
                prompt='consent'
            )
            
            logger.info(f"URL d'autorisation générée: {authorization_url}")
            return authorization_url, state
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'URL: {e}")
            raise
    
    def complete_oauth_callback(self, code: str, state: str) -> AuthResponse:
        """Compléter le callback OAuth (version simplifiée)"""
        try:
            client_config = {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            }
            
            flow = google_auth_oauthlib.flow.Flow.from_client_config(
                client_config,
                scopes=self.scopes,
                state=state
            )
            flow.redirect_uri = self.redirect_uri
            
            # Récupérer le token
            flow.fetch_token(code=code)
            
            # Récupérer les infos utilisateur
            user_info = self._get_user_info(flow.credentials)
            
            # Créer un utilisateur temporaire (sans base de données)
            user = User(
                id=hash(user_info['email']),  # ID temporaire basé sur l'email
                email=user_info['email'],
                name=user_info.get('name', ''),
                picture=user_info.get('picture', ''),
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            
            logger.info(f"Utilisateur connecté (temporaire): {user.email}")
            
            return AuthResponse(
                user=user,
                session_token="temp_token_" + secrets.token_urlsafe(32),
                message="Connexion réussie (mode temporaire)"
            )
            
        except Exception as e:
            logger.error(f"Erreur lors du callback: {e}")
            raise
    
    def _get_user_info(self, credentials) -> dict:
        """Récupérer les informations utilisateur depuis Google"""
        try:
            # Utiliser directement l'API REST
            headers = {'Authorization': f'Bearer {credentials.token}'}
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos utilisateur: {e}")
            raise


# Instance globale
simple_auth_service = SimpleAuthService()