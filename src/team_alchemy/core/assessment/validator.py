"""
Validation logic for assessments and responses.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from team_alchemy.core.assessment.models import (
    Assessment,
    Question,
    Response,
    QuestionType,
    AssessmentStatus,
)


@dataclass
class ValidationError:
    """Represents a validation error."""
    field: str
    message: str
    severity: str = "error"  # error, warning, info


@dataclass
class ValidationResult:
    """Result of validation."""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
        
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0


class AssessmentValidator:
    """
    Validates assessments, questions, and responses.
    """
    
    def __init__(self):
        self.min_questions = 5
        self.max_questions = 200
        self.min_completion_rate = 0.8  # 80% completion required
        
    def validate_assessment(self, assessment: Assessment, questions: List[Question]) -> ValidationResult:
        """
        Validate a complete assessment.
        
        Args:
            assessment: The assessment to validate
            questions: Questions in the assessment
            
        Returns:
            ValidationResult with any errors or warnings
        """
        errors = []
        warnings = []
        
        # Validate basic fields
        if not assessment.title or len(assessment.title.strip()) == 0:
            errors.append(ValidationError(
                field="title",
                message="Assessment title is required"
            ))
            
        # Validate question count
        if len(questions) < self.min_questions:
            errors.append(ValidationError(
                field="questions",
                message=f"Assessment must have at least {self.min_questions} questions"
            ))
        elif len(questions) > self.max_questions:
            errors.append(ValidationError(
                field="questions",
                message=f"Assessment cannot have more than {self.max_questions} questions"
            ))
            
        # Validate questions
        question_errors = self._validate_questions(questions)
        errors.extend(question_errors)
        
        # Validate responses if assessment is completed
        if assessment.status == AssessmentStatus.COMPLETED:
            response_errors, response_warnings = self._validate_responses(
                assessment.responses,
                questions
            )
            errors.extend(response_errors)
            warnings.extend(response_warnings)
            
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
        
    def _validate_questions(self, questions: List[Question]) -> List[ValidationError]:
        """Validate a list of questions."""
        errors = []
        
        question_ids = set()
        for i, question in enumerate(questions):
            # Check for duplicate IDs
            if question.id in question_ids:
                errors.append(ValidationError(
                    field=f"questions[{i}].id",
                    message=f"Duplicate question ID: {question.id}"
                ))
            question_ids.add(question.id)
            
            # Validate question text
            if not question.text or len(question.text.strip()) == 0:
                errors.append(ValidationError(
                    field=f"questions[{i}].text",
                    message="Question text is required"
                ))
                
            # Validate multiple choice questions
            if question.question_type == QuestionType.MULTIPLE_CHOICE:
                if not question.options or len(question.options) < 2:
                    errors.append(ValidationError(
                        field=f"questions[{i}].options",
                        message="Multiple choice questions must have at least 2 options"
                    ))
                    
            # Validate weight
            if question.weight < 0 or question.weight > 1:
                errors.append(ValidationError(
                    field=f"questions[{i}].weight",
                    message="Question weight must be between 0 and 1"
                ))
                
        return errors
        
    def _validate_responses(
        self,
        responses: List[Response],
        questions: List[Question]
    ) -> tuple[List[ValidationError], List[ValidationError]]:
        """Validate responses against questions."""
        errors = []
        warnings = []
        
        question_map = {q.id: q for q in questions}
        
        # Check completion rate
        completion_rate = len(responses) / len(questions) if questions else 0
        if completion_rate < self.min_completion_rate:
            warnings.append(ValidationError(
                field="responses",
                message=f"Only {completion_rate*100:.1f}% complete (minimum {self.min_completion_rate*100}% recommended)",
                severity="warning"
            ))
            
        # Validate each response
        answered_questions = set()
        for i, response in enumerate(responses):
            # Check if question exists
            question = question_map.get(response.question_id)
            if not question:
                errors.append(ValidationError(
                    field=f"responses[{i}].question_id",
                    message=f"Question {response.question_id} not found in assessment"
                ))
                continue
                
            # Check for duplicate responses
            if response.question_id in answered_questions:
                errors.append(ValidationError(
                    field=f"responses[{i}].question_id",
                    message=f"Duplicate response for question {response.question_id}"
                ))
            answered_questions.add(response.question_id)
            
            # Validate response based on question type
            answer_errors = self._validate_answer(response.answer, question)
            for error in answer_errors:
                error.field = f"responses[{i}].answer"
            errors.extend(answer_errors)
            
        return errors, warnings
        
    def _validate_answer(self, answer: Any, question: Question) -> List[ValidationError]:
        """Validate an answer against its question type."""
        errors = []
        
        if answer is None:
            errors.append(ValidationError(
                field="answer",
                message="Answer cannot be null"
            ))
            return errors
            
        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            if isinstance(answer, str):
                if question.options and answer not in question.options:
                    errors.append(ValidationError(
                        field="answer",
                        message=f"Answer '{answer}' not in valid options"
                    ))
            else:
                errors.append(ValidationError(
                    field="answer",
                    message="Multiple choice answer must be a string"
                ))
                
        elif question.question_type == QuestionType.SCALE:
            if not isinstance(answer, (int, float)):
                errors.append(ValidationError(
                    field="answer",
                    message="Scale answer must be a number"
                ))
            elif answer < 0 or answer > 100:
                errors.append(ValidationError(
                    field="answer",
                    message="Scale answer must be between 0 and 100"
                ))
                
        elif question.question_type == QuestionType.TEXT:
            if not isinstance(answer, str):
                errors.append(ValidationError(
                    field="answer",
                    message="Text answer must be a string"
                ))
                
        return errors
        
    def validate_response_confidence(self, confidence: Optional[float]) -> List[ValidationError]:
        """Validate response confidence score."""
        errors = []
        
        if confidence is not None:
            if confidence < 0 or confidence > 1:
                errors.append(ValidationError(
                    field="confidence",
                    message="Confidence must be between 0 and 1"
                ))
                
        return errors
