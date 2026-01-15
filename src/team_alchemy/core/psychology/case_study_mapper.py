"""
Case study mapping for psychological analysis.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CaseStudy:
    """Represents a psychological case study."""
    id: str
    title: str
    subject_profile: Dict[str, any]
    interventions: List[str]
    outcomes: Dict[str, any]
    psychological_framework: str
    created_at: datetime
    
    def get_summary(self) -> str:
        """Get a brief summary of the case study."""
        return f"{self.title}: {self.psychological_framework} approach"


class CaseStudyMapper:
    """
    Maps current assessments to relevant historical case studies.
    """
    
    def __init__(self):
        self.case_database: Dict[str, CaseStudy] = {}
        self._load_case_studies()
        
    def _load_case_studies(self):
        """Load case study database."""
        # Comprehensive case study database
        cases = [
            CaseStudy(
                id="CS001",
                title="Team Transformation through Archetype Awareness",
                subject_profile={
                    "team_size": 8,
                    "primary_issues": ["communication", "conflict"],
                    "archetypes": ["leader", "harmonizer", "analyst"]
                },
                interventions=[
                    "Archetype identification",
                    "Team composition analysis",
                    "Communication workshops"
                ],
                outcomes={
                    "effectiveness_increase": 0.35,
                    "satisfaction_increase": 0.40,
                    "conflict_reduction": 0.50
                },
                psychological_framework="Jungian",
                created_at=datetime(2023, 1, 1)
            ),
            CaseStudy(
                id="CS002",
                title="Defense Mechanism Integration in High-Stress Environment",
                subject_profile={
                    "team_size": 5,
                    "primary_issues": ["stress", "burnout"],
                    "defense_mechanisms": ["denial", "rationalization"]
                },
                interventions=[
                    "Defense mechanism awareness training",
                    "Stress management workshops",
                    "Individual counseling"
                ],
                outcomes={
                    "stress_reduction": 0.45,
                    "burnout_reduction": 0.38,
                    "coping_improvement": 0.52
                },
                psychological_framework="Freudian",
                created_at=datetime(2023, 2, 15)
            ),
            CaseStudy(
                id="CS003",
                title="Shadow Work in Leadership Development",
                subject_profile={
                    "team_size": 3,
                    "primary_issues": ["leadership", "authenticity"],
                    "archetypes": ["leader", "shadow"]
                },
                interventions=[
                    "Shadow integration exercises",
                    "Leadership coaching",
                    "Reflective journaling"
                ],
                outcomes={
                    "leadership_effectiveness": 0.48,
                    "authenticity_increase": 0.55,
                    "team_trust": 0.42
                },
                psychological_framework="Jungian",
                created_at=datetime(2023, 3, 20)
            ),
            CaseStudy(
                id="CS004",
                title="MBTI-Based Team Composition Optimization",
                subject_profile={
                    "team_size": 10,
                    "primary_issues": ["collaboration", "efficiency"],
                    "mbti_types": ["INTJ", "ENFP", "ISTJ", "ESFJ"]
                },
                interventions=[
                    "MBTI assessment and profiling",
                    "Function stack analysis",
                    "Role alignment based on cognitive functions"
                ],
                outcomes={
                    "efficiency_increase": 0.40,
                    "collaboration_improvement": 0.47,
                    "satisfaction_increase": 0.43
                },
                psychological_framework="Jungian",
                created_at=datetime(2023, 4, 10)
            ),
            CaseStudy(
                id="CS005",
                title="Conflict Resolution through Archetype Understanding",
                subject_profile={
                    "team_size": 6,
                    "primary_issues": ["conflict", "miscommunication"],
                    "archetypes": ["challenger", "harmonizer", "analyst"]
                },
                interventions=[
                    "Archetype-based communication training",
                    "Conflict mediation sessions",
                    "Team building exercises"
                ],
                outcomes={
                    "conflict_reduction": 0.58,
                    "communication_improvement": 0.51,
                    "team_cohesion": 0.45
                },
                psychological_framework="Jungian",
                created_at=datetime(2023, 5, 5)
            ),
            CaseStudy(
                id="CS006",
                title="Ego Strength Development in New Managers",
                subject_profile={
                    "team_size": 4,
                    "primary_issues": ["decision_making", "confidence"],
                    "experience_level": "new_managers"
                },
                interventions=[
                    "Ego strength assessment",
                    "Decision-making frameworks",
                    "Leadership mentoring"
                ],
                outcomes={
                    "decision_quality": 0.44,
                    "confidence_increase": 0.50,
                    "team_performance": 0.38
                },
                psychological_framework="Freudian",
                created_at=datetime(2023, 6, 18)
            ),
        ]
        
        for case in cases:
            self.case_database[case.id] = case
        
    def find_similar_cases(
        self,
        profile: Dict[str, any],
        limit: int = 5
    ) -> List[CaseStudy]:
        """
        Find case studies similar to a given profile.
        
        Args:
            profile: Current assessment profile
            limit: Maximum number of cases to return
            
        Returns:
            List of similar case studies
        """
        scored_cases = []
        
        for case in self.case_database.values():
            similarity = self._calculate_similarity(profile, case.subject_profile)
            scored_cases.append((similarity, case))
            
        # Sort by similarity and return top cases
        scored_cases.sort(key=lambda x: x[0], reverse=True)
        return [case for _, case in scored_cases[:limit]]
        
    def _calculate_similarity(
        self,
        profile1: Dict[str, any],
        profile2: Dict[str, any]
    ) -> float:
        """
        Calculate similarity between two profiles.
        
        Args:
            profile1: First profile
            profile2: Second profile
            
        Returns:
            Similarity score (0-1)
        """
        # Simple similarity calculation
        # Would be more sophisticated with actual data
        common_keys = set(profile1.keys()) & set(profile2.keys())
        
        if not common_keys:
            return 0.0
            
        matches = sum(
            1 for key in common_keys
            if profile1.get(key) == profile2.get(key)
        )
        
        return matches / len(common_keys)
        
    def extract_lessons(self, cases: List[CaseStudy]) -> List[Dict[str, any]]:
        """
        Extract key lessons from case studies.
        
        Args:
            cases: List of case studies
            
        Returns:
            List of lessons learned
        """
        lessons = []
        
        for case in cases:
            lesson = {
                "case_id": case.id,
                "title": case.title,
                "key_interventions": case.interventions,
                "outcomes": case.outcomes,
                "applicability": "high"  # Would be calculated
            }
            lessons.append(lesson)
            
        return lessons
        
    def recommend_interventions(
        self,
        current_profile: Dict[str, any]
    ) -> List[str]:
        """
        Recommend interventions based on similar cases.
        
        Args:
            current_profile: Current assessment profile
            
        Returns:
            List of recommended interventions
        """
        similar_cases = self.find_similar_cases(current_profile, limit=3)
        
        # Collect all interventions from similar cases
        all_interventions = []
        for case in similar_cases:
            all_interventions.extend(case.interventions)
            
        # Return unique interventions
        return list(set(all_interventions))
        
    def add_case_study(self, case: CaseStudy):
        """Add a new case study to the database."""
        self.case_database[case.id] = case
        
    def get_case_by_id(self, case_id: str) -> Optional[CaseStudy]:
        """Retrieve a case study by ID."""
        return self.case_database.get(case_id)
        
    def get_all_frameworks(self) -> List[str]:
        """Get list of all psychological frameworks used in cases."""
        frameworks = set(case.psychological_framework for case in self.case_database.values())
        return sorted(list(frameworks))


def generate_case_report(
    case: CaseStudy,
    include_details: bool = True
) -> Dict[str, any]:
    """
    Generate a formatted case report.
    
    Args:
        case: The case study
        include_details: Whether to include full details
        
    Returns:
        Formatted case report
    """
    report = {
        "id": case.id,
        "title": case.title,
        "framework": case.psychological_framework,
        "date": case.created_at.isoformat(),
    }
    
    if include_details:
        report.update({
            "profile": case.subject_profile,
            "interventions": case.interventions,
            "outcomes": case.outcomes,
        })
        
    return report
