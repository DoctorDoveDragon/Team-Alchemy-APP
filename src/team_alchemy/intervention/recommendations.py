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
                    "description": "Add members with different archetypes to improve team dynamics and problem-solving capabilities",
                    "priority": 4,
                    "expected_impact": 0.7,
                    "effort": "medium"
                },
                {
                    "type": RecommendationType.TEAM_COMPOSITION,
                    "title": "Balance Thinking Styles",
                    "description": "Recruit members with complementary cognitive approaches (analytical vs. creative, detail-oriented vs. big-picture)",
                    "priority": 3,
                    "expected_impact": 0.65,
                    "effort": "medium"
                }
            ],
            "poor_communication": [
                {
                    "type": RecommendationType.COMMUNICATION,
                    "title": "Implement Daily Standups",
                    "description": "Regular 15-minute check-ins to improve information flow and identify blockers early",
                    "priority": 5,
                    "expected_impact": 0.8,
                    "effort": "low"
                },
                {
                    "type": RecommendationType.COMMUNICATION,
                    "title": "Establish Communication Protocols",
                    "description": "Define clear channels for different types of communication (urgent, updates, discussions)",
                    "priority": 4,
                    "expected_impact": 0.75,
                    "effort": "low"
                },
                {
                    "type": RecommendationType.COMMUNICATION,
                    "title": "Implement Async Communication Tools",
                    "description": "Use collaborative documentation and async communication to accommodate different time zones and work styles",
                    "priority": 3,
                    "expected_impact": 0.7,
                    "effort": "low"
                }
            ],
            "high_conflict": [
                {
                    "type": RecommendationType.CONFLICT_RESOLUTION,
                    "title": "Facilitate Team Mediation Sessions",
                    "description": "Organize structured conflict resolution sessions with neutral facilitator",
                    "priority": 5,
                    "expected_impact": 0.85,
                    "effort": "medium"
                },
                {
                    "type": RecommendationType.CONFLICT_RESOLUTION,
                    "title": "Establish Ground Rules",
                    "description": "Create and enforce team agreements on respectful communication and collaboration",
                    "priority": 4,
                    "expected_impact": 0.7,
                    "effort": "low"
                }
            ],
            "skill_gaps": [
                {
                    "type": RecommendationType.SKILL_DEVELOPMENT,
                    "title": "Create Skill Development Plan",
                    "description": "Identify critical skill gaps and create targeted training programs",
                    "priority": 4,
                    "expected_impact": 0.75,
                    "effort": "medium"
                },
                {
                    "type": RecommendationType.SKILL_DEVELOPMENT,
                    "title": "Implement Peer Learning",
                    "description": "Establish mentoring pairs and knowledge sharing sessions",
                    "priority": 3,
                    "expected_impact": 0.65,
                    "effort": "low"
                },
                {
                    "type": RecommendationType.SKILL_DEVELOPMENT,
                    "title": "Cross-Training Program",
                    "description": "Enable team members to learn adjacent skills to increase flexibility",
                    "priority": 3,
                    "expected_impact": 0.6,
                    "effort": "medium"
                }
            ],
            "poor_processes": [
                {
                    "type": RecommendationType.PROCESS,
                    "title": "Implement Agile Ceremonies",
                    "description": "Adopt sprint planning, retrospectives, and reviews for continuous improvement",
                    "priority": 4,
                    "expected_impact": 0.8,
                    "effort": "medium"
                },
                {
                    "type": RecommendationType.PROCESS,
                    "title": "Document Standard Operating Procedures",
                    "description": "Create clear documentation for recurring tasks and workflows",
                    "priority": 3,
                    "expected_impact": 0.7,
                    "effort": "medium"
                },
                {
                    "type": RecommendationType.PROCESS,
                    "title": "Automate Repetitive Tasks",
                    "description": "Identify and automate manual processes to free up team capacity",
                    "priority": 3,
                    "expected_impact": 0.65,
                    "effort": "high"
                }
            ],
            "low_engagement": [
                {
                    "type": RecommendationType.TEAM_COMPOSITION,
                    "title": "Increase Team Autonomy",
                    "description": "Empower team members with decision-making authority in their areas of expertise",
                    "priority": 4,
                    "expected_impact": 0.75,
                    "effort": "low"
                },
                {
                    "type": RecommendationType.PROCESS,
                    "title": "Regular Recognition Program",
                    "description": "Implement peer recognition and celebrate team achievements",
                    "priority": 3,
                    "expected_impact": 0.7,
                    "effort": "low"
                }
            ],
            "burnout_risk": [
                {
                    "type": RecommendationType.PROCESS,
                    "title": "Workload Balancing",
                    "description": "Redistribute tasks and set realistic deadlines to prevent overwork",
                    "priority": 5,
                    "expected_impact": 0.85,
                    "effort": "medium"
                },
                {
                    "type": RecommendationType.TEAM_COMPOSITION,
                    "title": "Add Team Capacity",
                    "description": "Hire additional team members or contractors to reduce individual workload",
                    "priority": 4,
                    "expected_impact": 0.8,
                    "effort": "high"
                }
            ]
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
        diversity_score = team_analysis.get("diversity_score", 100)
        if diversity_score < 50:
            for template in self.recommendation_templates["low_diversity"]:
                recommendations.append(self._create_recommendation(template))
            
        # Analyze communication
        communication_score = team_analysis.get("communication_score", 100)
        if communication_score < 60:
            for template in self.recommendation_templates["poor_communication"]:
                recommendations.append(self._create_recommendation(template))
        
        # Analyze conflict levels
        conflict_score = team_analysis.get("conflict_score", 0)
        if conflict_score > 70:
            for template in self.recommendation_templates["high_conflict"]:
                recommendations.append(self._create_recommendation(template))
        
        # Analyze skill gaps
        skill_gap_score = team_analysis.get("skill_gap_score", 0)
        if skill_gap_score > 40:
            for template in self.recommendation_templates["skill_gaps"]:
                recommendations.append(self._create_recommendation(template))
        
        # Analyze process effectiveness
        process_score = team_analysis.get("process_score", 100)
        if process_score < 60:
            for template in self.recommendation_templates["poor_processes"]:
                recommendations.append(self._create_recommendation(template))
        
        # Analyze engagement
        engagement_score = team_analysis.get("engagement_score", 100)
        if engagement_score < 50:
            for template in self.recommendation_templates["low_engagement"]:
                recommendations.append(self._create_recommendation(template))
        
        # Analyze burnout risk
        burnout_risk = team_analysis.get("burnout_risk", 0)
        if burnout_risk > 60:
            for template in self.recommendation_templates["burnout_risk"]:
                recommendations.append(self._create_recommendation(template))
            
        # Sort by priority and limit
        recommendations.sort(key=lambda r: r.priority, reverse=True)
        return recommendations[:max_recommendations]
    
    def _create_recommendation(self, template: Dict[str, Any]) -> Recommendation:
        """Create a Recommendation object from a template."""
        return Recommendation(
            type=template["type"],
            title=template["title"],
            description=template["description"],
            priority=template["priority"],
            expected_impact=template["expected_impact"],
            implementation_effort=template["effort"]
        )
        
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
