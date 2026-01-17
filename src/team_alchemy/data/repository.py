"""
Database session management and repository pattern.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

from team_alchemy.data.models import Base

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./team_alchemy.db"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reinit_engine():
    """
    Reinitialize the engine and session factory with current DATABASE_URL.
    
    This function should be called when the DATABASE_URL environment variable
    has been changed after the module was first imported. It disposes of the
    existing engine (closing all connections) and creates a new one with the
    updated URL.
    
    Note: This modifies global module state (engine, SessionLocal, DATABASE_URL).
    Use with caution in production code - primarily intended for testing.
    
    Side effects:
    - Disposes the existing database engine (closes all active connections)
    - Recreates the engine with the current DATABASE_URL from environment
    - Recreates the SessionLocal session factory
    """
    global engine, SessionLocal, DATABASE_URL
    
    # Get current DATABASE_URL from environment
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./team_alchemy.db")
    
    # Dispose of old engine if it exists
    if engine is not None:
        engine.dispose()
    
    # Create new engine
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
    )
    
    # Recreate session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all database tables (use with caution!)."""
    Base.metadata.drop_all(bind=engine)
