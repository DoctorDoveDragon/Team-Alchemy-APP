"""
Recommendation engine for team improvements.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class RecommendationType(Enum):
    """Types of recommendations."""
    TEAM_COMPOSITION = "team_composition"
    COMMUNICATION = "communication"
    PROCESS = "process"
    SKILL_DEVELOPMENT = "skill_development"
    CONFLICT_RESOLUTION = "conflict_resolution"


@dataclass
class Recommendation:
    """A single recommendation."""
    type: RecommendationType
    title: str
    description: str
    priority: int  # 1-5, 5 being highest
    expected_impact: float  # 0-1
    implementation_effort: str  # low, medium, high
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "expected_impact": self.expected_impact,
            "implementation_effort": self.implementation_effort,
        }


class RecommendationEngine:
    """
    Generates recommendations based on team analysis.
    """
    
    def __init__(self):
        self.recommendation_templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load recommendation templates."""
        return {
            "low_diversity": [
                {
                    "type": RecommendationType.TEAM_COMPOSITION,
                    "title": "Increase Team Diversity",
                    "description": "Add members with different archetypes to improve team dynamics",
                    "priority": 4,
                    "expected_impact": 0.7,
                    "effort": "medium"
                }
            ],
            "poor_communication": [
                {
                    "type": RecommendationType.COMMUNICATION,
                    "title": "Implement Daily Standups",
                    "description": "Regular check-ins to improve information flow",
                    "priority": 5,
                    "expected_impact": 0.8,
                    "effort": "low"
                }
            ],
        }
        
    def generate_recommendations(
        self,
        team_analysis: Dict[str, Any],
        max_recommendations: int = 5
    ) -> List[Recommendation]:
        """
        Generate recommendations based on team analysis.
        
        Args:
            team_analysis: Team analysis results
            max_recommendations: Maximum number of recommendations
            
        Returns:
            List of prioritized recommendations
        """
        recommendations = []
        
        # Analyze diversity
        if team_analysis.get("diversity_score", 100) < 50:
            template = self.recommendation_templates["low_diversity"][0]
            recommendations.append(Recommendation(
                type=template["type"],
                title=template["title"],
                description=template["description"],
                priority=template["priority"],
                expected_impact=template["expected_impact"],
                implementation_effort=template["effort"]
            ))
            
        # Analyze communication
        if team_analysis.get("communication_score", 100) < 60:
            template = self.recommendation_templates["poor_communication"][0]
            recommendations.append(Recommendation(
                type=template["type"],
                title=template["title"],
                description=template["description"],
                priority=template["priority"],
                expected_impact=template["expected_impact"],
                implementation_effort=template["effort"]
            ))
            
        # Sort by priority and limit
        recommendations.sort(key=lambda r: r.priority, reverse=True)
        return recommendations[:max_recommendations]
        
    def get_quick_wins(
        self,
        recommendations: List[Recommendation]
    ) -> List[Recommendation]:
        """
        Filter recommendations for quick wins (low effort, high impact).
        
        Args:
            recommendations: List of recommendations
            
        Returns:
            Quick win recommendations
        """
        return [
            r for r in recommendations
            if r.implementation_effort == "low" and r.expected_impact > 0.6
        ]
