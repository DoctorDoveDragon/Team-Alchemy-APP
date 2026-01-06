"""
Assessment score calculation and analysis.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from team_alchemy.core.assessment.models import Assessment, Response, Question
from team_alchemy.core.archetypes.traits import TraitProfile


@dataclass
class AssessmentScore:
    """Represents calculated scores from an assessment."""
    total_score: float
    category_scores: Dict[str, float]
    trait_profile: TraitProfile
    completion_percentage: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_score": self.total_score,
            "category_scores": self.category_scores,
            "trait_scores": self.trait_profile.get_all_scores(),
            "completion_percentage": self.completion_percentage,
        }


class AssessmentCalculator:
    """
    Calculates scores and analyzes assessment results.
    """
    
    def __init__(self):
        self.category_weights: Dict[str, float] = {}
        self._initialize_weights()
        
    def _initialize_weights(self):
        """Initialize category weighting scheme."""
        self.category_weights = {
            "cognitive": 1.0,
            "emotional": 1.0,
            "behavioral": 1.0,
            "interpersonal": 1.2,  # Slightly higher weight
            "motivational": 1.0,
        }
        
    def calculate_scores(
        self,
        assessment: Assessment,
        questions: List[Question]
    ) -> AssessmentScore:
        """
        Calculate comprehensive scores from assessment responses.
        
        Args:
            assessment: The completed assessment
            questions: List of questions in the assessment
            
        Returns:
            AssessmentScore with all calculated metrics
        """
        if not assessment.responses:
            return self._empty_score()
            
        # Calculate category scores
        category_scores = self._calculate_category_scores(
            assessment.responses,
            questions
        )
        
        # Calculate total score
        total_score = self._calculate_total_score(category_scores)
        
        # Build trait profile
        trait_profile = self._build_trait_profile(assessment.responses, questions)
        
        # Calculate completion percentage
        completion = self._calculate_completion(assessment, questions)
        
        return AssessmentScore(
            total_score=total_score,
            category_scores=category_scores,
            trait_profile=trait_profile,
            completion_percentage=completion,
        )
        
    def _calculate_category_scores(
        self,
        responses: List[Response],
        questions: List[Question]
    ) -> Dict[str, float]:
        """Calculate scores by category."""
        category_totals: Dict[str, List[float]] = {}
        
        # Create question lookup
        question_map = {q.id: q for q in questions}
        
        for response in responses:
            question = question_map.get(response.question_id)
            if not question:
                continue
                
            category = question.category
            score = self._score_response(response, question)
            
            if category not in category_totals:
                category_totals[category] = []
            category_totals[category].append(score)
            
        # Average scores by category
        category_scores = {
            cat: sum(scores) / len(scores) if scores else 0.0
            for cat, scores in category_totals.items()
        }
        
        return category_scores
        
    def _calculate_total_score(self, category_scores: Dict[str, float]) -> float:
        """Calculate weighted total score."""
        if not category_scores:
            return 0.0
            
        weighted_sum = sum(
            score * self.category_weights.get(cat.lower(), 1.0)
            for cat, score in category_scores.items()
        )
        
        total_weight = sum(
            self.category_weights.get(cat.lower(), 1.0)
            for cat in category_scores.keys()
        )
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
        
    def _build_trait_profile(
        self,
        responses: List[Response],
        questions: List[Question]
    ) -> TraitProfile:
        """Build a trait profile from responses."""
        profile = TraitProfile()
        
        question_map = {q.id: q for q in questions}
        
        for response in responses:
            question = question_map.get(response.question_id)
            if not question:
                continue
                
            # Map response to trait score
            score = self._score_response(response, question)
            trait_name = question.category.title()
            profile.add_score(trait_name, score)
            
        return profile
        
    def _score_response(self, response: Response, question: Question) -> float:
        """Score an individual response."""
        # Simple scoring logic - would be more sophisticated in production
        if isinstance(response.answer, (int, float)):
            # Normalize to 0-100 scale
            return float(response.answer)
        elif isinstance(response.answer, str):
            # For text responses, use confidence or default
            return response.confidence * 100 if response.confidence else 50.0
        else:
            return 50.0  # Default neutral score
            
    def _calculate_completion(
        self,
        assessment: Assessment,
        questions: List[Question]
    ) -> float:
        """Calculate assessment completion percentage."""
        if not questions:
            return 0.0
            
        answered = len(assessment.responses)
        total = len(questions)
        
        return (answered / total) * 100 if total > 0 else 0.0
        
    def _empty_score(self) -> AssessmentScore:
        """Return an empty score object."""
        return AssessmentScore(
            total_score=0.0,
            category_scores={},
            trait_profile=TraitProfile(),
            completion_percentage=0.0,
        )


def calculate_team_aggregate_score(individual_scores: List[AssessmentScore]) -> Dict[str, Any]:
    """
    Calculate aggregate scores for a team.
    
    Args:
        individual_scores: List of individual assessment scores
        
    Returns:
        Dictionary with team aggregate metrics
    """
    if not individual_scores:
        return {
            "team_average": 0.0,
            "team_variance": 0.0,
            "category_averages": {},
        }
        
    # Calculate averages
    team_average = sum(s.total_score for s in individual_scores) / len(individual_scores)
    
    # Calculate variance
    variance = sum((s.total_score - team_average) ** 2 for s in individual_scores) / len(individual_scores)
    
    # Category averages
    all_categories = set()
    for score in individual_scores:
        all_categories.update(score.category_scores.keys())
        
    category_averages = {}
    for cat in all_categories:
        cat_scores = [s.category_scores.get(cat, 0) for s in individual_scores]
        category_averages[cat] = sum(cat_scores) / len(cat_scores)
        
    return {
        "team_average": team_average,
        "team_variance": variance,
        "category_averages": category_averages,
        "team_size": len(individual_scores),
    }
