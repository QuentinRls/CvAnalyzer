"""
Configuration de la base de données
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# URL de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cv_analyzer.db")

# Pour PostgreSQL asyncio (production)
if DATABASE_URL.startswith("postgresql://"):
    # Railway utilise postgresql://, mais SQLAlchemy 2.0 préfère postgresql+asyncpg://
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    # Heroku utilise postgres://, conversion nécessaire
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
else:
    # SQLite pour le développement local
    ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./cv_analyzer.db"
    DATABASE_URL = "sqlite:///./cv_analyzer.db"

# Engines
# Engine synchrone (pour les migrations)
engine = create_engine(
    DATABASE_URL,
    echo=False,  # True pour debug SQL
)

# Engine asynchrone (pour l'application)
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,  # True pour debug SQL
    future=True
)

# Sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    async_engine, 
    expire_on_commit=False
)

# Base pour les modèles
Base = declarative_base()

# Dépendance pour obtenir une session DB
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Helper pour les opérations synchrones (migrations)
def get_sync_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()