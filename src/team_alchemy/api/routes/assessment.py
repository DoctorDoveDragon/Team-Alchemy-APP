"""
FastAPI routes for assessments.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from sqlalchemy.orm import Session

from team_alchemy.core.assessment.models import (
    Assessment,
    AssessmentCreate,
    AssessmentORM,
    Response,
    ResponseBase,
    ResponseORM,
    QuestionORM,
    AssessmentStatus,
)
from team_alchemy.core.assessment.calculator import AssessmentCalculator
from team_alchemy.core.assessment.validator import AssessmentValidator
from team_alchemy.data.repository import get_db

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("/", response_model=Assessment, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    assessment: AssessmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new assessment."""
    # Validate assessment data
    validator = AssessmentValidator()
    validation_result = validator.validate_assessment(
        Assessment(
            id=0,
            title=assessment.title,
            description=assessment.description,
            version=assessment.version,
            status=AssessmentStatus.DRAFT,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            responses=[],
            results=None,
        ),
        assessment.questions
    )
    
    if validation_result.has_errors():
        error_messages = [f"{e.field}: {e.message}" for e in validation_result.errors]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation failed: {'; '.join(error_messages)}"
        )
    
    # Create assessment in database
    db_assessment = AssessmentORM(
        title=assessment.title,
        description=assessment.description,
        version=assessment.version,
        status=AssessmentStatus.DRAFT.value,
    )
    
    try:
        db.add(db_assessment)
        db.commit()
        db.refresh(db_assessment)
        
        # Create questions
        for question_data in assessment.questions:
            db_question = QuestionORM(
                text=question_data.text,
                question_type=question_data.question_type.value,
                options=question_data.options,
                category=question_data.category,
                weight=question_data.weight,
            )
            db.add(db_question)
        
        db.commit()
        
        return db_assessment.to_pydantic()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create assessment: {str(e)}"
        )


@router.get("/{assessment_id}", response_model=Assessment)
async def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db)
):
    """Get assessment by ID."""
    db_assessment = db.query(AssessmentORM).filter(AssessmentORM.id == assessment_id).first()
    
    if not db_assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment with id {assessment_id} not found"
        )
    
    return db_assessment.to_pydantic()


@router.post("/{assessment_id}/responses", status_code=status.HTTP_201_CREATED)
async def submit_response(
    assessment_id: int,
    response: ResponseBase,
    db: Session = Depends(get_db)
):
    """Submit a response to an assessment question."""
    # Validate assessment exists
    db_assessment = db.query(AssessmentORM).filter(AssessmentORM.id == assessment_id).first()
    if not db_assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment with id {assessment_id} not found"
        )
    
    # Validate question exists
    db_question = db.query(QuestionORM).filter(QuestionORM.id == response.question_id).first()
    if not db_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with id {response.question_id} not found"
        )
    
    # Validate response confidence
    validator = AssessmentValidator()
    confidence_errors = validator.validate_response_confidence(response.confidence)
    if confidence_errors:
        error_messages = [f"{e.field}: {e.message}" for e in confidence_errors]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation failed: {'; '.join(error_messages)}"
        )
    
    # Create response in database
    db_response = ResponseORM(
        assessment_id=assessment_id,
        question_id=response.question_id,
        answer=response.answer,
        confidence=response.confidence,
    )
    
    try:
        db.add(db_response)
        db.commit()
        db.refresh(db_response)
        
        return db_response.to_pydantic()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit response: {str(e)}"
        )


@router.post("/{assessment_id}/calculate")
async def calculate_results(
    assessment_id: int,
    db: Session = Depends(get_db)
):
    """Calculate assessment results."""
    # Get assessment
    db_assessment = db.query(AssessmentORM).filter(AssessmentORM.id == assessment_id).first()
    if not db_assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment with id {assessment_id} not found"
        )
    
    # Get all questions - for now, get all questions in the database
    # In production, you'd want to associate questions with assessments
    questions = db.query(QuestionORM).all()
    questions_pydantic = [q.to_pydantic() for q in questions]
    
    # Get assessment with responses
    assessment_pydantic = db_assessment.to_pydantic()
    
    # Calculate scores using calculator
    calculator = AssessmentCalculator()
    try:
        scores = calculator.calculate_scores(assessment_pydantic, questions_pydantic)
        
        # Update assessment with results
        db_assessment.results = scores.to_dict()
        db_assessment.status = AssessmentStatus.ANALYZED.value
        
        db.commit()
        db.refresh(db_assessment)
        
        return {
            "assessment_id": assessment_id,
            "status": "completed",
            "results": scores.to_dict()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate results: {str(e)}"
        )


@router.get("/", response_model=List[Assessment])
async def list_assessments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all assessments."""
    # Query assessments with pagination
    assessments = db.query(AssessmentORM).offset(skip).limit(limit).all()
    
    # Convert to Pydantic models
    return [assessment.to_pydantic() for assessment in assessments]
