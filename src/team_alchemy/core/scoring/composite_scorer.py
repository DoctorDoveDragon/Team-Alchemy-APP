"""
Composite scoring system combining multiple assessment dimensions.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class ScoreDimension:
    """Represents a scoring dimension."""
    name: str
    weight: float
    score: float
    sub_scores: Optional[Dict[str, float]] = None


class CompositeScorer:
    """
    Calculates composite scores from multiple dimensions.
    """
    
    def __init__(self, dimension_weights: Optional[Dict[str, float]] = None):
        """
        Initialize composite scorer.
        
        Args:
            dimension_weights: Optional custom weights for dimensions
        """
        self.dimension_weights = dimension_weights or self._default_weights()
        
    def _default_weights(self) -> Dict[str, float]:
        """Default dimension weights."""
        return {
            "personality": 1.0,
            "skills": 1.2,
            "values": 1.0,
            "communication": 1.1,
            "leadership": 0.9,
        }
        
    def calculate_composite(
        self,
        dimension_scores: Dict[str, float]
    ) -> float:
        """
        Calculate weighted composite score.
        
        Args:
            dimension_scores: Scores for each dimension
            
        Returns:
            Composite score (0-100)
        """
        if not dimension_scores:
            return 0.0
            
        weighted_sum = 0.0
        total_weight = 0.0
        
        for dimension, score in dimension_scores.items():
            weight = self.dimension_weights.get(dimension, 1.0)
            weighted_sum += score * weight
            total_weight += weight
            
        return weighted_sum / total_weight if total_weight > 0 else 0.0
        
    def calculate_team_score(
        self,
        individual_composites: List[float],
        team_dynamics_score: float
    ) -> Dict[str, Any]:
        """
        Calculate overall team score.
        
        Args:
            individual_composites: Individual composite scores
            team_dynamics_score: Score for team dynamics
            
        Returns:
            Team scoring analysis
        """
        if not individual_composites:
            return {"team_score": 0.0, "analysis": "No data"}
            
        avg_individual = sum(individual_composites) / len(individual_composites)
        
        # Team score combines individual averages and dynamics
        team_score = (avg_individual * 0.6) + (team_dynamics_score * 0.4)
        
        # Calculate variance
        variance = sum(
            (score - avg_individual) ** 2 
            for score in individual_composites
        ) / len(individual_composites)
        
        return {
            "team_score": team_score,
            "individual_average": avg_individual,
            "team_dynamics": team_dynamics_score,
            "variance": variance,
            "cohesion": 100 - min(100, variance),  # Lower variance = higher cohesion
            "size": len(individual_composites),
        }
