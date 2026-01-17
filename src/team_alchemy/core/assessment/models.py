"""
Data models for assessments using Pydantic and SQLAlchemy.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship

# Import Base from main data models to ensure all ORM models use the same Base
from team_alchemy.data.models import Base


class QuestionType(str, Enum):
    """Types of assessment questions."""
    MULTIPLE_CHOICE = "multiple_choice"
    SCALE = "scale"
    TEXT = "text"
    RANKING = "ranking"


class AssessmentStatus(str, Enum):
    """Status of an assessment."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ANALYZED = "analyzed"


# Pydantic Models for API validation
class QuestionBase(BaseModel):
    """Base question model."""
    text: str = Field(..., min_length=1, max_length=1000)
    question_type: QuestionType
    options: Optional[List[str]] = None
    category: str
    weight: float = Field(default=1.0, ge=0, le=1)
    
    @validator('options')
    def validate_options(cls, v, values):
        """Ensure options are provided for multiple choice questions."""
        if values.get('question_type') == QuestionType.MULTIPLE_CHOICE and not v:
            raise ValueError("Multiple choice questions must have options")
        return v


class Question(QuestionBase):
    """Question model with ID."""
    id: int
    
    class Config:
        from_attributes = True


class ResponseBase(BaseModel):
    """Base response model."""
    question_id: int
    answer: Any
    confidence: Optional[float] = Field(default=None, ge=0, le=1)


class Response(ResponseBase):
    """Response model with metadata."""
    id: int
    assessment_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AssessmentBase(BaseModel):
    """Base assessment model."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    version: str = Field(default="1.0.0")


class AssessmentCreate(AssessmentBase):
    """Model for creating assessments."""
    questions: List[QuestionBase]


class Assessment(AssessmentBase):
    """Full assessment model."""
    id: int
    status: AssessmentStatus = AssessmentStatus.DRAFT
    created_at: datetime
    updated_at: datetime
    responses: List[Response] = []
    results: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


# SQLAlchemy ORM Models
class AssessmentORM(Base):
    """SQLAlchemy model for assessments."""
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    version = Column(String(20), default="1.0.0")
    status = Column(String(20), default=AssessmentStatus.DRAFT.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    results = Column(JSON)
    
    responses = relationship("ResponseORM", back_populates="assessment")
    
    def to_pydantic(self) -> Assessment:
        """Convert to Pydantic model."""
        return Assessment(
            id=self.id,
            title=self.title,
            description=self.description,
            version=self.version,
            status=AssessmentStatus(self.status),
            created_at=self.created_at,
            updated_at=self.updated_at,
            responses=[r.to_pydantic() for r in self.responses],
            results=self.results,
        )


class QuestionORM(Base):
    """SQLAlchemy model for questions."""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(1000), nullable=False)
    question_type = Column(String(50), nullable=False)
    options = Column(JSON)
    category = Column(String(100))
    weight = Column(Float, default=1.0)
    
    def to_pydantic(self) -> Question:
        """Convert to Pydantic model."""
        return Question(
            id=self.id,
            text=self.text,
            question_type=QuestionType(self.question_type),
            options=self.options,
            category=self.category,
            weight=self.weight,
        )


class ResponseORM(Base):
    """SQLAlchemy model for responses."""
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    answer = Column(JSON)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    assessment = relationship("AssessmentORM", back_populates="responses")
    
    def to_pydantic(self) -> Response:
        """Convert to Pydantic model."""
        return Response(
            id=self.id,
            assessment_id=self.assessment_id,
            question_id=self.question_id,
            answer=self.answer,
            confidence=self.confidence,
            created_at=self.created_at,
        )
