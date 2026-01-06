"""
Team composition optimization algorithms.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TeamMember:
    """Represents a team member for optimization."""
    id: int
    name: str
    skills: List[str]
    archetype: str
    compatibility_scores: Dict[int, float]


@dataclass
class OptimizationResult:
    """Result of team optimization."""
    team_composition: List[int]  # Member IDs
    score: float
    metrics: Dict[str, float]
    recommendations: List[str]


class TeamOptimizer:
    """
    Optimizes team composition for maximum effectiveness.
    """
    
    def __init__(self):
        self.optimization_criteria = [
            "skill_coverage",
            "archetype_diversity",
            "compatibility",
            "experience_balance"
        ]
        
    def optimize_team(
        self,
        candidates: List[TeamMember],
        team_size: int,
        objectives: Optional[List[str]] = None
    ) -> OptimizationResult:
        """
        Optimize team composition from candidates.
        
        Args:
            candidates: Available team members
            team_size: Desired team size
            objectives: Optimization objectives
            
        Returns:
            Optimization result with best team composition
        """
        # Placeholder implementation
        # Would use genetic algorithms, constraint satisfaction, etc.
        
        # Simple greedy selection for demonstration
        selected = candidates[:team_size]
        
        return OptimizationResult(
            team_composition=[m.id for m in selected],
            score=75.0,
            metrics={
                "skill_coverage": 0.8,
                "diversity": 0.7,
                "compatibility": 0.75,
            },
            recommendations=[
                "Consider adding more diverse archetypes",
                "Balance skill levels across team"
            ]
        )
        
    def calculate_team_score(
        self,
        team: List[TeamMember]
    ) -> Dict[str, float]:
        """
        Calculate comprehensive score for a team.
        
        Args:
            team: List of team members
            
        Returns:
            Dictionary of score components
        """
        # Calculate various metrics
        archetype_diversity = len(set(m.archetype for m in team)) / len(team)
        
        # Average compatibility
        avg_compatibility = 0.0
        count = 0
        for i, member in enumerate(team):
            for j in range(i + 1, len(team)):
                other_id = team[j].id
                if other_id in member.compatibility_scores:
                    avg_compatibility += member.compatibility_scores[other_id]
                    count += 1
                    
        if count > 0:
            avg_compatibility /= count
            
        return {
            "diversity": archetype_diversity * 100,
            "compatibility": avg_compatibility,
            "size": len(team),
            "overall": (archetype_diversity * 50) + (avg_compatibility * 0.5),
        }
        
    def suggest_additions(
        self,
        current_team: List[TeamMember],
        candidates: List[TeamMember],
        max_suggestions: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Suggest candidates to add to team.
        
        Args:
            current_team: Current team members
            candidates: Available candidates
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of suggested additions with rationale
        """
        suggestions = []
        
        for candidate in candidates[:max_suggestions]:
            # Calculate impact of adding this candidate
            impact_score = 0.8  # Placeholder
            
            suggestions.append({
                "candidate_id": candidate.id,
                "name": candidate.name,
                "impact_score": impact_score,
                "rationale": f"Adds missing archetype: {candidate.archetype}",
            })
            
        return suggestions
