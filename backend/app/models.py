"""
Modèles de base de données pour CV Analyzer
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    picture = Column(String, nullable=True)
    google_id = Column(String, unique=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relations
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    cv_analyses = relationship("CVAnalysis", back_populates="user", cascade="all, delete-orphan")

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    session_token = Column(String, unique=True, nullable=False)
    
    # Session data
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    last_used = Column(DateTime, default=func.now())
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    
    # Relations
    user = relationship("User", back_populates="sessions")

class CVAnalysis(Base):
    __tablename__ = "cv_analyses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Fichier CV original
    original_filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, docx, txt
    file_size = Column(Integer, nullable=True)
    
    # Contenu extrait
    raw_text = Column(Text, nullable=True)
    structured_data = Column(JSON, nullable=True)  # Données extraites structurées
    
    # Métadonnées d'analyse
    extraction_status = Column(String, default="pending")  # pending, completed, failed
    extraction_error = Column(Text, nullable=True)
    processing_time = Column(Integer, nullable=True)  # en millisecondes
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="cv_analyses")
    comparisons = relationship("CVComparison", back_populates="cv_analysis", cascade="all, delete-orphan")

class CVComparison(Base):
    __tablename__ = "cv_comparisons"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cv_analysis_id = Column(String, ForeignKey("cv_analyses.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Mission/Offre d'emploi
    mission_title = Column(String, nullable=False)
    mission_description = Column(Text, nullable=False)
    mission_filename = Column(String, nullable=True)
    
    # Résultats de comparaison
    comparison_results = Column(JSON, nullable=True)
    match_score = Column(Integer, nullable=True)  # Score de 0 à 100
    
    # Métadonnées
    comparison_status = Column(String, default="pending")  # pending, completed, failed
    comparison_error = Column(Text, nullable=True)
    processing_time = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relations
    cv_analysis = relationship("CVAnalysis", back_populates="comparisons")
    user = relationship("User")

class GeneratedReport(Base):
    __tablename__ = "generated_reports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    cv_analysis_id = Column(String, ForeignKey("cv_analyses.id"), nullable=True)
    comparison_id = Column(String, ForeignKey("cv_comparisons.id"), nullable=True)
    
    # Rapport généré
    report_type = Column(String, nullable=False)  # pdf, pptx
    report_title = Column(String, nullable=False)
    file_path = Column(String, nullable=True)  # Chemin de stockage du fichier
    file_size = Column(Integer, nullable=True)
    
    # Métadonnées
    generation_status = Column(String, default="pending")  # pending, completed, failed
    generation_error = Column(Text, nullable=True)
    processing_time = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)  # Date d'expiration du fichier
    
    # Relations
    user = relationship("User")
    cv_analysis = relationship("CVAnalysis")
    comparison = relationship("CVComparison")