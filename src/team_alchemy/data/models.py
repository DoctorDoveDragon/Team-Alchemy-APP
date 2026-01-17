"""
SQLAlchemy database models.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


# Association table for many-to-many relationships
team_members = Table(
    'team_members',
    Base.metadata,
    Column('team_id', Integer, ForeignKey('teams.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teams = relationship("Team", secondary=team_members, back_populates="members")
    profile = relationship("UserProfile", back_populates="user", uselist=False)


class UserProfile(Base):
    """User personality profile."""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    archetype = Column(String(50))
    trait_scores = Column(JSON)
    jungian_type = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profile")


class Team(Base):
    """Team model."""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    members = relationship("User", secondary=team_members, back_populates="teams")
    analysis = relationship("TeamAnalysis", back_populates="team")


class TeamAnalysis(Base):
    """Team analysis results."""
    __tablename__ = "team_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    analysis_type = Column(String(50))
    results = Column(JSON)
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", back_populates="analysis")


# Import assessment ORM models to register them with Base
# This must be done after Base is defined to avoid circular imports
def _import_assessment_models():
    """Import assessment models to register them with SQLAlchemy Base."""
    try:
        from team_alchemy.core.assessment.models import (  # noqa: F401
            AssessmentORM,
            QuestionORM,
            ResponseORM,
        )
    except ImportError:
        # If models can't be imported, continue without them
        # This prevents circular import issues during initial setup
        pass


_import_assessment_models()
