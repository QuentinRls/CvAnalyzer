"""
Service d'authentification avec base de données
Remplace auth_store.py
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, select, func, or_

from .models import User, UserSession
from .database import AsyncSessionLocal
from .utils.logger import logger
import secrets
import uuid

class DatabaseAuthService:
    """Service d'authentification utilisant PostgreSQL/SQLite"""
    
    async def create_or_update_user(
        self, 
        google_id: str, 
        email: str, 
        name: str, 
        picture: Optional[str] = None
    ) -> User:
        """Créer un nouvel utilisateur ou mettre à jour un existant"""
        async with AsyncSessionLocal() as session:
            # Chercher utilisateur existant par google_id ou par email
            result = await session.execute(select(User).filter(
                or_(User.google_id == google_id, User.email == email)
            ))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                # Mettre à jour les informations
                existing_user.name = name
                existing_user.picture = picture
                existing_user.google_id = google_id  # Mettre à jour le google_id si nécessaire
                existing_user.last_login = datetime.utcnow()
                existing_user.updated_at = datetime.utcnow()
                
                await session.commit()
                await session.refresh(existing_user)
                logger.info(f"Utilisateur mis à jour: {email}")
                return existing_user
            else:
                # Créer nouvel utilisateur
                new_user = User(
                    id=str(uuid.uuid4()),
                    google_id=google_id,
                    email=email,
                    name=name,
                    picture=picture,
                    created_at=datetime.utcnow(),
                    last_login=datetime.utcnow()
                )
                
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                logger.info(f"Nouvel utilisateur créé: {email}")
                return new_user
    
    async def create_session(
        self, 
        user_id: str, 
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[str, datetime]:
        """Créer une nouvelle session utilisateur"""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)  # 7 jours
        
        async with AsyncSessionLocal() as session:
            new_session = UserSession(
                id=str(uuid.uuid4()),
                user_id=user_id,
                session_token=session_token,
                expires_at=expires_at,
                is_active=True,
                created_at=datetime.utcnow(),
                last_used=datetime.utcnow(),
                user_agent=user_agent,
                ip_address=ip_address
            )
            
            session.add(new_session)
            await session.commit()
            
            logger.info(f"Session créée pour utilisateur {user_id}")
            return session_token, expires_at
    
    async def validate_session(self, session_token: str) -> Optional[User]:
        """Valider un token de session et retourner l'utilisateur"""
        async with AsyncSessionLocal() as session:
            # Chercher session active et non expirée
            result = await session.execute(select(UserSession).filter(
                and_(
                    UserSession.session_token == session_token,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.utcnow()
                )
            ))
            user_session = result.scalar_one_or_none()
            
            if not user_session:
                return None
            
            # Récupérer l'utilisateur
            user_result = await session.execute(select(User).filter(
                User.id == user_session.user_id
            ))
            user = user_result.scalar_one_or_none()
            
            if user:
                # Mettre à jour last_used
                user_session.last_used = datetime.utcnow()
                await session.commit()
                
                logger.debug(f"Session validée pour: {user.email}")
                return user
            
            return None
    
    async def invalidate_session(self, session_token: str) -> bool:
        """Invalider une session (logout)"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(UserSession).filter(
                UserSession.session_token == session_token
            ))
            user_session = result.scalar_one_or_none()
            
            if user_session:
                user_session.is_active = False
                await session.commit()
                logger.info(f"Session invalidée: {session_token[:8]}...")
                return True
            
            return False
    
    async def cleanup_expired_sessions(self) -> int:
        """Nettoyer les sessions expirées"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(UserSession).filter(
                UserSession.expires_at < datetime.utcnow()
            ))
            expired_sessions = result.scalars().all()
            
            count = len(expired_sessions)
            
            for expired_session in expired_sessions:
                expired_session.is_active = False
            
            await session.commit()
            
            logger.info(f"Nettoyage: {count} sessions expirées désactivées")
            return count
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Récupérer un utilisateur par son ID"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).filter(User.id == user_id))
            user = result.scalar_one_or_none()
            return user
    
    async def get_user_stats(self) -> dict:
        """Statistiques des utilisateurs (pour debug/admin)"""
        async with AsyncSessionLocal() as session:
            total_users_result = await session.execute(select(func.count(User.id)))
            total_users = total_users_result.scalar()
            
            active_sessions_result = await session.execute(select(func.count(UserSession.id)).filter(
                and_(
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.utcnow()
                )
            ))
            active_sessions = active_sessions_result.scalar()
            
            return {
                "total_users": total_users,
                "active_sessions": active_sessions,
                "last_updated": datetime.utcnow().isoformat()
            }

# Instance globale
db_auth_service = DatabaseAuthService()