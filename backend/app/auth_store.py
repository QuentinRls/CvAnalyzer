"""
Store en mémoire pour la gestion des utilisateurs et des sessions
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
import uuid
import secrets
from .schemas import User, UserSession


class InMemoryAuthStore:
    """Store en mémoire pour les utilisateurs et sessions"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}  # user_id -> User
        self.sessions: Dict[str, UserSession] = {}  # session_token -> UserSession
        self.user_by_email: Dict[str, str] = {}  # email -> user_id
        
    def create_user(self, google_user_info: dict) -> User:
        """Créer un nouvel utilisateur à partir des infos Google"""
        user_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        user = User(
            id=user_id,
            email=google_user_info.get('email'),
            name=google_user_info.get('name', ''),
            picture=google_user_info.get('picture'),
            given_name=google_user_info.get('given_name'),
            family_name=google_user_info.get('family_name'),
            created_at=now,
            last_login=now
        )
        
        self.users[user_id] = user
        self.user_by_email[user.email] = user_id
        
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Récupérer un utilisateur par email"""
        user_id = self.user_by_email.get(email)
        if user_id:
            return self.users.get(user_id)
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Récupérer un utilisateur par ID"""
        return self.users.get(user_id)
    
    def update_last_login(self, user_id: str):
        """Mettre à jour la dernière connexion"""
        if user_id in self.users:
            self.users[user_id].last_login = datetime.utcnow()
    
    def create_session(self, user_id: str, expires_in_hours: int = 24) -> UserSession:
        """Créer une session pour un utilisateur"""
        session_token = secrets.token_urlsafe(32)
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=expires_in_hours)
        
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            expires_at=expires_at,
            created_at=now
        )
        
        self.sessions[session_token] = session
        return session
    
    def get_session(self, session_token: str) -> Optional[UserSession]:
        """Récupérer une session"""
        session = self.sessions.get(session_token)
        if session and session.expires_at > datetime.utcnow():
            return session
        elif session:
            # Session expirée, on la supprime
            del self.sessions[session_token]
        return None
    
    def delete_session(self, session_token: str):
        """Supprimer une session (logout)"""
        if session_token in self.sessions:
            del self.sessions[session_token]
    
    def get_user_sessions(self, user_id: str) -> List[UserSession]:
        """Récupérer toutes les sessions d'un utilisateur"""
        return [session for session in self.sessions.values() 
                if session.user_id == user_id and session.expires_at > datetime.utcnow()]
    
    def cleanup_expired_sessions(self):
        """Nettoyer les sessions expirées"""
        now = datetime.utcnow()
        expired_tokens = [token for token, session in self.sessions.items() 
                         if session.expires_at <= now]
        for token in expired_tokens:
            del self.sessions[token]
    
    def get_stats(self) -> dict:
        """Obtenir des statistiques sur le store"""
        self.cleanup_expired_sessions()
        return {
            "total_users": len(self.users),
            "active_sessions": len(self.sessions),
            "users": list(self.users.keys()),
        }


# Instance globale du store (en production, utilisez Redis ou une vraie DB)
auth_store = InMemoryAuthStore()