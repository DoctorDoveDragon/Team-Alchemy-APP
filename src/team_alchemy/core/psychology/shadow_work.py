"""
Shadow work and integration techniques.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class ShadowAspect(Enum):
    """Types of shadow aspects."""
    REPRESSED_DESIRE = "repressed_desire"
    DENIED_TRAIT = "denied_trait"
    PROJECTED_QUALITY = "projected_quality"
    UNACKNOWLEDGED_STRENGTH = "unacknowledged_strength"
    HIDDEN_WEAKNESS = "hidden_weakness"


@dataclass
class ShadowElement:
    """Represents an element of the shadow self."""
    aspect_type: ShadowAspect
    description: str
    intensity: float  # 0-1 scale
    triggers: List[str]
    integration_status: str  # unaware, aware, integrating, integrated
    
    def is_integrated(self) -> bool:
        """Check if shadow element is integrated."""
        return self.integration_status == "integrated"
        
    def needs_work(self) -> bool:
        """Check if shadow element needs integration work."""
        return self.integration_status in ["unaware", "aware"]


@dataclass
class ShadowWorkPlan:
    """Plan for shadow integration work."""
    target_element: ShadowElement
    techniques: List[str]
    timeline: str
    expected_outcomes: List[str]
    support_needed: List[str]


class ShadowWorkAnalyzer:
    """
    Analyzes and facilitates shadow integration.
    """
    
    def __init__(self):
        self.integration_techniques = self._load_techniques()
        
    def _load_techniques(self) -> Dict[ShadowAspect, List[str]]:
        """Load shadow integration techniques."""
        return {
            ShadowAspect.REPRESSED_DESIRE: [
                "Journaling about hidden wants",
                "Safe expression exercises",
                "Desire mapping",
                "Values clarification"
            ],
            ShadowAspect.DENIED_TRAIT: [
                "Self-reflection exercises",
                "Feedback integration",
                "Trait acceptance work",
                "Reframing perspectives"
            ],
            ShadowAspect.PROJECTED_QUALITY: [
                "Projection identification",
                "Ownership exercises",
                "Mirror work",
                "Relationship pattern analysis"
            ],
            # Add more techniques
        }
        
    def identify_shadow_elements(
        self,
        assessment_data: Dict[str, any],
        behaviors: List[str],
        projections: List[str]
    ) -> List[ShadowElement]:
        """
        Identify shadow elements from assessment data.
        
        Args:
            assessment_data: Psychological assessment data
            behaviors: Observed behaviors
            projections: Identified projections
            
        Returns:
            List of identified shadow elements
        """
        elements = []
        
        # Analyze for repressed desires
        if "unfulfilled_goals" in assessment_data:
            for goal in assessment_data["unfulfilled_goals"]:
                element = ShadowElement(
                    aspect_type=ShadowAspect.REPRESSED_DESIRE,
                    description=f"Repressed desire: {goal}",
                    intensity=0.7,
                    triggers=["goal-related situations"],
                    integration_status="aware"
                )
                elements.append(element)
                
        # Analyze projections
        for projection in projections:
            element = ShadowElement(
                aspect_type=ShadowAspect.PROJECTED_QUALITY,
                description=f"Projected quality: {projection}",
                intensity=0.8,
                triggers=["similar others"],
                integration_status="unaware"
            )
            elements.append(element)
            
        # Analyze denied traits
        if "trait_discrepancies" in assessment_data:
            for trait, discrepancy in assessment_data["trait_discrepancies"].items():
                if discrepancy > 0.5:  # Significant discrepancy
                    element = ShadowElement(
                        aspect_type=ShadowAspect.DENIED_TRAIT,
                        description=f"Denied trait: {trait}",
                        intensity=discrepancy,
                        triggers=["trait-relevant situations"],
                        integration_status="aware"
                    )
                    elements.append(element)
                    
        return elements
        
    def create_integration_plan(
        self,
        element: ShadowElement
    ) -> ShadowWorkPlan:
        """
        Create an integration plan for a shadow element.
        
        Args:
            element: The shadow element to integrate
            
        Returns:
            Shadow work plan
        """
        techniques = self.integration_techniques.get(
            element.aspect_type,
            ["General shadow work", "Therapeutic support"]
        )
        
        # Determine timeline based on intensity and status
        if element.intensity > 0.7 and element.integration_status == "unaware":
            timeline = "6-12 months"
        elif element.integration_status == "aware":
            timeline = "3-6 months"
        else:
            timeline = "1-3 months"
            
        return ShadowWorkPlan(
            target_element=element,
            techniques=techniques,
            timeline=timeline,
            expected_outcomes=[
                "Increased self-awareness",
                "Reduced projection",
                "Greater wholeness",
                "Improved relationships"
            ],
            support_needed=[
                "Therapeutic guidance",
                "Safe practice space",
                "Supportive relationships"
            ]
        )
        
    def assess_integration_progress(
        self,
        elements: List[ShadowElement],
        time_period: str = "3 months"
    ) -> Dict[str, any]:
        """
        Assess progress in shadow integration.
        
        Args:
            elements: Shadow elements being worked with
            time_period: Time period of assessment
            
        Returns:
            Progress assessment
        """
        integrated_count = sum(1 for e in elements if e.is_integrated())
        in_progress_count = sum(1 for e in elements if e.integration_status == "integrating")
        needs_work_count = sum(1 for e in elements if e.needs_work())
        
        avg_intensity = sum(e.intensity for e in elements) / len(elements) if elements else 0
        
        return {
            "total_elements": len(elements),
            "integrated": integrated_count,
            "in_progress": in_progress_count,
            "needs_work": needs_work_count,
            "average_intensity": avg_intensity,
            "integration_rate": integrated_count / len(elements) if elements else 0,
            "time_period": time_period,
            "overall_status": self._determine_overall_status(elements),
        }
        
    def _determine_overall_status(self, elements: List[ShadowElement]) -> str:
        """Determine overall integration status."""
        if not elements:
            return "no_data"
            
        integrated_ratio = sum(1 for e in elements if e.is_integrated()) / len(elements)
        
        if integrated_ratio > 0.7:
            return "advanced"
        elif integrated_ratio > 0.4:
            return "progressing"
        else:
            return "beginning"


def generate_shadow_work_exercises(
    element: ShadowElement
) -> List[Dict[str, str]]:
    """
    Generate specific exercises for shadow work.
    
    Args:
        element: The shadow element to work with
        
    Returns:
        List of exercises with descriptions
    """
    exercises = []
    
    if element.aspect_type == ShadowAspect.PROJECTED_QUALITY:
        exercises.append({
            "name": "Projection Reclamation",
            "description": "Identify qualities you dislike in others and explore how they might exist in yourself",
            "duration": "15-30 minutes daily"
        })
        exercises.append({
            "name": "Three Column Technique",
            "description": "List what you project, why you reject it, and how you might own it",
            "duration": "20 minutes weekly"
        })
        
    elif element.aspect_type == ShadowAspect.REPRESSED_DESIRE:
        exercises.append({
            "name": "Desire Exploration",
            "description": "Journal freely about hidden wants without judgment",
            "duration": "20 minutes daily"
        })
        exercises.append({
            "name": "Safe Expression",
            "description": "Practice expressing desires in safe, appropriate contexts",
            "duration": "Ongoing practice"
        })
        
    return exercises


def assess_team_shadow_dynamics(
    individual_shadows: List[List[ShadowElement]]
) -> Dict[str, any]:
    """
    Analyze collective shadow dynamics in a team.
    
    Args:
        individual_shadows: List of shadow elements for each team member
        
    Returns:
        Team shadow analysis
    """
    # Flatten all elements
    all_elements = [e for shadows in individual_shadows for e in shadows]
    
    # Count aspect types
    aspect_counts = {}
    for element in all_elements:
        aspect_counts[element.aspect_type] = aspect_counts.get(element.aspect_type, 0) + 1
        
    # Identify collective patterns
    team_size = len(individual_shadows)
    collective_shadows = {
        aspect: count / team_size
        for aspect, count in aspect_counts.items()
        if count / team_size > 0.5  # More than 50% of team
    }
    
    return {
        "team_size": team_size,
        "total_shadow_elements": len(all_elements),
        "collective_patterns": collective_shadows,
        "integration_priority": _prioritize_team_integration(aspect_counts),
        "team_shadow_intensity": sum(e.intensity for e in all_elements) / len(all_elements) if all_elements else 0,
    }


def _prioritize_team_integration(aspect_counts: Dict[ShadowAspect, int]) -> List[str]:
    """Prioritize which shadow aspects the team should work on."""
    # Sort by frequency
    sorted_aspects = sorted(aspect_counts.items(), key=lambda x: x[1], reverse=True)
    return [aspect.value for aspect, _ in sorted_aspects[:3]]  # Top 3 priorities
